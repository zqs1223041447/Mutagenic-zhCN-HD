import json
from pathlib import Path
p=Path("migration/inventory/p4_art_mapping.json")
j=json.loads(p.read_text(encoding="utf-8"))
weak_refs=set([
 "res://sprites/monsters/attack_dog.aseprite",
 "res://sprites/monsters/chilled_bones.aseprite",
 "res://sprites/player/heads/dragon.aseprite",
 "res://sprites/player/pants/dragon.aseprite",
 "res://sprites/player/back/dragon_wings.aseprite",
 "res://sprites/player/feet/frozen_boots.aseprite",
 "res://sprites/monsters/lightning_dog.aseprite",
 "res://sprites/monsters/spirit_of_the_ancient.aseprite",
 "res://sprites/worldmap/map_highlighted.aseprite",
])
for e in j["entries"]:
    if e["missing_ref"] in weak_refs:
        bucket=e["bucket"]
        stem=Path(e["missing_ref"][6:]).stem
        e["status"]="PLACEHOLDER"
        e["mapped_path"]=f"res://sprites/_placeholders/{bucket}/{stem}.png"
        e["source"]=None
        e["license"]="generated-placeholder"
        e["author"]="-"
        if "shares" not in e.get("note",""):
            e["note"]="no own remap or pack match found; generated stand-in"
# recount
counts={"OWN_REMAP":0,"MAPPED":0,"PLACEHOLDER":0}
for e in j["entries"]:
    counts[e["status"]]+=1
j["summary"]["own_remap"]=counts["OWN_REMAP"]
j["summary"]["mapped"]=counts["MAPPED"]
j["summary"]["placeholder"]=counts["PLACEHOLDER"]
j["generated_at"]="2026-08-22T13:40:00Z"
p.write_text(json.dumps(j, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(counts)
