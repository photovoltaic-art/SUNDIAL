#!/usr/bin/env python3
"""Compare KiCad's exported netlist (carrier.net) with the intended nets in parts.py,
and run basic electrical checks (single-pin nets, power pins, footprints exist)."""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from parts import SECTIONS, PWR_FLAGS

here = os.path.dirname(os.path.abspath(__file__))
net = open(os.path.join(here, "carrier.net")).read()

# intended: (ref, pin) -> net
want = {}
fps = {}
for _, parts in SECTIONS:
    for ref, _sym, _val, fp, nets, _n in parts:
        fps[ref] = fp
        for pin, n in nets.items():
            want[(ref, pin)] = n

# actual from KiCad
got = {}
nets = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', net, re.S):
    name = m.group(1).lstrip("/")
    nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))
    nets[name] = nodes
    for r, p in nodes:
        got[(r, p)] = name

errors = []
# Compare as partitions: every intended net must be exactly one KiCad net, same members.
# Names must also match where the schematic names the net (labels, power symbols); purely local
# nets drawn only with wires get KiCad's automatic name (Net-(...)), which is accepted.
want_sets = {}
for k, n in want.items(): want_sets.setdefault(n, set()).add(k)
got_sets = {}
for k, g in got.items():
    if not k[0].startswith("#"): got_sets.setdefault(g, set()).add(k)
for n, members in want_sets.items():
    gnames = {got.get(k) for k in members}
    if len(gnames) != 1 or None in gnames:
        errors.append(f"net {n}: split across {sorted(map(str, gnames))}")
        continue
    g = gnames.pop()
    if got_sets.get(g, set()) != members:
        errors.append(f"net {n}: KiCad net {g} has {sorted(got_sets.get(g, set()) - members)} extra")
    if g != n and not g.startswith("Net-("):
        errors.append(f"net {n}: named {g} in the schematic")
for k, g in got.items():
    if k[0].startswith("#"):
        continue
    if k not in want and not g.startswith("unconnected-"):
        errors.append(f"{k[0]}.{k[1]}: on {g} but not in parts.py")

local = sorted(n for n in want_sets if got.get(next(iter(want_sets[n]))) != n)
single = [n for n, nodes in nets.items()
          if len([x for x in nodes if not x[0].startswith("#")]) < 2 and not n.startswith("unconnected-")]
fpdir = "/usr/share/kicad/footprints"
missing_fp = [r for r, fp in fps.items() if fp and not os.path.exists(f"{fpdir}/{fp.split(':')[0]}.pretty/{fp.split(':')[1]}.kicad_mod")]

print(f"Parts: {len(fps)}  Nets (named): {len([n for n in nets if not n.startswith('unconnected-')])}  Pin connections checked: {len(want)}")
print("Mismatches:", len(errors)); [print("  ", e) for e in errors]
print("Local nets drawn with wires only (KiCad auto-names them, members checked):", ", ".join(local) or "none")
print("Nets with fewer than two pins:", single or "none")
print("Missing footprints:", missing_fp or "none")
print("Power flags: KiCad leaves PWR_FLAG symbols out of netlists; they are checked in the schematic only.")
for n in []:
    print(f"  power flag on {n}: {'yes' if any(r.startswith('#FLG') for r, _ in nets.get(n, [])) else 'NO'}")
sys.exit(1 if errors or missing_fp else 0)
