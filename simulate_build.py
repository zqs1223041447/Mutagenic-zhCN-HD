import json, zipfile, pathlib, subprocess
from pathlib import Path

STOPWORDS={"default","small","large","icon","new","sprite","effect"}
def tokenize(stem):
    t=[x for x in stem.lower().replace("-","_").split("_") if x]
    return [x for x in t if x not in STOPWORDS]
def match_score(stem, tokens, icon, use_word=True):
    name=icon.lower().replace("-","_")
    if name==stem.lower():
        return 100
    if not tokens:
        return 0
    if use_word:
        name_tokens=name.split("_")
        hits=[t for t in tokens if t in name_tokens]
    else:
        hits=[t for t in tokens if t in name]
    if not hits:
        return 0
    score=sum(len(t) for t in hits)
    if len(hits)==len(tokens):
        score+=10*len(tokens)
    return score

inv=json.loads(Path("migration/inventory/p4_art_missing_inventory_217.json").read_text())
gi_zip=Path("runtime/p4_art_downloads/game-icons.net.png.zip")
zf=zipfile.ZipFile(gi_zip)
by_name={}
for info in zf.infolist():
    if not info.filename.endswith(".png"): continue
    parts=info.filename.split("/")
    if len(parts)<5 or parts[0]!="icons": continue
    author,icon=parts[-2], parts[-1][:-4]
    by_name.setdefault(icon.lower(),[]).append({"author":author,"icon":icon})

# own index simulation
repo_root=Path(".")
product=Path("product")
own_index={}
for base in [product/"sprites", Path("04_recovered/sprites"), Path("03_raw/sprites")]:
    if not base.is_dir(): continue
    for png in base.rglob("*.png"):
        if any(part in ("_mapped","_placeholders","_acquired") for part in png.relative_to(base).parts):
            continue
        own_index.setdefault(png.stem.lower(),[]).append(png)

def build(min_score, use_deny, use_full, use_word):
    counts={"OWN_REMAP":0,"MAPPED":0,"PLACEHOLDER":0}
    for item in sorted(inv["items"], key=lambda i:(i["category"], Path(i["missing_ref"][6:]).stem.lower(), i["expected_suffix"]!=".png")):
        ref=item["missing_ref"]
        suffix=item["expected_suffix"]
        bucket=item["category"]
        stem=Path(ref[6:]).stem
        if suffix not in (".png",".aseprite"):
            counts["PLACEHOLDER"]+=1
            continue
        # check own
        if stem.lower() in own_index:
            counts["OWN_REMAP"]+=1
            continue
        # key sharing not simulated for simplicity, but most OWN share? ignore
        tokens=tokenize(stem)
        # find best
        candidates=[]
        deny={"actors":{"orb","gauge","leaf","ruins"},"tiles":{"orb","gauge","leaf","ruins"}}.get(bucket,set()) if use_deny else set()
        for key, entries in by_name.items():
            for e in entries:
                if deny:
                    toks=e["icon"].lower().replace("-","_").split("_")
                    if any(d in toks for d in deny):
                        continue
                score=match_score(stem,tokens,e["icon"],use_word)
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
        if candidates:
            candidates.sort(key=lambda c:(-c[0], len(c[1]), c[1]))
            counts["MAPPED"]+=1
        else:
            counts["PLACEHOLDER"]+=1
    return counts

for cfg in [(12,True,True,True),(6,True,True,True),(12,True,False,True),(6,True,False,True),(0,True,False,True),(12,False,False,False)]:
    c=build(*cfg)
    print(cfg, c)
