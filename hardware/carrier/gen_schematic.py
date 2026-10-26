#!/usr/bin/env python3
"""Generate the PVA carrier v1 KiCad 7 schematic from parts.py.

Wired style (draft-2, 26 Oct 2026, at the board designer's request):
- each functional block is drawn with wires: every capacitor and resistor sits beside the
  pin it serves and is wired to it;
- +5V, +3V3 and GND use power symbols;
- net labels are used only where a signal leaves its block (to the ESP32 socket, test points, headers).

parts.py stays the source of the netlist. The layout below only decides where parts sit and
how wires run; verify.py then checks KiCad's own netlist against parts.py, pin by pin, and
this script refuses to write a sheet with accidental wire contacts.
"""
import re, uuid, sys, os, math
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from parts import SECTIONS, PWR_FLAGS

SYMDIR = "/usr/share/kicad/symbols"
POWER_NETS = {"+5V": "+5V", "+3V3": "+3V3", "GND": "GND"}
G = 2.54
_libcache = {}

def U(): return str(uuid.uuid4())
def r2(v): return round(v + 0.0, 2)
def P(x, y): return (r2(x), r2(y))

# ---------------------------------------------------------------- symbol library
def lib_text(lib):
    if lib not in _libcache:
        _libcache[lib] = open(f"{SYMDIR}/{lib}.kicad_sym").read()
    return _libcache[lib]

def find_block(text, name):
    i = text.find(f'\n  (symbol "{name}"')
    if i < 0: raise KeyError(name)
    i += 1
    depth = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == '(': depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0: return text[i:j + 1]
    raise ValueError(name)

def flat_symbol(lib, name):
    t = lib_text(lib)
    blk = find_block(t, name)
    m = re.search(r'\(extends "([^"]+)"\)', blk)
    if m:
        base = m.group(1)
        bblk = find_block(t, base)
        props = re.findall(r'\n    \(property "[^"]+" .*?\n    \)', blk, re.S)
        body = re.sub(r'\n    \(property "[^"]+" .*?\n    \)', '', bblk, flags=re.S)
        body = body.replace(f'(symbol "{base}_', f'(symbol "{name}_')
        head, rest = body.split('\n', 1)
        head = head.replace(f'(symbol "{base}"', f'(symbol "{name}"')
        blk = head + ''.join(props) + '\n' + rest
    return blk.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)

def pins_of(blk):
    out = {}
    for m in re.finditer(r'\(pin (\w+) \w+ \(at ([-\d.]+) ([-\d.]+) (\d+)\) \(length ([-\d.]+)\).*?\(name "([^"]*)".*?\(number "([^"]*)"', blk, re.S):
        out[m.group(7)] = (float(m.group(2)), float(m.group(3)), int(m.group(4)), m.group(1))
    return out

lib_blocks = {}
def lib_pins(lib, name):
    key = f"{lib}:{name}"
    if key not in lib_blocks:
        lib_blocks[key] = flat_symbol(lib, name)
    return pins_of(lib_blocks[key])

# ---------------------------------------------------------------- geometry
def xform(px, py, rot, mirror):
    """Symbol coords (y up) -> offset in sheet coords (y down)."""
    if mirror: px = -px
    a = math.radians(rot)
    x = px * math.cos(a) - py * math.sin(a)
    y = px * math.sin(a) + py * math.cos(a)
    return r2(x), r2(-y)

def out_dir(ang, rot, mirror):
    """Unit vector (sheet coords) pointing away from the body at a pin."""
    a = (180 - ang) if mirror else ang      # direction towards the body, symbol coords
    a = math.radians(a + rot)
    tx, ty = round(math.cos(a)), round(-math.sin(a))
    return (-tx, -ty)

# ---------------------------------------------------------------- the sheet
ROOT = U()
items = []
PARTS = {r: (lib, nm, v, fp, nets) for _, ps in SECTIONS for r, (lib, nm), v, fp, nets, _n in ps}
placed = {}            # ref -> dict(pins: {num: (pt, outdir)}, ...)
wires = []             # (p1, p2)
labels = []            # (net, pt)
pwr_pins = []          # (net, pt)
touched = set()        # (ref, pin) handled explicitly
pwr_count = [0]

def place(ref, x, y, rot=0, mirror=False):
    lib, nm, value, fp, nets = PARTS[ref]
    pins = lib_pins(lib, nm)
    x, y = r2(x), r2(y)
    pp = {}
    for num, (px, py, ang, etype) in pins.items():
        dx, dy = xform(px, py, rot, mirror)
        pp[num] = (P(x + dx, y + dy), out_dir(ang, rot, mirror), etype)
    placed[ref] = dict(at=(x, y), rot=rot, mirror=mirror, pins=pp)
    return placed[ref]

def place_pin(ref, pin, pt, rot=0, mirror=False):
    """Place a part so that its pin `pin` lands on point pt."""
    lib, nm = PARTS[ref][0], PARTS[ref][1]
    px, py, ang, _ = lib_pins(lib, nm)[pin]
    dx, dy = xform(px, py, rot, mirror)
    return place(ref, pt[0] - dx, pt[1] - dy, rot, mirror)

def pt(s):
    if isinstance(s, tuple): return P(*s)
    ref, pin = s.split(".")
    touched.add((ref, pin))
    return placed[ref]["pins"][pin][0]

def W(*pts):
    ps = [pt(p) for p in pts]
    for a, b in zip(ps, ps[1:]):
        assert a[0] == b[0] or a[1] == b[1], f"wire not orthogonal {a}->{b}"
        if a != b: wires.append((a, b))

def ROT_FOR(outv, base):
    """Rotation for a power symbol whose body points along `base` by default, to point along outv."""
    order = [(0, -1), (-1, 0), (0, 1), (1, 0)]       # up, left, down, right: successive CCW 90
    return (order.index(outv) - order.index(base)) % 4 * 90

def PWR(net, p, outv=None):
    """Power symbol at point p. outv: direction the symbol body points (default: GND down, others up)."""
    p = pt(p)
    if net == "GND":
        lib, nm, base = "power", "GND", (0, 1)
    else:
        lib, nm, base = "power", net, (0, -1)
    outv = outv or base
    rot = ROT_FOR(outv, base)
    lib_pins(lib, nm)
    pwr_count[0] += 1
    ref = f"#PWR0{pwr_count[0]:02d}"
    tx, ty = p[0] + outv[0] * 5.0, p[1] + outv[1] * 5.0
    pj = ""
    if outv[0] != 0:                      # sideways symbol: horizontal text beyond it
        tx, ty = p[0] + outv[0] * 4.2, p[1] + 0.4
        pj = " (justify right)" if outv[0] < 0 else " (justify left)"
    pfa = rot if rot in (90, 270) else 0
    items.append(f'  (symbol (lib_id "{lib}:{nm}") (at {p[0]:.2f} {p[1]:.2f} {rot}) (unit 1)\n'
                 f'    (in_bom no) (on_board no) (dnp no) (uuid {U()})\n'
                 f'    (property "Reference" "{ref}" (at {p[0]:.2f} {p[1]:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (property "Value" "{net}" (at {tx:.2f} {ty:.2f} {pfa}) (effects (font (size 1.27 1.27)){pj}))\n'
                 f'    (property "Footprint" "" (at {p[0]:.2f} {p[1]:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (property "Datasheet" "" (at {p[0]:.2f} {p[1]:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (pin "1" (uuid {U()}))\n'
                 f'    (instances (project "carrier" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
    pwr_pins.append((net, p))

def LBL(net, p, outv):
    """Net label at p; text runs in direction outv."""
    p = pt(p)
    la = {(-1, 0): 180, (1, 0): 0, (0, -1): 90, (0, 1): 270}[outv]
    just = "right" if la in (180, 270) else "left"
    items.append(f'  (label "{net}" (at {p[0]:.2f} {p[1]:.2f} {la}) (fields_autoplaced)\n'
                 f'    (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {U()}))')
    labels.append((net, p))

def TERM(net, p, outv, stub=G):
    """Stub from p along outv, ending in a power symbol (power nets) or a label."""
    p = pt(p)
    q = P(p[0] + outv[0] * stub, p[1] + outv[1] * stub)
    W(p, q)
    if net in POWER_NETS: PWR(net, q, outv)
    else: LBL(net, q, outv)

def text(t, x, y, size=2.54):
    items.append(f'  (text "{t}" (at {x:.2f} {y:.2f} 0) (effects (font (size {size} {size}) bold) (justify left bottom)) (uuid {U()}))')

def note(t, x, y, size=1.5):
    items.append(f'  (text "{t}" (at {x:.2f} {y:.2f} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {U()}))')

def finish_part(ref):
    """Emit the symbol, and terminate pins not wired explicitly."""
    lib, nm, value, fp, nets = PARTS[ref]
    d = placed[ref]
    x, y = d["at"]
    pts = [v[0] for v in d["pins"].values()] or [(x, y)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if w <= h:   # tall part: text to the right
        tx, ty0 = max(xs) + 2.54 if w > 0 else x + 2.54, (min(ys) + max(ys)) / 2
        refp, valp, just = (tx, ty0 - 1.27), (tx, ty0 + 1.27), " (justify left)"
    else:        # wide part: text above and below
        refp, valp, just = (x, min(ys) - 3.2), (x, max(ys) + 3.2), ""
    if nm.startswith("Screw_Terminal") or nm.startswith("Conn_01x"):
        side = -1 if d["mirror"] else 1
        bx = x + side * (4.5 if nm.startswith("Screw") else 3.0)
        j = " (justify left)" if side > 0 else " (justify right)"
        refp, valp, just = (bx, min(ys) - 1.3), (bx, max(ys) + 2.6), j
        if nm in ("Conn_01x15", "Conn_01x09", "Conn_01x04"):
            refp, valp, just = (x, min(ys) - 4.5), (x, max(ys) + 4.5), ""
    if nm in ("Micro_SD_Card_Det_Hirose_DM3AT",):
        refp, valp, just = (x, min(ys) - 4.5), (x, max(ys) + 4.5), ""
    if nm in ("DS3231M", "INA180A3", "MCP1416", "AP22804AW5"):
        refp, valp, just = (max(xs) + 1.5, max(ys) - 2.0), (max(xs) + 1.5, max(ys) + 0.5), " (justify left)"
    if nm == "TestPoint":
        refp, valp, just = (x + 2.0, y - 5.5), (x + 2.0, y - 3.5), " (justify left)"
    if nm == "MountingHole":
        refp, valp, just = (x, y - 4), (x, y + 4), ""
    if ref in OVR:
        (rx, ry), (vx, vy), j = OVR[ref]
        refp, valp, just = (x + rx, y + ry), (x + vx, y + vy), j
    if ((d["rot"] != 0) != d["mirror"]) and just:      # KiCad turns the text upright and mirrors its justification
        just = {" (justify left)": " (justify right)", " (justify right)": " (justify left)"}[just]
    dnp = value.startswith("DNP")
    value = SHORT.get(ref, value)
    fa = d["rot"] if d["rot"] in (90, 270) else 0
    mir = " (mirror y)" if d["mirror"] else ""
    pin_uuids = " ".join(f'(pin "{n}" (uuid {U()}))' for n in d["pins"])
    items.append(f'  (symbol (lib_id "{lib}:{nm}") (at {x:.2f} {y:.2f} {d["rot"]}){mir} (unit 1)\n'
                 f'    (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"})\n'
                 f'    (uuid {U()})\n'
                 f'    (property "Reference" "{ref}" (at {refp[0]:.2f} {refp[1]:.2f} {fa}) (effects (font (size 1.27 1.27)){just}))\n'
                 f'    (property "Value" "{value}" (at {valp[0]:.2f} {valp[1]:.2f} {fa}) (effects (font (size 1.27 1.27)){just}))\n'
                 f'    (property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (property "Datasheet" "~" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    {pin_uuids}\n'
                 f'    (instances (project "carrier" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
    done_pts = set()
    k = 0
    for num, (p, outv, etype) in sorted(d["pins"].items(), key=lambda kv: (kv[1][0][1], kv[1][0][0])):
        if (ref, num) in touched or p in done_pts: continue
        net = nets.get(num)
        done_pts.add(p)
        if net is None:
            items.append(f'  (no_connect (at {p[0]:.2f} {p[1]:.2f}) (uuid {U()}))')
        elif net in POWER_NETS and outv[0] != 0:
            TERM(net, p, outv, stub=G if k % 2 == 0 else 3 * G); k += 1
        else:
            TERM(net, p, outv)

# Short values for the drawing; the full rating stays in parts.py, bom.csv and CARRIER.md.
SHORT = {
    "J1": "PANEL+ / PANEL- (>=15 A)", "D0": "MBRB20100CT", "Q1": "IRLR3110Z", "D6": "DNP: SMCJ58A",
    "RSH1": "5m 1% 2512 3 W", "RSH2": "DNP: 10m 2512", "U2": "INA180A3", "U3": "MCP1416", "JP1": "Sun sensor on",
    "D1": "S3M", "J2": "BUCK IN", "F1": "2 A slow-blow", "J3": "BUCK OUT 5.0 V", "D2": "SMAJ5.0A",
    "C3": "470u 10V", "LED1": "Green", "J6": "Supercap 10 F (upper)", "J7": "Supercap 10 F (lower)",
    "U1": "DS3231SN", "BT1": "CR2032", "J4": "Probe 1", "J5": "Probe 2", "D3": "PESD3V3L1BA",
    "J8": "microSD (Hirose DM3AT)", "J9": "Spare GPIO", "J10": "UART", "J13": "I2C",
    "J11": "5V / 5V SW / 3V3 / GND", "F2": "PTC 0.5 A", "F3": "PTC 0.2 A", "U4": "AP22804AW5", "D4": "SS14",
    "J12": "AUX + / - (>=15 A)", "F4": "ATO holder, empty", "D5": "MBR10100",
    "J14": "ESP32 left row", "J15": "ESP32 right row", "R20": "DNP",
}

# Hand-placed reference/value text where the defaults collide: ref -> ((dx, dy) ref, (dx, dy) value, justify)
OVR = {
    "U3": ((-12.0, -12.0), (-12.0, -9.6), " (justify right)"),
    "U2": ((-4.5, 10.5), (-4.5, 13.0), " (justify right)"),
    "U4": ((-10.0, -10.0), (-10.0, -7.6), " (justify left)"),
    "RSH1": ((-3.0, 8.0), (-3.0, 10.5), " (justify right)"),
    "J2": ((4.5, -4.5), (4.5, -2.0), " (justify left)"),
    "J3": ((-4.5, -4.5), (-1.0, 7.0), " (justify right)"),
}

# ================================================================ layout, block by block
text("PVA carrier board v1 - schematic draft-2 (wired). Generated from hardware/CARRIER.md via parts.py. "
     "Engineer review required before manufacture.", 20, 22, 3)
note("Wired style: each capacitor and resistor is drawn beside the pin it serves. +5V, +3V3 and GND are power symbols. "
     "Net labels only where a signal leaves its block. Placement priorities: PLACEMENT.md.", 20, 26, 1.8)

def title(t, x, y): text(t, x, y)

# ---- 1. Panel input and sun sensor ---------------------------------------------------------
title("1. Panel input and sun sensor", 20, 45)
place("J1", 40, 60, mirror=True)                                   # pins face right
place_pin("D0", "1", (55.88, 60))
A = (53.34, 60)
W("J1.1", A, "D0.1"); W(A, (53.34, 65.08), "D0.3"); LBL("PANEL+", (46.99, 60), (1, 0))
W("J1.2", (48.26, 62.54), (48.26, 66.04)); PWR("GND", (48.26, 66.04))
PVP = (76.2, 62.54)
place_pin("Q1", "2", (76.2, 87.63))
W("D0.2", PVP, "Q1.2")
place_pin("D6", "1", (86.36, 62.54), rot=270)
W(PVP, "D6.1"); W("D6.1", (96.52, 62.54)); LBL("PV+", (96.52, 62.54), (1, 0))
# shunt and its sense lines
N = (76.2, 99.06)
place_pin("RSH1", "1", (76.2, 101.6)); place_pin("RSH2", "1", (88.9, 101.6))
W("Q1.3", N, "RSH1.1"); W(N, (88.9, 99.06), "RSH2.1")
B1, B2 = (76.2, 111.76), (88.9, 111.76)
W("RSH1.2", B1); W("RSH2.2", B2, B1)
W(B1, (76.2, 114.3)); PWR("GND", (76.2, 114.3))
note("Star ground: one point, at RSH1's GND end", 60, 120, 1.27)
place_pin("U2", "3", (104.14, 101.6))
W((88.9, 99.06), (99.06, 99.06), (99.06, 101.6), "U2.3")          # Kelvin: IN+ from the shunt top
W(B2, (99.06, 111.76), (99.06, 106.68), "U2.4")                    # Kelvin: IN- from the shunt bottom
vs = placed["U2"]["pins"]["5"][0]
W("U2.5", (vs[0], vs[1] - 5.08)); PWR("+3V3", (vs[0], vs[1] - 5.08))
place_pin("C6", "1", (vs[0] + 12.7, vs[1] - 5.08))
W((vs[0], vs[1] - 5.08), "C6.1"); PWR("GND", "C6.2")
o = placed["U2"]["pins"]["1"][0]
place_pin("R6", "1", (o[0] + 5.08, o[1]), rot=90)
W("U2.1", "R6.1")
r6 = placed["R6"]["pins"]["2"][0]
place_pin("C7", "1", (r6[0] + 5.08, r6[1]))
W("R6.2", "C7.1"); PWR("GND", "C7.2")
W("C7.1", (r6[0] + 12.7, r6[1])); LBL("ISENSE", (r6[0] + 12.7, r6[1]), (1, 0))
# gate drive
g = placed["Q1"]["pins"]["1"][0]                                    # (68.58, 87.63+5.08)
GN = (g[0] - 2.54, g[1])
place_pin("R4", "2", (GN[0] - 2.54, g[1]), rot=90)
W("R4.2", GN, "Q1.1"); W(GN, (GN[0], GN[1] - 5.08)); LBL("GATE", (GN[0], GN[1] - 5.08), (0, -1))
place_pin("R21", "1", (GN[0], g[1] + 2.54))
W(GN, "R21.1")
r21 = placed["R21"]["pins"]["2"][0]
W("R21.2", (r21[0], r21[1] + 2.54), (72.39, r21[1] + 2.54), (72.39, N[1]), N)
place_pin("U3", "5", placed["R4"]["pins"]["1"][0])
touched.add(("U3", "5"))
vd = placed["U3"]["pins"]["2"][0]
W("U3.2", (vd[0], vd[1] - 5.08)); PWR("+5V", (vd[0], vd[1] - 5.08))
place_pin("C11", "1", (vd[0] + 7.62, vd[1] - 5.08))
W((vd[0], vd[1] - 5.08), "C11.1"); PWR("GND", "C11.2")
inp = placed["U3"]["pins"]["3"][0]
GI = (inp[0] - 2.54, inp[1])
place_pin("JP1", "2", (GI[0] - 2.54, inp[1]))
W("JP1.2", GI, "U3.3")
place_pin("R5", "1", (GI[0], inp[1] + 2.54))
W(GI, "R5.1"); PWR("GND", "R5.2")
for r in ["J1", "D0", "Q1", "D6", "RSH1", "RSH2", "U2", "C6", "R6", "C7", "R4", "R21", "U3", "C11", "JP1", "R5"]:
    finish_part(r)

# ---- 2. Board supply: fuse, diode, divider -------------------------------------------------
title("2. Board supply", 150, 45)
LBL("PV+", (157.48, 62.54), (-1, 0))
place_pin("F1", "1", (162.56, 62.54), rot=90)
W((157.48, 62.54), "F1.1")
Q = (175.26, 62.54)
place_pin("D1", "2", (180.34, 62.54), mirror=True)                # anode on the left
W("F1.2", Q, "D1.2")
K = (190.5, 62.54)
place("J2", 198.12, 62.54)
W("D1.1", K, "J2.1")
W(K, (190.5, 57.15)); LBL("BUCK_IN+", (190.5, 57.15), (0, -1))
W("J2.2", (190.5, 65.08), (190.5, 68.58)); PWR("GND", (190.5, 68.58))
place_pin("R1", "1", (175.26, 67.31))
W(Q, "R1.1")
r1 = placed["R1"]["pins"]["2"][0]
V = (r1[0], r1[1] + 2.54)
place_pin("R2", "1", (V[0], V[1] + 2.54))
W("R1.2", V, "R2.1"); PWR("GND", "R2.2")
place_pin("C5", "1", (V[0] + 12.7, V[1] + 2.54))
W(V, (V[0] + 12.7, V[1]), "C5.1"); PWR("GND", "C5.2")
W(V, (V[0] - 7.62, V[1])); LBL("VDIV", (V[0] - 7.62, V[1]), (-1, 0))
for r in ["F1", "D1", "J2", "R1", "R2", "C5"]: finish_part(r)

# ---- 3. 5 V rail ---------------------------------------------------------------------------
title("3. 5 V rail", 225, 45)
place("J3", 228.6, 62.54, mirror=True)
j3 = placed["J3"]["pins"]["1"][0]
W("J3.2", (j3[0] + 2.54, j3[1] + 2.54), (j3[0] + 2.54, j3[1] + 6.35)); PWR("GND", (j3[0] + 2.54, j3[1] + 6.35))
taps = {"D2": 241.3, "C3": 254.0, "C4": 266.7, "R9": 279.4, "R7": 292.1, "J6": 302.26}
xs = [j3[0]] + list(taps.values())
for a, b in zip(xs, xs[1:]): W((a, 62.54), (b, 62.54))
PWR("+5V", (taps["J6"], 62.54))
place_pin("D2", "1", (taps["D2"], 62.54), rot=270); PWR("GND", "D2.2")
place_pin("C3", "1", (taps["C3"], 62.54)); PWR("GND", "C3.2")
place_pin("C4", "1", (taps["C4"], 62.54)); PWR("GND", "C4.2")
place_pin("R9", "1", (taps["R9"], 62.54))
r9 = placed["R9"]["pins"]["2"][0]
place_pin("LED1", "2", (r9[0], r9[1] + 2.54), rot=90)
W("R9.2", "LED1.2"); PWR("GND", "LED1.1")
place_pin("R7", "1", (taps["R7"], 62.54))
r7 = placed["R7"]["pins"]["2"][0]
place_pin("R8", "1", (r7[0], r7[1] + 2.54))
W("R7.2", "R8.1"); PWR("GND", "R8.2")
for r in ["D2", "C3", "C4", "R9", "R7", "J3"]: pt(f"{r}.1")
pt("C3.1"); pt("D2.1")
place_pin("J6", "1", (taps["J6"] + 5.08, 66.04))
place_pin("J7", "1", (taps["J6"] + 5.08, 73.66))
W((taps["J6"], 62.54), (taps["J6"], 66.04), "J6.1")
MIDX = taps["J6"] + 2.54
W("R7.2", (MIDX, r7[1]), (MIDX, 68.58), "J6.2")
W("R8.1", (MIDX + 1.27, r7[1] + 2.54))
W((MIDX + 1.27, r7[1] + 2.54), (MIDX + 1.27, 73.66), "J7.1")
LBL("MID", (r7[0] + 3.81, r7[1]), (1, 0))
W("J7.2", (taps["J6"], 76.2), (taps["J6"], 80.01)); PWR("GND", (taps["J6"], 80.01))
for r in ["J3", "D2", "C3", "C4", "R9", "LED1", "R7", "R8", "J6", "J7"]: finish_part(r)

# ---- 5. Clock ------------------------------------------------------------------------------
title("5. Clock", 320, 45)
place("U1", 365.76, 88.9)
vcc, vbat = placed["U1"]["pins"]["2"][0], placed["U1"]["pins"]["14"][0]
W("U1.2", (vcc[0], vcc[1] - 10.16)); PWR("+3V3", (vcc[0], vcc[1] - 10.16))
place_pin("C10", "1", (vcc[0] - 7.62, vcc[1] - 10.16))
W((vcc[0], vcc[1] - 10.16), "C10.1"); PWR("GND", "C10.2")
place_pin("BT1", "1", (vbat[0] + 38.1, vbat[1] - 5.08))
W("U1.14", (vbat[0], vbat[1] - 5.08), "BT1.1"); PWR("GND", "BT1.2"); LBL("VBAT", (vbat[0] + 5.08, vbat[1] - 5.08), (1, 0))
scl, sda = placed["U1"]["pins"]["16"][0], placed["U1"]["pins"]["15"][0]
nscl, nsda = (scl[0] - 10.16, scl[1]), (sda[0] - 10.16, sda[1])
place_pin("R11", "1", (nscl[0], nscl[1] - 2.54), rot=180)          # pull-up drawn upwards
W("U1.16", nscl, (nscl[0] - 10.16, nscl[1])); W(nscl, "R11.1"); PWR("+3V3", "R11.2")
LBL("SCL", (nscl[0] - 10.16, nscl[1]), (-1, 0))
place_pin("R10", "1", (nsda[0], nsda[1] + 2.54))                   # pull-up drawn downwards
W("U1.15", nsda, (nsda[0] - 10.16, nsda[1])); W(nsda, "R10.1"); PWR("+3V3", "R10.2", (0, 1))
LBL("SDA", (nsda[0] - 10.16, nsda[1]), (-1, 0))
finish_part("U1"); finish_part("C10"); finish_part("BT1"); finish_part("R10"); finish_part("R11")

# ---- 6. Temperature probes -----------------------------------------------------------------
title("6. Temperature probes", 425, 45)
place("J4", 477.52, 66.04); place("J5", 477.52, 78.74)
j4, j5 = placed["J4"]["pins"]["2"][0], placed["J5"]["pins"]["2"][0]
DX = j4[0] - 12.7
W("J4.2", (DX, j4[1])); W("J5.2", (DX, j5[1]), (DX, j4[1]))
nodes = [DX - 7.62 * i for i in range(1, 4)]
W((DX, j4[1]), (nodes[0], j4[1]), (nodes[1], j4[1]), (nodes[2], j4[1]))
place_pin("D3", "1", (nodes[0], j4[1] + 2.54), rot=270)
W((nodes[0], j4[1]), "D3.1"); PWR("GND", "D3.2")
place_pin("R12", "1", (nodes[1], j4[1] - 2.54), rot=180); W((nodes[1], j4[1]), "R12.1"); PWR("+3V3", "R12.2")
place_pin("R20", "1", (nodes[2], j4[1] - 2.54), rot=180); W((nodes[2], j4[1]), "R20.1"); PWR("+3V3", "R20.2")
place_pin("R13", "1", (nodes[2] - 5.08, j4[1]), rot=270)
W((nodes[2], j4[1]), "R13.1")
for r in ["J4", "J5", "D3", "R12", "R20", "R13"]: finish_part(r)

# ---- 7. microSD ----------------------------------------------------------------------------
title("7. microSD (future-proofing)", 500, 45)
place("J8", 571.5, 96.52)
pp = placed["J8"]["pins"]
LX = pp["2"][0][0] - 40.64                      # label column
pulls = [("2", "R14", 0), ("3", "R15", 1), ("7", "R16", 2), ("10", "R17", 3)]
for pin, r, k in pulls:
    p = pp[pin][0]
    nx = p[0] - 7.62 - 7.62 * k
    place_pin(r, "1", (nx, pp["1"][0][1] - 7.62 - 2.54), rot=180)  # all pull-ups in a row above the connector
    top = placed[r]["pins"]["1"][0]
    W(f"J8.{pin}", (nx, p[1]), (LX, p[1])); W((nx, p[1]), f"{r}.1")
    PWR("+3V3", f"{r}.2")
    LBL(PARTS["J8"][4][pin], (LX, p[1]), (-1, 0))
p5 = pp["5"][0]; W("J8.5", (LX, p5[1])); LBL("SD_SCK", (LX, p5[1]), (-1, 0))
vdd = pp["4"][0]
W("J8.4", (vdd[0] - 2.54, vdd[1])); PWR("+3V3", (vdd[0] - 2.54, vdd[1]), (-1, 0))
for pin in ("6", "9"):
    p = pp[pin][0]; W(f"J8.{pin}", (p[0] - 2.54, p[1])); PWR("GND", (p[0] - 2.54, p[1]), (-1, 0))
place_pin("C8", "1", (pp["11"][0][0] + 12.7, pp["4"][0][1] - 5.08)); PWR("+3V3", "C8.1"); PWR("GND", "C8.2")
place_pin("C9", "1", (pp["11"][0][0] + 20.32, pp["4"][0][1] - 5.08)); PWR("+3V3", "C9.1"); PWR("GND", "C9.2")
note("C8, C9: place at J8 pin 4 (VDD)", pp["11"][0][0] + 8, pp["4"][0][1] + 9, 1.27)
for r in ["J8", "R14", "R15", "R16", "R17", "C8", "C9"]: finish_part(r)

# ---- 9. Power take-off ---------------------------------------------------------------------
title("9. Power take-off for add-ons", 190, 150)
place("U4", 220.98, 177.8)
uin, uen, uout = placed["U4"]["pins"]["5"][0], placed["U4"]["pins"]["4"][0], placed["U4"]["pins"]["1"][0]
NI = (uin[0] - 5.08, uin[1])
W("U4.5", NI, (NI[0], NI[1] - 5.08)); PWR("+5V", (NI[0], NI[1] - 5.08))
place_pin("C12", "1", (NI[0] - 17.78, NI[1] + 2.54))
W(NI, (NI[0] - 17.78, NI[1]), "C12.1"); PWR("GND", "C12.2")
NE = (uen[0] - 2.54, uen[1])
place_pin("R18", "1", (NE[0], NE[1] + 2.54))
W("U4.4", NE, "R18.1"); PWR("GND", "R18.2")
place_pin("R19", "2", (NE[0] - 10.16, NE[1] + 2.54), rot=180)      # GPIO27 comes from below
W(NE, (NE[0] - 10.16, NE[1]), "R19.2")
NO = (uout[0] + 5.08, uout[1])
place("J11", 279.4, 190.5)
j11 = {k: v[0] for k, v in placed["J11"]["pins"].items()}
place_pin("C13", "1", (NO[0], NO[1] + 2.54))
ND = (NO[0] + 12.7, NO[1])
W("U4.1", NO, ND); W(NO, "C13.1"); PWR("GND", "C13.2")
place_pin("D4", "1", (ND[0], ND[1] + 2.54), rot=270)               # cathode to 5V_SW
W(ND, "D4.1"); PWR("GND", "D4.2")
W(ND, (j11["2"][0] - 5.08, ND[1]), (j11["2"][0] - 5.08, j11["2"][1]), "J11.2")
place_pin("F2", "2", (j11["1"][0] - 2.54, 172.72))
W("J11.1", (j11["1"][0] - 2.54, j11["1"][1]), "F2.2"); PWR("+5V", "F2.1")
N3 = (j11["3"][0] - 15.24, j11["3"][1])
place_pin("F3", "2", (N3[0], N3[1] + 5.08), rot=180)
W("J11.3", N3, "F3.2"); PWR("+3V3", "F3.1", (0, 1))
W(N3, (N3[0] - 7.62, N3[1])); LBL("+3V3_EXT", (N3[0] - 7.62, N3[1]), (-1, 0))
W("J11.4", (j11["4"][0] - 2.54, j11["4"][1]), (j11["4"][0] - 2.54, j11["4"][1] + 5.08)); PWR("GND", (j11["4"][0] - 2.54, j11["4"][1] + 5.08))
for r in ["U4", "C12", "R18", "R19", "C13", "D4", "J11", "F2", "F3"]: finish_part(r)

# ---- 10. AUX power out ---------------------------------------------------------------------
title("10. AUX power out", 310, 150)
LBL("PV+", (317.5, 170.18), (-1, 0))
place_pin("F4", "1", (322.58, 170.18), rot=90)
W((317.5, 170.18), "F4.1")
place_pin("D5", "2", (337.82, 170.18), mirror=True)
W("F4.2", "D5.2")
place("J12", 355.6, 170.18)
W("D5.1", "J12.1")
j12 = placed["J12"]["pins"]["2"][0]
W("J12.2", (j12[0] - 2.54, j12[1]), (j12[0] - 2.54, j12[1] + 7.62)); PWR("GND", (j12[0] - 2.54, j12[1] + 7.62))
for r in ["F4", "D5", "J12"]: finish_part(r)

# ---- 4. ESP32 socket -----------------------------------------------------------------------
title("4. ESP32 socket (ELEGOO 30-pin, plugged in; antenna keep-out)", 20, 150)
place("J14", 55.88, 190.5); place("J15", 132.08, 190.5)
finish_part("J14"); finish_part("J15")

# ---- 8. Expansion headers and test points --------------------------------------------------
title("8. Expansion headers and test points", 400, 150)
place("J13", 431.8, 172.72); place("J10", 431.8, 195.58); place("J9", 482.6, 182.88)
for r in ["J13", "J10", "J9"]: finish_part(r)
for i in range(1, 12):
    place(f"TP{i}", 520.7 + (i - 1) % 6 * 12.7, 172.72 + (i - 1) // 6 * 20.32)
    finish_part(f"TP{i}")

# ---- Mechanical ----------------------------------------------------------------------------
title("Mechanical", 400, 225)
for i in range(1, 5):
    place(f"H{i}", 410 + (i - 1) * 15, 240); finish_part(f"H{i}")

# ---- Power flags (ERC) ---------------------------------------------------------------------
title("Power flags (ERC)", 590, 150)
lib_pins("power", "PWR_FLAG")
for i, net in enumerate(PWR_FLAGS):
    x, y = 600 + (i % 3) * 22, 170 + (i // 3) * 22
    items.append(f'  (symbol (lib_id "power:PWR_FLAG") (at {x:.2f} {y:.2f} 0) (unit 1)\n'
                 f'    (in_bom no) (on_board no) (dnp no) (uuid {U()})\n'
                 f'    (property "Reference" "#FLG0{i+1}" (at {x:.2f} {y - 3:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y - 4:.2f} 0) (effects (font (size 1.27 1.27))))\n'
                 f'    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (property "Datasheet" "~" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
                 f'    (pin "1" (uuid {U()}))\n'
                 f'    (instances (project "carrier" (path "/{ROOT}" (reference "#FLG0{i+1}") (unit 1))))\n  )')
    q = P(x, y + 5.08)
    W((x, y), q)
    if net in POWER_NETS: PWR(net, q, (0, 1) if net == "GND" else (0, 1))
    else: LBL(net, q, (0, 1))

# ---- design notes --------------------------------------------------------------------------
def note_block(lines, x, y, ttl):
    text(ttl, x, y, 2.0)
    note("\\n".join(lines), x, y + 3)
note_block([
    "1. SUN-SENSOR LOOP: J1 -> D0 -> Q1 -> RSH1 -> GND (drawn in block 1)",
    "   Panel short-circuit current, ~1 ms every 10 s. Panel Isc 5.40 A (label), max ~6 A in cold strong sun.",
    "   A vertical panel peaks near 1.8 A at noon. The panel cannot supply more than its Isc.",
    "2. BOARD SUPPLY: PV+ -> F1 (2 A) -> D1 (3 A) -> buck -> +5V. Under 0.3 A. F1 and D1 are NOT in the measured path.",
    "3. AUX (optional): PV+ -> F4 (<= 3 A on v1; 9 A only with D5 on a heatsink) -> D5 -> J12. Never through the shunt.",
    "J1 and J12 '>= 15 A' is the terminal and wire rating, not a measured current.",
], 20, 290, "Current paths")
note_block([
    "ISENSE (GPIO 35): RSH1 5 mOhm x INA180A3 gain 100 = 0.5 V/A. Range 0-6 A (pulsed); output clamps at 3.3 V (~6.6 A), harmless.",
    "   U2 IN+ and IN- are Kelvin traces from the inner ends of RSH1's pads (drawn as separate wires from the shunt).",
    "VDIV (GPIO 34): R1 100k / R2 4k7 = x 22.3. Voc 44.5 V -> 2.00 V; 48 V -> 2.15 V; 60 V -> 2.69 V. Firmware DIVIDER = (100 + 4.7) / 4.7.",
], 20, 320, "Measurement ranges")
note_block([
    "The ESP32 is a complete ELEGOO dev board plugged into J14/J15: EN pull-up, buttons, USB-serial and strapping are on that board.",
    "EN and GPIO 0, 1, 2, 3, 12, 15 are not brought out. GPIO 5 (strapping) is held high by R14.",
    "Q1 gate: U3 drives it when +5V exists; R21 (100k, gate-source) holds Q1 off before that, at dawn.",
    "D6 (TVS on PV+): footprint only; fitted if the v1 bench test shows turn-off overshoot. Then Q1 >= 100 V.",
], 20, 345, "ESP32 module and Q1 gate")

# ================================================================ checks before writing
def on_seg(p, a, b):
    if a[0] == b[0] == p[0]: return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]: return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False
anchors = [p for a, b in wires for p in (a, b)]
pinpts = [v[0] for d in placed.values() for v in d["pins"].values()]
problems = []
for p in set(anchors + pinpts + [p for _, p in pwr_pins]):          # labels may sit on a wire
    for a, b in wires:
        if on_seg(p, a, b): problems.append(f"point {p} touches the middle of wire {a}-{b}")
for i, (a, b) in enumerate(wires):
    for c, d in wires[i + 1:]:
        if a[0] == b[0] == c[0] == d[0] and max(min(a[1], b[1]), min(c[1], d[1])) < min(max(a[1], b[1]), max(c[1], d[1])):
            problems.append(f"overlapping wires {a}-{b} / {c}-{d}")
        if a[1] == b[1] == c[1] == d[1] and max(min(a[0], b[0]), min(c[0], d[0])) < min(max(a[0], b[0]), max(c[0], d[0])):
            problems.append(f"overlapping wires {a}-{b} / {c}-{d}")
missing = [r for r in PARTS if r not in placed]
if missing: problems.append(f"parts not placed: {missing}")
if problems:
    print("\n".join(problems[:40])); sys.exit("layout problems: not written")

cnt = defaultdict(int)
for p in anchors: cnt[p] += 1
for p in pinpts + [p for _, p in pwr_pins]:
    if cnt.get(p): cnt[p] += 1
for p, n in cnt.items():
    if n >= 3: items.append(f'  (junction (at {p[0]:.2f} {p[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
for a, b in wires:
    items.append(f'  (wire (pts (xy {a[0]:.2f} {a[1]:.2f}) (xy {b[0]:.2f} {b[1]:.2f})) (stroke (width 0) (type default)) (uuid {U()}))')

sch = ['(kicad_sch (version 20230121) (generator eeschema)', f'  (uuid {ROOT})', '  (paper "A1")',
       '  (title_block (title "PVA carrier board v1") (date "2026-10-26") (rev "draft-2") (company "photovoltaic-art / SUNDIAL")',
       '    (comment 1 "Generated from hardware/CARRIER.md by gen_schematic.py (wired style)") (comment 2 "Draft: engineer review required before manufacture"))',
       '  (lib_symbols']
for k, b in lib_blocks.items():
    sch.append('    ' + b.replace('\n', '\n  '))
sch.append('  )')
sch += items
sch.append('  (sheet_instances (path "/" (page "1")))')
sch.append(')')
open(os.path.join(os.path.dirname(__file__), "carrier.kicad_sch"), "w").write("\n".join(sch) + "\n")
print("parts:", len(placed), "wires:", len(wires), "power symbols:", len(pwr_pins), "labels:", len(labels))
