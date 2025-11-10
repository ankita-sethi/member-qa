import json
from pathlib import Path

RAW_FILE = Path("data/response.json")
STORE_FILE = Path("data/store.json")

# Step 1: Load the JSON file
with open(RAW_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)
    data = raw.get("items", [])

print(f"Loaded {len(data)} messages")

# Step 2: Group by first name
map={}
store = {}

for item in data:
    name = (item.get("user_name") or "").strip()
    msg = (item.get("message") or "").strip()
    ts = (item.get("timestamp") or "").strip()
    uid=(item.get("user_id")or "").strip()
    
    #checking for duplicate names or user ids
    if name not in map:
        map[name]=[uid]
    else:
        if uid not in map[name]:
            print("duplicate")
            print(uid,name)
            map[name].append(uid)


    if not name or not msg:
        continue

    first_name = name.split()[0].strip().capitalize()
    if first_name not in store:
        store[first_name]=[]

    store[first_name].append({
        "full_name": name,
        "message": msg,
        "timestamp": ts
    })

# Step 3: Save to new JSON file
STORE_FILE.parent.mkdir(exist_ok=True)
with open(STORE_FILE, "w", encoding="utf-8") as f:
    json.dump(store, f, ensure_ascii=False, indent=2)

print(f"There are a total of {len(store)} unique first names")
