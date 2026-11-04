#!/usr/bin/env python3
"""Run a Sloyd asset pack from plan.json into a resumable manifest.json.

    python3 run_pack.py art/dungeon/plan.json --estimate     # price it, spend nothing
    python3 run_pack.py art/dungeon/plan.json --yes          # run it
    python3 run_pack.py art/dungeon/plan.json --yes          # re-run = resume

What it does per asset, in order:
    concept  generate_image            (route "concept")
    model    generate_3d_from_text     (route "text")
             generate_3d_from_image    (routes "concept", "image")
             generate_3d_from_images   (route "views")
    variant  retexture_model           (one per entry in "variants")
    split    split_model_into_parts    (if "split" is set)

Guarantees:
  * never more than --max-concurrent (default 5, the API limit) jobs in flight;
    429 means "wait for a slot", not failure
  * every jobId is written to manifest.json the moment it exists, so a crash or
    Ctrl-C never loses a paid result; re-running resumes polling instead of
    paying again
  * a 402 stops new submissions, lets running jobs finish, and exits with code 2
  * a failed job (credits are refunded) is retried once, then marked failed

Standard library only. Uses ../../sloyd-api/scripts/sloyd.py.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import copy
import datetime as dt
import json
import os
import sys
import threading
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sloyd-api", "scripts"))
try:
    import sloyd  # noqa: E402
except ImportError:  # pragma: no cover
    sys.exit("Cannot find sloyd-api/scripts/sloyd.py. Keep the skills folder layout intact.")

SCHEMA = "sloyd-game-art/manifest@1"
ROUTES = ("text", "concept", "image", "views")
DONE = ("success", "completed")
FAILED = ("error", "failed")
MAX_ATTEMPTS = 2
MODEL_TOOLS = ("generate_3d_from_text", "generate_3d_from_image", "generate_3d_from_images",
               "retexture_model", "split_model_into_parts")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------- planning


def merged(asset: dict, defaults: dict, budgets: dict) -> dict:
    a = copy.deepcopy(defaults)
    a.update(asset)
    if "targetFaceCount" not in asset and a.get("size") in budgets:
        a["targetFaceCount"] = budgets[a["size"]]
    a.setdefault("route", "concept")
    if a["route"] not in ROUTES:
        raise ValueError(f"{a.get('id')}: route must be one of {ROUTES}")
    return a


def join(*parts: str) -> str:
    return ", ".join(p.strip().strip(",") for p in parts if p and p.strip())


def stages_for(a: dict) -> list[tuple[str, str, dict]]:
    """[(stage_key, tool, args)] in execution order. Args may hold
    placeholders {"$from": "concept"} resolved to an earlier stage's jobId."""
    out: list[tuple[str, str, dict]] = []
    tex = a.get("textureResolution")
    common3d = {k: a[k] for k in ("topology", "targetFaceCount", "textureResolution") if a.get(k) not in (None, "")}
    route = a["route"]
    if route == "concept":
        args = {"prompt": join(a["subject"], a.get("conceptSuffix", "")), "aspectRatio": a.get("aspectRatio", "1:1")}
        if a.get("genStyleId"):
            args["genStyleId"] = a["genStyleId"]
        if a.get("tPose"):
            args["tPose"] = True
        out.append(("concept", "generate_image", args))
        out.append(("model", "generate_3d_from_image", {**common3d, "imageJobId": {"$from": "concept"}}))
    elif route == "text":
        args = {"prompt": join(a["subject"], a.get("modelSuffix", "")), **common3d}
        if a.get("genStyleId"):
            args["genStyleId"] = a["genStyleId"]
        if a.get("tPose"):
            args["tPose"] = True
        out.append(("model", "generate_3d_from_text", args))
    elif route == "image":
        if not a.get("image"):
            raise ValueError(f"{a['id']}: route 'image' needs an 'image' https URL")
        out.append(("upload", "upload_image", {"file": {"url": a["image"]}}))
        out.append(("model", "generate_3d_from_image", {**common3d, "imageJobId": {"$from": "upload"}}))
    elif route == "views":
        views = a.get("views") or {}
        if "front" not in views or not any(k in views for k in ("left", "back", "right")):
            raise ValueError(f"{a['id']}: route 'views' needs views.front and one of left/back/right")
        args = {f"{k}Image": {"url": v} for k, v in views.items() if k in ("front", "left", "back", "right")}
        args["EnablePBR"] = "false" if tex == "none" else "true"
        if a.get("targetFaceCount"):
            args["FaceCount"] = str(int(a["targetFaceCount"]))
        out.append(("model", "generate_3d_from_images", args))
    for v in a.get("variants") or []:
        args = {"jobId": {"$from": "model"}, "prompt": join(v["prompt"], a.get("retextureSuffix", ""))}
        if tex and tex != "none":
            args["textureResolution"] = tex
        out.append((f"variant:{v['name']}", "retexture_model", args))
    if a.get("split"):
        s = a["split"] if isinstance(a["split"], dict) else {}
        args = {"jobId": {"$from": "model"}, "method": s.get("method", "partition")}
        if args["method"] == "partition":
            args["numberOfParts"] = int(s.get("numberOfParts", 6))
            args["attachmentPoints"] = bool(s.get("attachmentPoints", False))
        out.append(("split", "split_model_into_parts", args))
    return out


def cost_of(tool: str, args: dict) -> int:
    clean = {k: v for k, v in args.items() if not isinstance(v, dict) or "$from" not in v}
    return sloyd.estimate(tool, clean)


# ---------------------------------------------------------------- manifest


class Manifest:
    def __init__(self, path: str, plan: dict):
        self.path = path
        self.lock = threading.Lock()
        self.data = {}
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                self.data = json.load(fh)
        old = {a["id"]: a for a in self.data.get("assets", [])}
        d = plan.get("defaults", {})
        self.data.update({
            "schema": SCHEMA,
            "pack": plan["pack"],
            "title": plan.get("title", plan["pack"]),
            "styleBible": plan.get("styleBible", "style-bible.md"),
            "genStyleId": d.get("genStyleId"),
            "textureResolution": d.get("textureResolution"),
            "topology": d.get("topology"),
            "createdAt": self.data.get("createdAt", now()),
        })
        assets = []
        for raw in plan["assets"]:
            a = merged(raw, d, plan.get("budgets", {}))
            prev = old.get(a["id"], {})
            entry = {
                **{k: v for k, v in prev.items() if k not in ("jobs", "status")},  # keep notes like rerolls, export
                "id": a["id"],
                "name": a.get("name", a["id"]),
                "category": a.get("category", ""),
                "size": a.get("size", ""),
                "heightM": a.get("heightM"),
                "route": a["route"],
                "subject": a.get("subject", ""),
                "targetFaceCount": a.get("targetFaceCount"),
                "jobs": prev.get("jobs", {}),
            }
            for key, tool, args in stages_for(a):
                job = entry["jobs"].get(key, {})
                job.update({"tool": tool, "args": args, "estimate": cost_of(tool, args)})
                job.setdefault("status", "planned")
                job.setdefault("attempts", 0)
                entry["jobs"][key] = job
            assets.append(entry)
        self.data["assets"] = assets
        self.save()

    def save(self) -> None:
        with self.lock:
            self._refresh_totals()
            tmp = self.path + ".tmp"
            os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
            os.replace(tmp, self.path)

    def _refresh_totals(self) -> None:
        assets = self.data.get("assets", [])
        spent = remaining = 0
        n_done = n_failed = 0
        for a in assets:
            jobs = a["jobs"].values()
            for j in jobs:
                if j["status"] in DONE:
                    spent += j.get("estimate", 0)
                elif j["status"] not in FAILED:
                    remaining += j.get("estimate", 0)
            if jobs and all(j["status"] in DONE for j in jobs):
                a["status"] = "done"
                n_done += 1
            elif any(j["status"] in FAILED and j.get("attempts", 0) >= MAX_ATTEMPTS for j in jobs):
                a["status"] = "failed"
                n_failed += 1
            elif any(j["status"] in DONE for j in jobs):
                a["status"] = "partial"
            else:
                a["status"] = "planned"
        self.data["totals"] = {
            "assets": len(assets),
            "done": n_done,
            "failed": n_failed,
            "creditsSpentEstimate": spent,
            "creditsRemainingEstimate": remaining,
        }
        self.data["updatedAt"] = now()


# ---------------------------------------------------------------- runner


class Runner:
    def __init__(self, api: "sloyd.Sloyd", man: Manifest, out_dir: str, download: bool):
        self.api = api
        self.man = man
        self.out = out_dir
        self.download = download
        self.stop = threading.Event()
        self.stop_reason = ""

    def resolve(self, a: dict, args: dict) -> dict:
        res = {}
        for k, v in args.items():
            if isinstance(v, dict) and "$from" in v:
                src = a["jobs"].get(v["$from"], {})
                if src.get("status") not in DONE:
                    raise RuntimeError(f"{a['id']}: stage {v['$from']} not finished")
                res[k] = src["jobId"]
            else:
                res[k] = v
        return res

    def local_path(self, a: dict, key: str, url: str) -> str:
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".bin"
        if key == "concept":
            return os.path.join("concepts", a["id"] + ext)
        if key == "upload":
            return os.path.join("concepts", a["id"] + "__source" + ext)
        if key == "model":
            return os.path.join("models", a["id"] + ext)
        if key.startswith("variant:"):
            return os.path.join("variants", f"{a['id']}__{key.split(':', 1)[1]}{ext}")
        if key == "split":
            return os.path.join("parts", a["id"] + "__parts" + ext)
        return os.path.join("misc", f"{a['id']}__{key}{ext}")

    def finish(self, a: dict, key: str, job: dict, result: dict) -> None:
        outs = result.get("outputs") or {}
        url = outs.get("glbUrl") or outs.get("imageUrl") or outs.get("panoramaUrl") or result.get("imageUrl")
        if not url and job["tool"] in MODEL_TOOLS:
            # Documented public path for every finished model job.
            url = f"https://storage.googleapis.com/ai-services-quality/jobs/{job['jobId']}.glb"
        job["url"] = url
        job["status"] = "success"
        job["finishedAt"] = now()
        if url and self.download:
            rel = self.local_path(a, key, url)
            sloyd.download(url, os.path.join(self.out, rel))
            job["file"] = rel

    def run_stage(self, a: dict, key: str) -> bool:
        job = a["jobs"][key]
        while True:
            if job["status"] in DONE:
                if self.download and job.get("url") and not (job.get("file") and os.path.isfile(os.path.join(self.out, job["file"]))):
                    rel = self.local_path(a, key, job["url"])
                    sloyd.download(job["url"], os.path.join(self.out, rel))
                    job["file"] = rel
                    self.man.save()
                return True
            if job.get("jobId") and job["status"] in ("pending", "running", "submitted"):
                res = self.api.wait(job["jobId"])
                if sloyd.job_ok(res):
                    self.finish(a, key, job, res)
                    self.man.save()
                    log(f"done    {a['id']:<28} {key:<16} {job.get('url', '')}")
                    return True
                job["status"] = "error"
                job["error"] = res.get("errorMessage") or res.get("status")
                self.man.save()
                log(f"failed  {a['id']:<28} {key:<16} {job['error']}")
                continue
            if job["status"] in FAILED and job.get("attempts", 0) >= MAX_ATTEMPTS:
                return False
            if self.stop.is_set():
                return False
            args = self.resolve(a, job["args"])
            try:
                if job["tool"] == "upload_image":
                    res = self.api.tool("upload_image", args)
                    job.update({"jobId": res["jobId"], "attempts": job.get("attempts", 0) + 1,
                                "submittedAt": now()})
                    self.finish(a, key, job, res)
                    self.man.save()
                    return True
                job_id = self.api.start(job["tool"], args)
            except sloyd.CreditsError as err:
                b = err.body
                self.stop_reason = f"402 insufficient credits (need {b.get('required')}, have {b.get('available')})"
                self.stop.set()
                log(f"STOP    {self.stop_reason}. Running jobs will finish; re-run after topping up.")
                return False
            except sloyd.SloydError as err:
                job["status"] = "error"
                job["attempts"] = job.get("attempts", 0) + 1
                job["error"] = str(err)[:300]
                self.man.save()
                log(f"failed  {a['id']:<28} {key:<16} {job['error']}")
                continue
            job.update({"jobId": job_id, "status": "running", "attempts": job.get("attempts", 0) + 1,
                        "submittedAt": now(), "error": None})
            self.man.save()
            log(f"started {a['id']:<28} {key:<16} {job_id}")

    def run_asset(self, a: dict) -> None:
        for key in list(a["jobs"].keys()):
            if self.stop.is_set() and not a["jobs"][key].get("jobId"):
                return
            try:
                ok = self.run_stage(a, key)
            except Exception as err:  # keep the batch alive
                a["jobs"][key]["status"] = "error"
                a["jobs"][key]["error"] = f"{type(err).__name__}: {err}"[:300]
                a["jobs"][key]["attempts"] = MAX_ATTEMPTS
                self.man.save()
                log(f"failed  {a['id']:<28} {key:<16} {a['jobs'][key]['error']}")
                ok = False
            if not ok and key in ("concept", "upload", "model"):
                return  # later stages depend on these


def print_estimate(man: Manifest, balance: int | None, only: set[str] | None = None) -> int:
    by_tool: dict[str, list[int]] = {}
    for a in man.data["assets"]:
        if only and a["id"] not in only:
            continue
        for j in a["jobs"].values():
            if j["status"] in DONE:
                continue
            by_tool.setdefault(j["tool"], []).append(j["estimate"])
    total = sum(sum(v) for v in by_tool.values())
    print("\nRemaining work")
    for tool, costs in sorted(by_tool.items()):
        print(f"  {tool:<26} x{len(costs):<4} {sum(costs):>6} credits")
    print(f"  {'total':<32} {total:>6} credits  (~${total / 75:.2f})")
    reroll = round(total * 0.15)
    print(f"  suggested reroll reserve (15%)   {reroll:>6} credits")
    if balance is not None:
        print(f"  balance                          {balance:>6} credits")
        print(f"  after run (est.)                 {balance - total:>6} credits")
    print()
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--out", help="output folder (default: the plan's folder)")
    ap.add_argument("--estimate", action="store_true", help="price the remaining work and exit")
    ap.add_argument("--yes", action="store_true", help="confirm spending credits")
    ap.add_argument("--max-concurrent", type=int, default=None, help="in-flight job cap (1-5)")
    ap.add_argument("--only", help="comma-separated asset ids to run")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--allow-partial", action="store_true", help="run even if the balance covers only part")
    args = ap.parse_args()

    with open(args.plan, encoding="utf-8") as fh:
        plan = json.load(fh)
    out = os.path.abspath(args.out or os.path.dirname(os.path.abspath(args.plan)))
    ids = [a["id"] for a in plan["assets"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        sys.exit(f"duplicate asset ids in plan: {sorted(dupes)}")
    man = Manifest(os.path.join(out, "manifest.json"), plan)

    try:
        api = sloyd.Sloyd()
        balance = api.balance()
    except sloyd.SloydError as err:
        print(err, file=sys.stderr)
        return 1
    only = set(args.only.split(",")) if args.only else None
    total = print_estimate(man, balance, only)
    if args.estimate:
        return 0
    if total == 0:
        log("Nothing left to generate; checking downloads.")
    if total > balance and not args.allow_partial:
        print(f"Balance {balance} does not cover {total}. Top up at {sloyd.DASHBOARD} "
              "or pass --allow-partial to run what fits (the run stops cleanly at the first 402).")
        return 2
    if not args.yes:
        print("Re-run with --yes to spend these credits.")
        return 0

    cap = args.max_concurrent or int(plan.get("maxConcurrent", 5))
    cap = max(1, min(cap, 5))
    runner = Runner(api, man, out, download=not args.no_download)
    todo = [a for a in man.data["assets"] if not only or a["id"] in only]
    log(f"Running {len(todo)} assets with up to {cap} concurrent jobs. Manifest: {man.path}")
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=cap) as pool:
        futures = [pool.submit(runner.run_asset, a) for a in todo]
        try:
            for f in cf.as_completed(futures):
                f.result()
        except KeyboardInterrupt:
            runner.stop.set()
            log("Interrupted. Running jobs keep going server-side; re-run to resume them.")
            raise
    man.save()
    t = man.data["totals"]
    log(f"Finished in {int(time.time() - t0)}s: {t['done']}/{t['assets']} assets done, "
        f"{t['failed']} failed, ~{t['creditsSpentEstimate']} credits used in total.")
    if runner.stop.is_set():
        log(f"Stopped early: {runner.stop_reason}")
        return 2
    return 0 if t["failed"] == 0 and t["done"] == t["assets"] else 3


if __name__ == "__main__":
    sys.exit(main())
