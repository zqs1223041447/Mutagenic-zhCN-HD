import json, subprocess, zipfile
from pathlib import Path

STOPWORDS={"default","small","large","icon","new","sprite","effect"}
def tokenize(stem):
    t=[x for x in stem.lower().replace("-","_").split("_") if x]
    return [x for x in t if x not in STOPWORDS]
def match_score(stem, tokens, icon):
    name=icon.lower().replace("-","_")
    if name==stem.lower():
        return 100
    if not tokens:
        return 0
    name_tokens=name.split("_")
    hits=[t for t in tokens if t in name_tokens]
    if not hits:
        return 0
    score=sum(len(t) for t in hits)
    if len(hits)==len(tokens):
        score+=10*len(tokens)
    return score

old_text=subprocess.check_output(["git","show","HEAD:migration/inventory/p4_art_mapping.json"]).decode()
old=json.loads(old_text)
inv=json.loads(Path("migration/inventory/p4_art_missing_inventory_217.json").read_text(encoding="utf-8"))
gi_zip=Path("runtime/p4_art_downloads/game-icons.net.png.zip")
zf=zipfile.ZipFile(gi_zip)
by_name={}
for info in zf.infolist():
    if not info.filename.endswith(".png"): continue
    parts=info.filename.split("/")
    if len(parts)<5 or parts[0]!="icons": continue
    author,icon=parts[-2], parts[-1][:-4]
    key=icon.lower()
    by_name.setdefault(key,[]).append({"author":author,"icon":icon,"zip_path":info.filename})

def best_for(stem, tokens, bucket, min_score, use_deny, use_full, use_word):
    candidates=[]
    deny={"actors":{"orb","gauge","leaf","ruins"},"tiles":{"orb","gauge","leaf","ruins"}}.get(bucket,set()) if use_deny else set()
    for key, entries in by_name.items():
        for e in entries:
            if deny:
                toks=e["icon"].lower().replace("-","_").split("_")
                if any(d in toks for d in deny):
                    continue
            if use_word:
                score=match_score(stem,tokens,e["icon"])
            else:
                name=e["icon"].lower().replace("-","_")
                if name==stem.lower():
                    score=100
                else:
                    if not tokens: score=0
                    else:
                        hits=[t for t in tokens if t in name]
                        if not hits: score=0
                        else:
                            score=sum(len(t) for t in hits)
                            if len(hits)==len(tokens):
                                score+=10*len(tokens)
            if score < min_score: continue
            if use_full and tokens:
                if use_word:
                    name_tokens=e["icon"].lower().replace("-","_").split("_")
                    hits=[t for t in tokens if t in name_tokens]
                    if stem.lower()!=e["icon"].lower().replace("-","_"):
                        if len(hits)!=len(tokens):
                            continue
                else:
                    hits=[t for t in tokens if t in e["icon"].lower()]
                    if len(hits)!=len(tokens):
                        continue
            if score>0:
                candidates.append((score,e["icon"],e))
    if not candidates: return None
    candidates.sort(key=lambda c: (-c[0], len(c[1]), c[1]))
    return candidates[0][2]

configs=[
    (12,True,True,True),
    (6,True,True,True),
    (5,True,True,True),
    (12,True,False,True),
    (6,True,False,True),
    (5,True,False,True),
    (0,True,False,True),
    (12,True,True,False),
]

for ms,deny,full,word in configs:
    cnt=0
    for item in inv["items"]:
        if item["expected_suffix"] not in (".png",".aseprite"): continue
        stem=Path(item["missing_ref"][6:]).stem
        tokens=tokenize(stem)
        b=item["category"]
        best=best_for(stem,tokens,b,ms,deny,full,word)
        if best:
            cnt+=1
    print(f"MIN {ms} deny {deny} full {full} word {word} => MAPPED {cnt}")

print("--- detail for 12 deny full word ---")
for item in inv["items"]:
    if item["expected_suffix"] not in (".png",".aseprite"): continue
    stem=Path(item["missing_ref"][6:]).stem
    tokens=tokenize(stem)
    b=item["category"]
    old_entry=next((e for e in old["entries"] if e["missing_ref"]==item["missing_ref"]), None)
    if old_entry and old_entry["status"]=="MAPPED":
        best=best_for(stem,tokens,b,12,True,True,True)
        print(stem, "old",old_entry["source"], "new", best["icon"] if best else "PLACEHOLDER", "tokens",tokens)
