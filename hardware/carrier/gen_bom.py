#!/usr/bin/env python3
"""Write bom.csv from parts.py: one line per value+footprint, references grouped."""
import csv, os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from parts import SECTIONS
from mpn import MPN
from placement import PLACEMENT
def key(r): m = re.match(r"([A-Z_]+)(\d+)", r); return (m.group(1), int(m.group(2))) if m else (r, 0)
groups = {}
for sec, parts in SECTIONS:
    for ref, (lib, name), value, fp, nets, note in parts:
        g = groups.setdefault((value, fp), {"refs": [], "notes": set(), "section": sec.split(" ")[0].rstrip(".")})
        g["refs"].append(ref)
        if note: g["notes"].add(note)
rows = sorted(groups.items(), key=lambda kv: key(sorted(kv[1]["refs"], key=key)[0]))
with open(os.path.join(os.path.dirname(__file__), "bom.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["References", "Qty", "Value / rating", "Footprint", "Fitted", "Manufacturer", "MPN", "Confirm", "Placement", "Section (first)", "Notes"])
    for (value, fp), g in rows:
        refs = sorted(g["refs"], key=key)
        fitted = "no (DNP)" if value.startswith("DNP") else ("holder only" if "NOT fitted" in value else "yes")
        mp = [MPN[r] for r in refs if r in MPN]
        if refs[0].startswith("H"): mp = [("", "", "mounting holes, no part")]
        assert mp and all(m == mp[0] for m in mp) and len(mp) == (len(refs) if not refs[0].startswith("H") else 1), f"MPN missing or mixed for {refs}"
        man, num, chk = mp[0]
        pl = "; ".join(f"{r}: {PLACEMENT[r][0]} - {PLACEMENT[r][1]}" for r in refs if r in PLACEMENT)
        w.writerow([" ".join(refs), len(refs), value, fp, fitted, man, num, chk, pl, g["section"], "; ".join(sorted(g["notes"]))])
    w.writerow([])
    w.writerow(["Fitted by the builder (not assembled):", "", "ELEGOO ESP32 30-pin; ANGEEK buck 8-60 V set to 5.0 V; 2x 2.7 V 10 F supercaps; CR2032; DS18B20 probe(s); JP1 jumper; AUX fuse; microSD card", "", "", "", "", "", "", "", "See CARRIER.md"])
print(len(rows), "BOM lines")
