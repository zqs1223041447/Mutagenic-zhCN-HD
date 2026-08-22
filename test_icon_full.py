import json, zipfile
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
product=Path("product")
own_index={}
for base in [product/"sprites", Path("04_recovered/sprites"), Path("03_raw/sprites")]:
    if not base.is_dir(): continue
    for png in base.rglob("*.png"):
        if any(part in ("_mapped","_placeholders","_acquired") for part in png.relative_to(base).parts):
            continue
        own_index.setdefault(png.stem.lower(),[]).append(png)

def build(min_score):
    counts={"OWN_REMAP":0,"MAPPED":0,"PLACEHOLDER":0}
    demoted=[]
    for item in sorted(inv["items"], key=lambda i:(i["category"], Path(i["missing_ref"][6:]).stem.lower(), i["expected_suffix"]!=".png")):
        ref=item["missing_ref"]
        suffix=item["expected_suffix"]
        bucket=item["category"]
        stem=Path(ref[6:]).stem
        if suffix not in (".png",".aseprite"):
            counts["PLACEHOLDER"]+=1
            continue
        if stem.lower() in own_index:
            counts["OWN_REMAP"]+=1
            continue
        tokens=tokenize(stem)
        candidates=[]
        deny={"actors":{"orb","gauge","leaf","ruins"},"tiles":{"orb","gauge","leaf","ruins"}}.get(bucket,set())
        for key, entries in by_name.items():
            for e in entries:
                toks=e["icon"].lower().replace("-","_").split("_")
                if any(d in toks for d in deny):
                    continue
                score=match_score(stem,tokens,e["icon"])
                if score < min_score: continue
                # icon-in-stem full
                icon_tokens=e["icon"].lower().replace("-","_").split("_")
                hits_icon=[t for t in icon_tokens if t in tokens]
                # require all icon tokens in stem (or exact)
                if stem.lower()!=e["icon"].lower().replace("-","_"):
                    if len(hits_icon)!=len(icon_tokens):
                        continue
                if score>0:
                    candidates.append((score,e["icon"],e))
        if candidates:
            candidates.sort(key=lambda c:(-c[0], len(c[1]), c[1]))
            counts["MAPPED"]+=1
        else:
            counts["PLACEHOLDER"]+=1
            # check old mapped?
            demoted.append(stem)
    return counts, demoted

for ms in [6,12]:
    c,d=build(ms)
    print(ms,c, d[:5])
