import os
import sys
import re
import shutil
sys.path.append("server")
import run
run.setup_env()

import pdoc

modules = ["server"]
context = pdoc.Context()

modules = [pdoc.Module(mod, context=context) for mod in modules]
pdoc.link_inheritance(context)

def recursive_htmls(mod):
    yield mod.name, mod.html()
    for submod in mod.submodules():
        yield from recursive_htmls(submod)

def recursive_texts(mod):
    yield mod.name, mod.text()
    for submod in mod.submodules():
        yield from recursive_texts(submod)

base_dir, _ = os.path.split(os.environ["SERVER_ROOT"])
dir_path = os.path.join(base_dir, "docs")
if not os.path.isdir(dir_path):
    os.mkdir(dir_path)
else:
    shutil.rmtree(dir_path)
    os.mkdir(dir_path)

def put(d, l, index, val):
    item = l[index]
    if item in d.keys():
        new_d = d[item]
    else:
        new_d = {}
        d[item] = new_d
    
    if len(l) - 1 == index:
        new_d["value"] = val
        new_d["full_name"] = ".".join(l[1:])
    else:
        return put(new_d, l, index + 1, val)

def walk_and_print(d, dir, prev_key=None):
    if "full_name" in d.keys() and "value" in d.keys():
        full_name = d.pop("full_name", "")
        value = d.pop("value", None)
        if prev_key is None or full_name == "": 
            filename = "index.html"
            item = "server"
        else: 
            splitted = re.split(r"\.", full_name)
            item = splitted[-1]
        if len(d.keys()) > 0:
            filename = "index.html"
            if full_name != "" and full_name is not None:
                new_dir_path = os.path.join(dir, item)
            else:
                new_dir_path = dir
        else:
            new_dir_path = dir
            filename = f'{item}.html'
        new_dir_path = new_dir_path.strip()
        if not os.path.isdir(new_dir_path):
            os.mkdir(new_dir_path)
            dir = new_dir_path

        with open(os.path.join(dir, filename), "xt", encoding="utf-8") as f:
            print(value, file=f)
    else:
        item = None
    for key in d.keys():
        walk_and_print(d[key], dir, item)
    
for mod in modules:
    the_dict = {}
    for module_name, text in recursive_htmls(mod):
        path = re.split(r"\.", module_name)
        put(the_dict, path, 0, text)

walk_and_print(the_dict, dir_path)