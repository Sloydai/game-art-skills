"""Batch-import an exported pack into Unreal Engine 5.

Run inside the Unreal Editor (Python Editor Script Plugin enabled):
    Tools > Execute Python Script... > unreal_import.py
or from the Output Log's Python console:
    py "C:/path/to/unreal_import.py" "C:/path/to/art/dungeon/export/unreal" "/Game/Art/Dungeon"

Imports every .glb in the folder as a Static Mesh asset under the destination path, with the
file name (already SM_-prefixed by glb_tool.py export) as the asset name, then saves. Unreal's
glTF importer converts glTF meters to centimeters.
"""

import os
import sys

import unreal  # available only inside the editor

DEFAULT_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export", "unreal")
DEFAULT_DST = "/Game/Art/SloydPack"


def main(src: str, dst: str) -> None:
    files = sorted(f for f in os.listdir(src) if f.lower().endswith(".glb"))
    if not files:
        unreal.log_warning(f"No .glb files in {src}")
        return
    tasks = []
    for f in files:
        t = unreal.AssetImportTask()
        t.filename = os.path.join(src, f)
        t.destination_path = dst
        t.destination_name = os.path.splitext(f)[0]
        t.automated = True       # no dialogs
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    done = sum(1 for t in tasks if t.imported_object_paths)
    unreal.log(f"Sloyd pack: imported {done}/{len(tasks)} files into {dst}")
    for t in tasks:
        if not t.imported_object_paths:
            unreal.log_warning(f"Failed: {t.filename}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC, sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DST)
