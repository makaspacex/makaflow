from pathlib import Path
import glob
import os
import json


def update_json(repo_dir, out_path, icon_base_url):
    repo_dir = Path(repo_dir)
    icon_dir = f"{repo_dir}/IconSet"
    png_paths = list(glob.glob(f"{icon_dir}/**/*.png", recursive=True))
    res = {"name": "Maka Gallery", "description": "Makaflow收集互联网公开图标文件，版权属于原作者和商标持有人。"}
    icons = []
    
    for path in png_paths:
        path = path.replace(f"{repo_dir.parent}/", "")
        path = Path(path)
        
        new_name = "_".join(path.parts)
        d_path = "/".join(path.parts)
        downw_url = f"{icon_base_url}/{d_path}"
        icons.append({"name":new_name, "url":downw_url})

    res['icons'] = icons
    os.makedirs(Path(out_path).parent, exist_ok=True)
    json.dump(res, open(f"{out_path}", 'w+'))
    return res
    