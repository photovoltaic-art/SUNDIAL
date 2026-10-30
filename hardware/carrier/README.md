# Carrier board v1 — schematic draft

A KiCad schematic for the carrier board, generated from the specification in [CARRIER.md](../CARRIER.md).

> **Status: draft-2, 26 Oct 2026: schematic redrawn with wires at the board designer's request; reviews 1 and 2 applied, part numbers added 23 Oct. Awaiting the manufacturer's review. Do not manufacture from this yet.**
> It is a faithful drawing of the spec, checked by script and by two reviews. Before layout it needs the manufacturer's review and sign-off ([below](#manufacturer-review-and-sign-off)). The board switches a 45 V panel's full short-circuit current every 10 seconds.

## Start here (for the board designer)

Everything needed is linked from this page:

1. **[Specification: CARRIER.md](../CARRIER.md)** (also as a [PDF](../PVA_carrier_board_spec_v1.pdf)): what the board does, every part with its rating, layout rules, bench test.
2. **[Schematic PDF](carrier_schematic.pdf)** (A1): the full drawing, with notes on current paths and measurement ranges.
3. **[Bill of materials: bom.csv](bom.csv)**: references, values and ratings, footprints, fitted or not, and a **proposed manufacturer and part number for every line** (equivalents welcome; the few lines to confirm are marked).
4. **KiCad files:** [carrier.kicad_pro](carrier.kicad_pro), [carrier.kicad_sch](carrier.kicad_sch), and the netlist with footprints [carrier.net](carrier.net). Download the whole folder to open the project.
5. **[Placement: PLACEMENT.md](PLACEMENT.md)**: which capacitor or resistor goes next to which part (the schematic joins parts by net name, so it does not show this).
6. **[Design checks: checks.txt](checks.txt)**: the calculations behind the ranges and ratings.
7. **[Review log](#review-log)** and **[manufacturer sign-off](#manufacturer-review-and-sign-off)**, further down this page.

The board as a sundial on its panel, and its mounting: [GNOMON.md](../GNOMON.md). The firmware it runs: [panel_page_server.ino](../../firmware/panel_page_server/panel_page_server.ino).

## Files

| File | What |
| --- | --- |
| [carrier.kicad_pro](carrier.kicad_pro), [carrier.kicad_sch](carrier.kicad_sch) | KiCad project and schematic (KiCad 7 format; opens in KiCad 7 and 8) |
| [carrier_schematic.pdf](carrier_schematic.pdf) | The schematic as a PDF (A1), for review |
| [carrier.net](carrier.net) | Netlist exported by KiCad, with footprints: what a layout designer imports |

**Using Altium or Allegro?** Recent versions of Altium Designer can import KiCad projects directly (Import Wizard). Otherwise the schematic PDF and the netlist are complete enough to redraw from: every part, value, footprint and pin connection is in them and in `bom.csv`.
| [bom.csv](bom.csv) | Bill of materials: references, values and ratings, footprints, fitted or not, manufacturer and part number, what to confirm, notes |
| [PLACEMENT.md](PLACEMENT.md), [placement.py](placement.py) | Where each passive goes: priority, which pin, why (also the *Placement* column in bom.csv) |
| [outline.dxf](outline.dxf), [gen_outline.py](gen_outline.py) | Board outline: 100 × 80 mm, 4 × M3 holes 3.5 mm from the corners. 2 layers, 2 oz copper, 1.6 mm (CARRIER.md) |
| [mpn.py](mpn.py) | The proposed manufacturer part numbers, by reference (feeds bom.csv) |
| [checks.py](checks.py), [checks.txt](checks.txt) | Calculations: divider and current-sense ranges, supercap ride-through, AUX diode heat |
| [parts.py](parts.py) | **The source:** every part, footprint and pin-to-net connection, transcribed from CARRIER.md |
| [gen_schematic.py](gen_schematic.py), [gen_bom.py](gen_bom.py), [verify.py](verify.py), [build.sh](build.sh) | Regenerate everything with `./build.sh` |

**Drawing style (draft-2, wired).** Each block is drawn with wires: every capacitor and resistor sits beside the pin it serves and is wired to it (decoupling capacitors to the IC's supply pin, pull-ups to their line, the shunt with its two Kelvin wires to U2). +5V, +3V3 and GND are power symbols. Net labels are used only where a signal leaves its block (to the ESP32 socket, test points and headers). Draft-1 joined every pin by net label; the board designer asked for drawn wires to avoid misconnections between schematic and layout.

**To change the board before hand-over,** edit `parts.py` and run `./build.sh`; hand edits to `carrier.kicad_sch` would be overwritten. **From the hand-over to the board designer,** the KiCad schematic becomes the master and the generator scripts are retired (see CARRIER.md, *Hand-over of the schematic*).

## How it was checked

- **Connectivity:** `verify.py` reads the netlist KiCad itself exports and checks all **209 pin connections** against `parts.py`, net by net: each intended net must be exactly one KiCad net with the same pins. Result: 0 mismatches, no net with fewer than two pins. Nets drawn only with wires inside one block (e.g. SHUNT_TOP, GATE_IN) get KiCad's automatic names; their members are still checked. `gen_schematic.py` also refuses to write a sheet where a wire end or pin touches the middle of another wire, or two wires overlap.
- **Footprints:** all exist in KiCad's standard libraries.
- **Coverage:** every reference in CARRIER.md's part tables is present. The extras are parts the spec describes in its text rather than its tables (headers J9, J10, J11, J13; test points; mounting holes; the ESP32 sockets), plus three capacitors I added (below).
- **ERC (electrical rules check):** not yet run. KiCad 7's command line has no ERC; open the project in KiCad and run *Inspect → Electrical Rules Checker*. Power flags are placed on GND, +5V, +3V3, VBAT, PANEL+ and PV+.

## Choices made where the spec left room: please review

1. **ESP32 pin order: provisional.** The sockets follow the common 30-pin DOIT DevKit V1 layout (left: EN, 36, 39, 34, 35, 32, 33, 25, 26, 27, 14, 12, 13, GND, VIN; right: 23, 22, 1, 3, 21, 19, 18, 5, 17, 16, 4, 2, 15, GND, 3V3). **Confirm against a photo of both sides of the ELEGOO board**, together with the 25.4 mm row spacing, before layout.
2. **D0** is drawn as a dual common-cathode Schottky in D2PAK (TO-263) with both anodes on PANEL+, matching the "dual 20 A 100 V" example. A single diode in another package is fine; update the footprint.
3. **Q1** uses a DPAK (TO-252) footprint: gate pad 1, drain on the tab, source pad 3.
4. **Shunt RSH1** (spec R_SH) is a 2-pin 2512 resistor. The Kelvin connection to U2 is a **layout** rule: two thin traces from the inner ends of the pads.
5. **U1** uses KiCad's DS3231M symbol, which has the same 16-pin pinout as the DS3231SN. Pins 5–12 go to GND, as the DS3231SN datasheet requires. RST is left unconnected.
6. **U4 load switch:** AP22804AW5 (SOT-23-5), fed from +5V as the spec describes; its fault flag is not used. **Checked against the datasheet (review 2):** pin 1 OUT, 2 GND, 3 FLG, 4 EN, 5 IN; the "A" version is active-high; current limit 2.7–3.3 A; built-in soft start.
7. **Added, not in spec v1:** C11 (1 µF, U3 gate-driver supply decoupling, required by its datasheet), and C12 and C13 (1 µF, U4 input and output). Remove them if the reviewer disagrees.
13. **Added in review 2:** R21 (100 kΩ, Q1 gate to source), and D6 (SMCJ58A TVS on PV+, footprint only). Both are now also in CARRIER.md.
8. **D2** (SMAJ5.0A, unidirectional TVS) is drawn with a Zener symbol; **D3** (3.3 V ESD on the probe line) as a bidirectional TVS.
9. **High-current terminals J1 and J12** use a 10 mm-pitch footprint (MetzConnect Type 067) as a placeholder. The designer chooses an equivalent rated ≥ 15 A for 4–6 mm² wire.
10. **microSD J8:** Hirose DM3AT push-push socket. Its detect switch connects SD_CD to GND, and R17 pulls SD_CD up. Whether the switch closes or opens when a card is inserted depends on the socket: check the datasheet, and set the firmware's polarity to match.
11. **Header 3V3 pins** (J9, J10, J13) and J11's 3V3 come through F3 (net +3V3_EXT), as the spec says. The DS3231, probes and microSD use +3V3 directly.
12. **Test points TP10 and TP11** carry the DS3231's INT/SQW and 32K outputs, which the spec sends to test pads only.

## What the calculations show (`checks.txt`)

- **Panel voltage (GPIO 34):** R2 is now 4.7 kΩ (was 5.6 kΩ). The ESP32's analog input reads accurately up to about 2.45 V, which is now about 54 V of panel voltage: the 44.5 V open-circuit voltage gives 2.00 V, a cold-morning 48 V gives 2.15 V, and the board's 60 V rating gives 2.69 V, under the pin's 3.6 V absolute maximum. The 7 V dusk threshold still gives 0.31 V.
- **Sun current (GPIO 35):** 0.5 V per amp, reliable to about 4.9 A. A vertical panel peaks near 1.8 A (0.9 V), with plenty of margin. Only a tilted panel in full sun would exceed the reliable range.
- **Supercaps (5 F at 5 V):** about 45 seconds of ride-through at 0.5 W, as SUNDIAL.md states.
- **Shunt:** 0.18 W during each 1 ms pulse at 6 A, negligible on average.
- **AUX:** above about 2 A the diodes D0 and D5 need real cooling (6 W in D5 at 9 A).

## Review log

**Review 1 (20 Oct 2026), schematic PDF only.** Three points, all answered:

1. *Current-sense range too low for 15 A.* The sensor only sees the panel's own short-circuit current: 5.40 A on the label, about 6 A at most. 15 A is the terminal and wire rating. Gain 100 is deliberate for a vertical panel (about 1.8 A at noon). Saturation above about 6.6 A is harmless. **Change:** measurement ranges noted on the sheet.
2. *2 A fuse and 3 A diode on a 15 A input?* F1 and D1 are only in the board-supply branch (under 0.3 A), not in the measured current path; F1 sits after the Q1 node so short-circuit pulses never pass through it. **Change:** current-path note on the sheet.
3. *60 V gives 3.17 V at the divider: little margin.* 60 V is the board rating, not an expected voltage (Voc 44.5 V, about 48 V on a cold morning). It was still below the pin's 3.6 V maximum, but above the ADC's accurate range. **Change:** R2 5.6 kΩ → 4.7 kΩ; firmware `DIVIDER` updated (pva-fw-6.1.1).

**Review 2 (20 Oct 2026), GitHub Copilot on parts.py, README and checks.txt; it could not see CARRIER.md.**

1. *Critical: ESP32 boot/strap network missing.* Not applicable. The carrier takes a complete ELEGOO dev board, which has the EN pull-up, reset and boot buttons, USB-serial and strapping resistors. EN and GPIO 0, 2, 12, 15 are deliberately not brought out; GPIO 5 is held high by R14. **Change:** note on the sheet.
2. *Critical: AP22804AW5 pinout unchecked.* Checked against the datasheet: pinout as wired, active-high enable, 2.7–3.3 A current limit, soft start. **No change.**
3. *Critical: AUX at 9 A is thermally marginal.* Agreed: about 6 W in D5 and 4.5 W in D0. **Change:** AUX limited to a 3 A fuse on v1; 9 A only with D5 on a heatsink and D0's copper checked (CARRIER.md F4, parts.py, sheet note).
4. *Should fix: no gate pull-down at Q1.* Agreed, and more than a robustness point: at dawn U3 is unpowered (no 5 V yet), its output floats, and the rising panel voltage can couple through Q1's drain-gate capacitance and turn Q1 partly on, shorting the panel before the board can start. **Change:** R21 100 kΩ gate to source.
5. *Should fix: transients at the panel front end.* Partly agreed. When Q1 switches off, the panel lead's inductance can push PV+ above Voc. The energy is small (about 36 µJ for 2 µH at 6 A) and the buck's input capacitors should absorb it through F1 and D1, but it should be measured. **Change:** D6 TVS footprint (fit if needed; then Q1 ≥ 100 V), and a PV+ overshoot check added to the bench test.
6. *Should fix: U4 depends on boot timing.* As intended: R18 keeps the switched output off until firmware enables it; GPIO 27 is not a strapping pin. **No change.**
7. *Notes on the 60 V divider and INA180 margin:* covered by review 1. Above about 6.6 A the amplifier output clamps at its 3.3 V supply, which is harmless. **No change.**

**Rush PCB, 26 Oct 2026:** *several resistors and capacitors are assigned only to a power net name; which need to be placed near their components?* Answered in [PLACEMENT.md](PLACEMENT.md) and the BOM's *Placement* column. Connectivity was already complete (net labels; all pin connections checked); placement intent was missing from the drawing.

**Rush PCB, 26 Oct 2026:** *we need the schematic with drawn wires, to avoid misconnections between schematic and layout.* Done in draft-2: the sheet is regenerated in wired style (see *Drawing style* above), with the same netlist, checked pin by pin.

## Manufacturer review and sign-off

> **Sent to Rush PCB, 30 Oct 2026; acknowledged:** J9, J10 and J13 side by side along one board edge (J11 too if it fits), away from the antenna end (layout rule 9 in CARRIER.md). Also confirmed: 100 × 80 mm, 2 oz copper preferred, black mask, lead-free finish. Open: whether the layout is done directly in KiCad; fixed price and lead time.

This package (CARRIER.md, this folder, `bom.csv`, the KiCad project) goes to the design-and-build company for review before layout. Please confirm each point in writing.

**For the manufacturer**

1. **Parts:** `bom.csv` proposes a manufacturer and part number for every line. Please confirm them or list substitutions from your supplier, and settle the lines in the *Confirm* column (F1, Q1, C3, F3, J14/J15). Especially D0, Q1, RSH1, U2, U3, U4, J1 and J12 (≥ 15 A terminals), and the microSD socket J8.
2. **Q1 voltage rating:** quote one 60 V and one 100 V part (both logic-level, R_DS(on) ≤ 20 mΩ at V_GS 4.5 V, I_D ≥ 20 A). The 100 V part is needed if D6 is fitted after the bench test.
3. **Layout:** the layout rules in CARRIER.md, in particular the two high-current loops, the Kelvin connections from RSH1 to U2, the star ground, the copper for D0, and the ESP32 antenna keep-out.
4. **Manufacturability:** footprints, clearances (60 V on the panel side), board outline and mounting holes, and anything you would change to make the board easier or cheaper to build.
5. **Scope of your review:** please state whether it covers the circuit design itself, or manufacturability and parts only.

**Kept by PVA**

- The ESP32 pin order and row spacing (photo of the ELEGOO board), and the box size for the mounting holes: supplied before layout.
- The bench test of the v1 boards (CARRIER.md, "v1 bench test"), including the PV+ overshoot check that decides D6.

## Next steps

1. Confirm the ESP32 pin order and spacing, and the box size for the mounting holes.
2. Engineer review of this schematic.
3. Run ERC in KiCad and fix anything it finds.
4. Then layout: in KiCad, *Tools → Update PCB from Schematic*, or send the project or `carrier.net` to the layout service.
