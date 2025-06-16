import json

def get_json(path):
    with open(path, "r+") as f:
        return json.load(f)
def set_json(path, dic):
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)

def get_navs():
    return get_json("txt/register.json")
def set_navs(navs):
    set_json("txt/register.json", navs)

def get_memory():
    return get_json("txt/memory.json")    
def set_memory(memory):
    set_json("txt/memory.json", memory)
    
def get_settings():
    return get_json("txt/settings.json")    
def set_settings(settings):
    set_json("txt/settings.json", settings)