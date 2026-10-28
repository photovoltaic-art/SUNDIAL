# PVA carrier board — specification v1

One small board per panel. It carries everything except the ESP32 and the buck converter, which plug in or wire on.
Every part on the board is fitted by the board maker; the builder only plugs in, screws down and fits a coin cell.

> Status: specification for the board designer. The **schematic is already drawn**: a KiCad project generated from this document and reviewed twice is in [carrier/](carrier/README.md) (start there), with PDF, netlist and BOM. What remains is the manufacturer's review, part selection, layout and build.
>
> v1 is also the bench test of the sun sensor,
> so it carries test points and options. Order 5 for v1; fix, then order 10 of v2.

## What the board does

The board sits in a weatherproof box behind a recycled 185 W solar panel mounted **vertically on an outdoor wall** (or on a free-standing post: [POST.md](POST.md)). It is the panel's only load, and it has **no battery and no mains supply**: it lives entirely on the panel's own power.

**Its job is to measure the panel and serve the results over Wi-Fi.** A plugged-in ESP32 dev board runs its own Wi-Fi access point (no internet), and visitors' phones read web pages from it. Behind those pages it records:

- **Sunlight on the panel**, from the panel's **short-circuit current**. Every 10 seconds a MOSFET (Q1) shorts the panel for about 1 ms; the current through a 5 mΩ shunt is amplified by an INA180 and read by the ESP32. Short-circuit current is proportional to the light falling on the panel, so this is the board's light meter. It is why the board has a high-current path at all.
- **Panel voltage**, through a resistor divider, used to decide when there is enough light to start Wi-Fi (dawn) and when to stop (dusk).
- **Panel temperature**, from a DS18B20 probe on the back of the panel.
- **The time**, kept through the night by a DS3231 clock with a coin cell, because the rest of the board loses power every evening.

**A day in the life:**

1. At night the board is completely off.
2. At dawn the panel voltage rises, the buck converter starts and charges two supercapacitors on the 5 V rail, and the ESP32 boots with its radio off.
3. Once the panel holds about 12 V for a minute, Wi-Fi starts and the board measures and logs all day.
4. At dusk the voltage falls and the board shuts down, with the supercapacitors riding through brief dips (clouds, the 1 ms short-circuit pulses) but not the night.

**What this means for the design:**

- **The board browns out every evening and starts cold every morning,** on a slowly rising, current-limited supply. Start-up and shut-down must be clean, with no part left half-on (see R21, the gate pull-down on Q1).
- **The board's own consumption is under 1 W** from a panel that can give 50–60 W, so the panel is effectively unloaded. The only large currents are the 1 ms short-circuit pulses (up to about 6 A) and, optionally, the AUX output for a future add-on.
- **Wi-Fi is the only interface:** there is no screen or button on the installed object. Antenna placement and keep-out matter more than usual.
- **Outdoors, in a closed box behind a panel in a Sardinian summer:** expect high box temperatures; it affects the supercapacitors most.
- **Panel side up to 60 V** (open-circuit 44.5 V on the label, about 48 V on a cold morning).


## Brief for the board designer

**The job:** starting from the existing schematic in [carrier/](carrier/README.md), review it against this document, choose the parts,
lay out the board in KiCad (version 8 or later; the project is in KiCad 7 format and opens in 8) and build it, for manufacture and
assembly by the chosen maker (an Italian/European assembler, or JLCPCB/PCBWay).
It is a two-layer board of moderate density; the only demanding parts are the two high-current paths and the antenna keep-out.
Please confirm the points in [Manufacturer review and sign-off](carrier/README.md#manufacturer-review-and-sign-off) before layout.

**Hand-over of the schematic:** up to now the schematic has been generated from `carrier/parts.py` by a script. From the hand-over,
**the KiCad schematic becomes the master**: edit it directly in KiCad, and the generator scripts are retired. Any change you make to
the circuit is listed in your BOM notes and shown in the updated schematic PDF.

**Deliverables**

1. KiCad project: the existing schematic, with any corrections, plus the board layout, in a shareable archive.
2. Schematic as PDF (updated).
3. BOM with manufacturer part numbers (and the assembler's own stock codes where it has them), all confirmed in stock.
4. Pick-and-place (CPL) file and Gerbers in the assembler's format, plus a 3D render of the assembled board, top and bottom.
5. A clean design-rule check (DRC) and the assembler's manufacturability check passed.
6. **All native design files handed over to the client**, so a v2 can be made anywhere.

**Your choices:** where a part is given as a "class" (for example "S3M class", "TC4427A / MCP1416 class"), choose an equivalent
that the assembler can source, meeting the ratings in the table. List any substitution in the BOM.

**Provisional, to confirm before ordering**

- ESP32 socket row spacing 25.4 mm (from the listing; the client confirms on a delivered board).
- **Board outline (fixed 27 Oct 2026): 100 × 80 mm, 1.6 mm FR-4, 4 × M3 holes (3.2 mm drill) 3.5 mm in from each corner: [carrier/outline.dxf](carrier/outline.dxf).** The board mounts on standoffs on the box's removable mounting plate, so the box does not constrain the hole pattern. The only change allowed to the outline is a slot or notch under the ESP32 antenna (see the antenna keep-out).
- ESP32 pin order: from the ELEGOO 30-pin (USB-C) pinout; the client sends a photo of both sides of a delivered board.

**Review:** before layout, the manufacturer confirms the sign-off points in carrier/README.md. Before anything is ordered,
the client checks the updated schematic PDF, BOM and 3D render against this document. Expect one round of corrections.

**Order quantity:** v1, 5 boards, fully assembled (SMD and through-hole).

## The panel (from its label)

Trina Solar TSM-185DC01: P_max 185 W, V_mp 37.5 V, I_mp 4.95 A, **V_oc 44.5 V, I_sc 5.40 A**, NOCT 47 ± 2 °C,
maximum series fuse 9 A, 1581 × 809 × 40 mm, 15.6 kg. Field wiring at least 4 mm² copper.

## Panel compatibility: three parameters

**As specified (U2 = INA180A3), the carrier suits panels with a label short-circuit current (I_sc) of about 1–5.5 A and an open-circuit voltage (V_oc) up to about 50 V, from about 20 W upwards.**

In practice: 12 V panels (36 cells) of about 20–90 W, and older 24 V panels (60–72 cells) up to about 200 W, such as the Trina 185 W above.

Checking a used panel, from its label:

| Parameter | Limit (as built) | Why |
| --- | --- | --- |
| **I_sc** | ≤ 5.5 A | The sun sensor reads up to about 4.9 A at gain 100; a vertical panel stays below about 85 % of its label I_sc. Higher I_sc: change U2 (below) |
| **V_oc** | ≤ 50 V | Leaves room for cold mornings (about +8 %) within the board's 60 V rating and the panel-voltage reading's 54 V limit |
| **P_max** | ≥ 20 W | The board uses up to about 1 W with Wi-Fi on; smaller panels wake late, sleep early and drop out under cloud |

**Panels with a higher I_sc** (100 W 12 V panels, modern 300–450 W panels) need a different U2. Same footprint and pins; only the firmware's `SENSE_GAIN` changes:

| U2 | Gain (`SENSE_GAIN`) | Reads up to | Unreliable below | Label I_sc |
| --- | --- | --- | --- | --- |
| **INA180A3** (as specified) | 100 | about 4.9 A | about 0.3 A | 1–5.5 A |
| INA180A2 | 50 | about 9.8 A | about 0.6 A | 5–10 A |
| INA180A1 | 20 | about 24 A | about 1.5 A | 9–20 A |

The floor comes from the ESP32's analog input, which cannot read the bottom ~0.15 V reliably. Use one panel model for all nine panels of a work, so every panel reads alike; record the U2 fitted on each build.

## Decisions

| Decision | Choice |
| --- | --- |
| Schematic | Drawn: KiCad project in [carrier/](carrier/README.md), generated from this document and reviewed twice (review log in carrier/README.md) |
| Layout and build | The chosen maker (design-and-build), or a KiCad designer plus a maker |
| ESP32 | ELEGOO ESP32 30-pin (USB-C) dev board, **plugged into two 1 × 15 female header sockets** (removable) |
| Buck converter | ANGEEK 8–60 V module, **beside the board**, joined by 4 short wires (screw terminal to screw terminal) |
| Clock | DS3231 chip **on the board**, CR2032 holder, **no charging circuit** |
| Supercapacitors | Two 2.7 V 10 F radial cells (10 × 25 mm, 5 mm lead pitch), **in screw terminals**, fitted by the builder |
| Enclosure | Standard IP65 plastic junction box, about 150 × 110 × 70 mm: 2 glands for the panel leads, 1 for the probe, a breather vent; 2 more glands later if AUX is used |
| Board | 2 layers, **2 oz copper** (1 oz acceptable if the designer widens the high-current paths and pours copper; say which), 100 × 80 mm, 1.6 mm thick ([outline.dxf](carrier/outline.dxf)), 4 × M3 mounting holes, black solder mask, white silkscreen |
| Maker | An Italian/European design-and-assembly house (first choice), or JLCPCB/PCBWay; SMD + through-hole assembly for the terminals |

## Block diagram

```
 panel + ── D0 ──┬──────── F1 2 A ──┬── D1 ──► J2 BUCK IN +      J3 BUCK OUT + ──► 5V rail ──► ESP32 VIN
                 │                   │                                              │
                 ├─ F4 ─ D5 ─► AUX   R1/R2 divider ─► GPIO 34               J6+J7 supercaps (series)
                 │
                 Q1 sun MOSFET
           │                         │                                       TVS, 470 µF, LED
                 R_SH 5 mΩ ─► INA180 ─► GPIO 35
                 │
 panel − ────────┴────── GND ──────────────────────► J2 BUCK IN −      J3 BUCK OUT − ──► GND

 ESP32 3V3 ──► 3V3 rail ──► DS3231 + CR2032, DS18B20 terminals (GPIO 4), INA180 supply, I2C header
 GPIO 25 ──► jumper JP1 ──► gate driver U3 (from 5 V) ──► Q1 gate
```

**Important: the sun MOSFET sits across the panel, after the input diode D0 but before the fuse.** The panel is a current source:
its short-circuit current (5.40 A on the label; up to about 6 A in strong cold sun) is safe to short for a millisecond, but it must not flow
through a small fuse every 10 seconds. The fuse protects only the board side, so it can be small.

## Circuit, section by section

### 1. Panel input and sun sensor

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| J1 | Screw terminal, 2-way, high current | ≥ 15 A, accepts 4–6 mm² (or ferrules), 7.62–10 mm pitch | Board edge; labelled `PANEL +` `PANEL −` |
| D0 | Schottky diode, input protection | ≥ 100 V, ≥ 15 A, TO-220 or D2PAK (e.g. dual 20 A 100 V) | In `PANEL +`, straight after J1. **Protects Q1:** without it, a panel connected backwards would push its full short-circuit current through Q1's internal diode continuously and overheat it. Its ~0.5 V drop does not change the short-circuit reading. With AUX in use, D0 carries the AUX current too: size its cooling to that load |
| Q1 | N-MOSFET | V_DS ≥ 60 V (≥ 100 V preferred if D6 is fitted, see below), I_D ≥ 20 A, R_DS(on) ≤ 20 mΩ at V_GS 4.5 V, DPAK/D2PAK or PowerPAK | Drain on the D0 cathode node (`PV+`), source on R_SH top |
| R_SH | Shunt resistor | 5 mΩ, 1 %, 2512, ≥ 2 W | Between Q1 source and GND |
| R_SH2 | Footprint only | 2512, parallel to R_SH | Option: two 10 mΩ in parallel instead of one 5 mΩ. **Always fit both or neither:** the firmware assumes 5 mΩ in total (0.5 V/A); one 10 mΩ alone would double every current reading |
| U2 | Current-sense amplifier **INA180A3** | Gain 100 V/V, SOT-23-5 | Supply 3V3 (output then can never exceed 3.3 V); IN+ to R_SH top, IN− to R_SH bottom by **Kelvin traces** |
| C6 | Capacitor | 100 nF, 0603 | U2 supply decoupling |
| R6, C7 | RC on U2 output | 1 kΩ + 10 nF | Light filter into GPIO 35; time constant 10 µs, well inside the 400 µs settle |
| U3 | Low-side gate driver, non-inverting | Supply 4.5–18 V, input threshold works from 3.3 V (TC4427A / MCP1416 class), SOT-23-5 or SOIC-8 | Powered from 5V rail, so Q1 gets 5 V gate drive |
| R4 | Gate resistor | 10 Ω, 0603 | U3 output to Q1 gate |
| R5 | Pull-down | 10 kΩ, 0603 | U3 input to GND: Q1 stays off while the ESP32 boots |
| R21 | Gate pull-down | 100 kΩ, 0603 | Q1 gate to source (`SHUNT_TOP`), at Q1. Added in review 2: before the 5 V rail exists (dawn), U3 is unpowered and its output floats; without R21 the rising panel voltage could couple through Q1's drain-gate capacitance and turn Q1 partly on, shorting the panel before the board can start |
| D6 | TVS, footprint only (fit after the bench test if needed) | SMCJ58A class (stand-off 58 V), SMC | `PV+` to GND. Added in review 2: when Q1 switches off, the panel lead's inductance can kick `PV+` above V_oc. The buck's input capacitors (through F1 and D1) should absorb this; the v1 bench test checks it on the oscilloscope. If D6 is fitted, Q1 must be ≥ 100 V, because the TVS clamps at about 90 V |
| JP1 | 2-pin header + jumper | | GPIO 25 to U3 input. **Remove the jumper to disable the sun sensor** |

Scale: 0.5 V per amp at GPIO 35 (`SHUNT_OHM 0.005`, `SENSE_GAIN 100`). The panel (Trina TSM-185DC01) has I_sc 5.40 A, so full sun on a tilted panel would give 2.7 V, inside the ESP32's range. **Why gain 100, not 20:** mounted vertically, the clear-noon current is only about a third of I_sc (≈ 1.8 A → 0.9 V), and the sun threshold is a third of that (≈ 0.6 A → 0.3 V). With gain 20 these would sit at 0.04–0.2 V, where the ESP32's analog input reads poorly or not at all.

### 2. Board side of the panel: fuse, diode, divider

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| F1 | Fuse | 2 A slow-blow, 1812 SMD or 5 × 20 mm holder | After the Q1 node, before D1. 2 A, not 1 A: on the first morning the empty supercaps make the buck draw a brief surge |
| D1 | Rectifier diode | 1000 V 3 A, SMC (S3M class) | Reverse-polarity protection; stops Q1 pulses draining the buck's input capacitor |
| J2 | Screw terminal, 2-way | 5.0 mm pitch, ≥ 5 A | `BUCK IN +` (after D1), `BUCK IN −` (GND) |
| R1 | Resistor | 100 kΩ, 1 %, 0805 | From F1/D1 node |
| R2 | Resistor | 4.7 kΩ, 1 %, 0603 | To GND (was 5.6 kΩ: changed after review so a cold-morning 48 V stays inside the ADC's accurate range) |
| C5 | Capacitor | 100 nF, 0603 | Across R2; divider to GPIO 34 (45 V → 2.0 V, 48 V → 2.15 V, 60 V → 2.7 V; the ESP32 reads accurately to about 2.45 V, i.e. 54 V) |

### 3. 5 V rail

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| J3 | Screw terminal, 2-way | 5.0 mm pitch | `BUCK OUT +` `BUCK OUT −`, from the buck set to 5.0 V |
| J6, J7 | Screw terminals, 2-way | 5.0 mm pitch | One per supercap cell, in series: J6 from 5V to MID, J7 from MID to GND. Silkscreen the **−** side (stripe) |
| R7, R8 | Balancing resistors | 10 kΩ, 0805 | One across each cell |
| D2 | TVS | 5.0 V standoff (SMAJ5.0A) | Across 5V rail |
| C3 | Electrolytic or polymer | 470 µF, 10 V, low ESR | Across 5V rail, close to ESP32 VIN |
| C4 | Capacitor | 100 nF, 0603 | Across 5V rail |
| LED1, R9 | Green LED + resistor | 10 kΩ (about 0.3 mA) | "5 V present"; dim on purpose |

### 4. ESP32 socket

Two 1 × 15 female headers, 2.54 mm pitch. **Row spacing: 25.4 mm (1.0 in) centre to centre, provisional.** The listing
gives 25.64 mm, which on a 2.54 mm grid is the 1.0 in (10-pitch) wide variant. Confirm on a delivered board before
the design is sent for manufacture. Pin positions from the ELEGOO 30-pin pinout.

| ESP32 pin | Net |
| --- | --- |
| VIN (5V) | 5V rail |
| GND (both) | GND |
| 3V3 | 3V3 rail (the dev board's own regulator feeds the board's 3.3 V parts) |
| GPIO 4 | DS18B20 data |
| GPIO 21 / 22 | I2C SDA / SCL (DS3231, expansion header) |
| GPIO 25 | Sun MOSFET gate (via JP1 and U3) |
| GPIO 34 | Panel voltage divider |
| GPIO 35 | Sun current (INA180 output) |
| GPIO 5 / 18 / 19 / 23 | microSD: CS / SCK / MISO / MOSI (VSPI) |
| GPIO 39 | microSD card-detect (input only) |
| GPIO 26 / 27 / 32 / 33 / 36 / 13 / 14 | Spare-pins header J9 (32, 33 and 36 are ADC1, usable with Wi-Fi on; 36 is input only) |
| GPIO 16 / 17 | UART header J10 (RX2 / TX2) |
| Not brought out | GPIO 1 / 3 (USB serial), 2 / 12 / 15 (boot strapping pins; 2 also drives the dev board's LED) |

**Antenna keep-out (important: Wi-Fi is the whole visitor experience).** The ESP32 module's printed antenna sits at the
end of the dev board, past the last pins. Under that area, on **both layers**: no copper pour, no traces, no parts.
Best: place the socket so the antenna end **overhangs the board edge**, or cut a slot in the board outline under it.
The dev board sits about 8–10 mm above the carrier on its sockets, which helps, but the rule still applies.
The USB-C socket must stay reachable for programming with the board in the box.

### 5. Clock

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| U1 | RTC DS3231SN (SOIC-16W) | | V_CC 3V3; INT/SQW and 32K to test pads only |
| BT1 | CR2032 holder, SMD | | V_BAT. **No charging resistor or diode** |
| C10 | Capacitor | 100 nF, 0603 | U1 decoupling |
| R10, R11 | I2C pull-ups | 4.7 kΩ, 0603 | SDA, SCL to 3V3 |

If the DS3231SN is not in stock at the maker, an RV-3028-C7 is a drop-in alternative in function (needs a firmware library change).

### 6. Temperature probes

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| J4, J5 | Screw terminals, 3-way | 3.5 mm pitch | Wired in parallel: `3V3` `DATA` `GND` (red, yellow, black). J5 is for an optional second probe |
| R12 | Pull-up | 4.7 kΩ, 0603 | DATA to 3V3, next to J4 |
| R12b | Footprint only | 0603 | Second pull-up value, if a longer cable needs a stronger pull-up |
| R13 | Series resistor | 100 Ω, 0603 | DATA to GPIO 4 |
| D3 | ESD diode | 3.3 V, SOD-323 | DATA to GND, at the terminal |

### 7. microSD card (future-proofing)

Not used by firmware draft 6; fitted now so that raw data and future media layers can outgrow the ESP32's 2 MB.

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| J8 | microSD socket, push-push, with card-detect switch | | SPI mode on the VSPI pins |
| R14–R17 | Pull-ups | 10 kΩ, 0603 | On CS (GPIO 5), MOSI, MISO and card-detect (GPIO 39), to 3V3. The CS pull-up also keeps GPIO 5 high at boot, as a strapping pin should be |
| C8, C9 | Capacitors | 10 µF + 100 nF | At the socket's 3V3 pin |

Place J8 at a board edge where a card can be inserted with the board in the box. Any card from 1 to 32 GB, FAT32.
A card draws up to about 100 mA from 3V3 while writing; together with the ESP32's own peaks this is within the dev board's regulator, but leaves less for 3.3 V add-ons.

### 8. Expansion and test

- **I2C header J13:** 4-pin, 2.54 mm: 3V3, GND, SDA, SCL (for future I2C sensors, e.g. a BME280).

- **Spare-pins header J9:** 9-pin, 2.54 mm: 3V3, GND, GPIO 32, 33, 36, 26, 27, 13, 14. Silkscreen each pin; note "32/33/36 analog, 36 input only".

- **UART header J10:** 4-pin, 2.54 mm: 3V3, GND, GPIO 16 (RX), GPIO 17 (TX), for a future serial device.

- **AUX power out J12:** spare panel power for future add-ons (see section 10).

- **Power take-off J11:** 4-way screw terminal, 3.5 mm pitch: `5V`, `5V SW`, `3V3`, `GND`, for future add-ons (see section 9).

- Every usable ESP32 pin is then either in use or on a header. The ones left off are reserved for programming (1, 3) or decide how the chip starts (2, 12, 15), and connecting things to them can stop the board booting.
- **Test points** (loops or pads, labelled): `PV+`, `BUCK IN`, `5V`, `MID` (between the supercaps), `3V3`, `GND`, `VDIV` (GPIO 34), `ISENSE` (GPIO 35), `GATE` (Q1 gate).

- **Silkscreen:** "PVA carrier v1", the net name at every terminal, the supercap polarity, and "JP1: remove = sun sensor off".

### 9. Power take-off for future add-ons

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| F2 | Resettable fuse (PTC) | 0.5 A hold, 1206 | 5V rail to J11 `5V`: a faulty add-on cannot drag down the panel's own board |
| F3 | Resettable fuse (PTC) | 0.2 A hold, 0805 | 3V3 rail to J11 `3V3` and to the header 3V3 pins |
| U4 | Load switch, 5 V, ≥ 1 A, active-high enable, with soft start (TPS22918 / AP22802 class) | | 5V rail to J11 `5V SW` |
| R18 | Pull-down | 100 kΩ, 0603 | U4 enable to GND: switched output off at boot |
| R19 | 0 Ω link | 0603 | GPIO 27 to U4 enable. Fitted by default; remove to free GPIO 27 |
| D4 | Schottky diode, 1 A (SS14 class), SMA | | Cathode to `5V SW`, anode to GND: flyback clamp, so a bare 5 V relay coil can be driven straight from `5V SW` |

- **A 5 V relay:** either wire a bare 5 V relay coil to `5V SW` and `GND` (D4 absorbs the coil's switch-off kick), or use a relay module powered from `5V` with its input on a spare GPIO (choose a module that triggers from a 3.3 V signal). A typical coil draws 70–90 mA while on; a latching relay draws only during its switching pulse.

- `5V SW` lets a future firmware power an add-on only when wanted (after the dawn gate, or only during the day), so it never competes with the board at the weak ends of the day.
- The 3.3 V comes from the ESP32 dev board's own regulator, which has only about 200 mA to spare: keep 3.3 V add-ons to small sensors. Anything bigger runs from `5V` or `5V SW`.
- Every milliamp taken shortens the supercaps' ride-through in the same proportion. A load of more than about 1 A belongs on its own supply, not on this board.

### 10. AUX power out, for spare panel capacity

The board itself uses well under 1 W; a vertical panel in June gives roughly 50–60 W at noon. AUX lets a future
add-on use that spare power through its own converter, switched by the relay output, without touching the board's supply.

| Ref | Part | Value / rating | Notes |
| --- | --- | --- | --- |
| J12 | Screw terminal, 2-way, high current | ≥ 15 A, 4–6 mm² | `AUX +`, `AUX −`. Board edge, beside J1 |
| F4 | Fuse holder, blade (ATO) or 5 × 20 mm | fuse up to **3 A on v1**; up to 9 A (the panel's maximum series fuse) only with D5 on a heatsink and D0's copper checked (review 2: at 9 A, D5 dissipates about 6 W and D0 about 4.5 W) | **Fuse not fitted**: the builder fits one sized to the add-on. Empty holder = AUX dead |
| D5 | Schottky diode | ≥ 100 V, ≥ 10 A (TO-220 or D2PAK, e.g. MBR10100 class) | In `AUX +`, cathode towards J12 |

- `AUX +` is taken from `PV+` (after D0, **before F1**, the same node as Q1's drain), then through F4 and D5. `AUX −` is `PANEL −`, so AUX current never passes through the shunt.

- **D5 is essential:** every 10 s Q1 shorts the panel for about 1 ms. Without D5, the add-on converter's input capacitors would discharge into Q1, spoiling the sun reading and stressing Q1. With D5, the add-on simply rides through the pulse on its own capacitors.

- The add-on's converter is switched by the relay on `5V SW` (its input or its enable pin). The firmware is to switch it on only in strong sun and shed it the moment the panel voltage sags, so the artwork always has priority.
- Copper: treat J1 → D0 → F4 → D5 → J12 as a high-current path, like the sun loop.

## Layout rules for the designer

1. **Two high-current paths:** the sun loop J1 → D0 → Q1 → R_SH → `PANEL −`, and the AUX path D0 → F4 → D5 → J12. Keep both short and wide (copper pour, ≥ 3 mm on 2 oz), with J1, D0, Q1 and R_SH close together. Give D0 copper area for cooling.
2. **Kelvin connections:** U2's inputs run as two thin, parallel traces from the inner ends of R_SH's pads; U2 sits right next to R_SH.
3. **Star ground** at R_SH's ground end: the sun loop returns there; signal ground joins there, not through the loop.
4. **Gate:** U3 next to Q1, gate trace short.
5. **Edges:** J1 (panel) and J4/J5 (probe) on one edge, towards the cable glands; J2/J3 towards the buck module; ESP32 antenna at the opposite edge, overhanging or over a cut-out, USB-C reachable.
8. **In the box:** mount the box at the panel's edge with the antenna end pointing away from the panel (the aluminium frame and the cells shield the signal), and keep the buck module and cables away from the antenna end. Check the Wi-Fi range on the pilot from where visitors will stand.
6. **Spacing:** panel V_oc 44.5 V (about 48 V on a cold morning), board rated to 60 V; normal 0.5 mm clearances are plenty.
7. **Mounting:** 4 × M3 holes for standoffs in the box; keep 3 mm clear round them.
9. **Headers together (added 28 Oct 2026):** place **J9, J10 and J13 side by side along one board edge**, with J11 beside them if it fits, away from the ESP32 antenna end. On SUNSET's interactive nodes three short cables run from these headers to an I/O board beside the carrier (SUNSET repository, io-board.md). A placement preference only: no circuit change.

## Parts the builder fits (no soldering)

| Part | Per board |
| --- | --- |
| ELEGOO ESP32 30-pin | 1, plugged into the sockets |
| ANGEEK buck converter, set to exactly 5.0 V first | 1, wired to J2 and J3 |
| 2.7 V 10 F supercap | 2, into J6 and J7, stripe to **−** |
| CR2032 | 1 |
| DS18B20 probe | 1 (2 optional), into J4 (J5) |
| Jumper on JP1 | 1, once the sun sensor is to be used |
| AUX fuse in F4 | only when an add-on is connected, sized to it |
| microSD card | optional, 1–32 GB, FAT32 |

## Firmware

Firmware 6.1.1 matches: pins GPIO 4/21/22/25/34/35, `SHUNT_OHM 0.005`, `SENSE_GAIN 100`, `DIVIDER (100 + 4.7) / 4.7`.
The gate driver is non-inverting, so GPIO 25 high still means "short the panel".
The microSD socket and the spare pins are unused until a later firmware adds them; nothing on them affects boot.

**Expansion is limited by power, not pins:** there is no battery, so any future sensor should draw no more than a few milliamps.

## v1 bench test, before ordering v2

1. **Jumper JP1 off.** Power the board from a 12–24 V bench supply into J1, with the buck connected: check 5V, `MID` (about half of 5V), 3V3, the LED, the clock (set from the admin page, unplug, plug back in) and the probe. Reverse the supply leads briefly: nothing should happen.
2. Connect a real panel, jumper JP1 off: check `VDIV` against a multimeter on the panel voltage.
3. Jumper on, clear sun near noon: check `PV+` on the oscilloscope at Q1 turn-off for an overshoot above V_oc (decides whether D6 is fitted, review 2). **Pass:** peak below 70 V (30 % margin on a 100 V Q1); D6 stays unfitted. **Above 70 V:** fit D6 and measure again; the peak must then stay below 80 V, otherwise choose a 150 V Q1. Check `ISENSE` on an oscilloscope or by the firmware's `isc` reading against a multimeter's short-circuit current reading of the same panel.
4. Run a full day with `BENCH 0`, then fix anything in v2.

## Planned for v2 (not in v1)

v1 stays as specified: it suits the panels in hand (Trina 185 W) and the many like them for sale in Italy. Changes noted here go into v2, after the v1 bench test.

1. **Dual-gain sun sensor, for any panel from about 20 W to 450 W+** (noted 28 Oct 2026).
   - Add **U2B, an INA180A1 (gain 20)**, on the same shunt as U2 (INA180A3, gain 100): its IN+ and IN− from the same Kelvin points, its own 1 kΩ / 10 nF filter, output to **GPIO 36** (ADC1, readable with Wi-Fi on; taken from the spare header, leaving GPIO 32 and 33 spare).
   - Firmware reads both and uses U2 up to about 4.5 A, U2B above; between 1.5 and 4.5 A both are valid and cross-check each other.
   - Result: label I_sc from about 1 A to 20 A on one board, with no part to choose and no setting to change. Panel compatibility drops from three parameters to two (V_oc ≤ 50 V, P_max ≥ 20 W).
   - Cost: one SOT-23 part, one resistor, two capacitors; no change to the board outline.
   - Not a socket or plug-in: a socket for a SOT-23 is unreliable outdoors, and a connector in the millivolt sense path invites trouble.
