import json

def get_navs():
    with open("txt/register.json", "r+") as f:
        return json.load(f)

def set_navs(navs):
    with open("txt/register.json", "w+", encoding="utf-8") as f:
        json.dump(navs, f, ensure_ascii=False, indent=4)

def get_memory():
    with open("txt/memory.json", "r+") as f:
        return json.load(f)
    
def set_memory(memory):
    with open("txt/memory.json", "w+", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)