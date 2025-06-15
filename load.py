import json

def get_navs():
    with open("txt/register.txt", "r+") as f:
        return f.readlines()

def set_navs(navs):
    with open("txt/register.txt", "w+") as f:
        for i in range(len(navs)):
            f.write(navs[i])
            if i != len(navs) - 1:
                f.write("\n")

def get_memory():
    with open("txt/memory.json", "r+") as f:
        return json.load(f)
    
def set_memory(memory):
    with open("txt/memory.json", "w+", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)