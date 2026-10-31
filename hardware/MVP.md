# SUNDIAL wall — the MVP build (no custom board)

The simplest wall that makes the full SUNDIAL dial: **off-the-shelf modules on a screw-terminal breakout, no PCB to design, no soldering.** Any town can build it from this page.

> Status: draft 1, 31 Oct 2026. **The build to make first**, starting with the artist's proof. The carrier board ([CARRIER.md](CARRIER.md), [carrier/](carrier/README.md)) is **on hold**: kept, complete and quoted, for the day the module build proves too fragile outdoors or the walls need what only it offers.

---

## 1. What changes, and what doesn't

**The one change:** the sun is measured by a **small reference solar cell** on the panel's frame, not by shorting the big panel. That single change removes the whole custom sun-sensor circuit (MOSFET, gate driver, shunt, current amplifier, input diode, jumper), and with it the reason for a custom board.

### The dial stays the same

| Dial element | Built from | MVP |
| --- | --- | --- |
| **Sun ring:** 96 fifteen-minute solar sections, ochre for sun, blue for shade | Per section: sun if more than half the readings are above **one third** of the wall's clear-noon reading (rules-1) | **Same rule, same ring.** Each reading is compared with its own calibrated noon value, so the cell's scale cancels out |
| **Temperature line** | DS18B20 on the panel back | Same probe |
| **Visitor marks** per solar hour | Wi-Fi connections | Same |
| Day details: first and last sun, hours of sun, temperature range, visitors | The three daily files | Same |
| Panel voltage | Raw data only (not drawn) | Same, from the same divider |
| **Sole** (rules-2, modelled clear sun) | Calibrated sun readings | Same: the cell is calibrated against a clear noon, as the panel was |

**The daily sealed artifact is unchanged.** The only difference in meaning: the dial records **sun on the cell**, at one edge of the panel, rather than on the whole panel. On a clear wall they match. Where a shadow crosses the panel (a tree, a chimney, a balcony), a few sections at the edge of the shadow can differ. Placing the cell well (4.2) keeps this small.

## 2. Parts, per wall

| # | Part | Job | Notes |
| --- | --- | --- | --- |
| 1 | **Recycled PV panel** (Trina TSM-185DC01) | Power | Within the three compatibility limits (CARRIER.md, *Panel compatibility*): I_sc ≤ 5.5 A, V_oc ≤ 50 V, ≥ 20 W. The I_sc limit no longer applies to the MVP: the panel is not the sensor |
| 2 | **Inline MC4 fuse, 2 A** | Safety | On the panel's + lead. MC4 connectors are polarised, so the panel cannot be wired backwards |
| 3 | **Buck converter, 8–60 V in → 5 V** (ANGEEK module) | Power | **Set to exactly 5.0 V with a multimeter before connecting anything** |
| 4 | **ELEGOO ESP32 30-pin** (USB-C) | The wall | As before |
| 5 | **Screw-terminal breakout for the 30-pin ESP32** | Every wire in a screw terminal | Check it fits the ELEGOO's row spacing before buying nine |
| 6 | **DS3231 clock module + CR2032** | Time at dawn, offline | **Remove the charging part** on "ZS-042" modules (a diode and a 200 Ω resistor near the cell holder): they try to charge a CR2032, which is not rechargeable. Or buy a module without a charger |
| 7 | **Reference solar cell: a small "6 V" mini panel**, 0.5–1 W, monocrystalline, with leads | The sun sensor | A multi-cell 6 V type (not a single 0.5 V cell), so it stays near short circuit at the reading voltage (4.1) |
| 8 | **Cell resistor**, 1 %, ¼ W, value from 4.1 (about 5–10 Ω) | Turns the cell's current into a voltage | Across the cell's leads, at the terminals |
| 9 | **DS18B20 waterproof probe** + 4.7 kΩ pull-up | Panel temperature | As before |
| 10 | **Divider: 100 kΩ and 4.7 kΩ, 1 %**, + 100 nF | Panel voltage, and the dawn and dusk gates | As before (firmware DIVIDER unchanged) |
| 11 | **IP65 box** (about 115 × 90 × 55 mm), 3–4 cable glands, a breather vent, a desiccant pack | Housing | Smaller than the carrier's box |
| 12 | Wire ferrules, short wires, standoffs | Assembly | Ferrules on every stranded wire into a screw terminal |

**Optional, only if testing asks for them:** a 1000 µF / 10 V capacitor on the 5 V input (if Wi-Fi peaks cause resets); the two 10 F supercaps (if dusk brownouts misbehave).

**Rough cost** without the panel: about €50–60 per wall. Estimates, not quotes.

## 3. Wiring

```
panel + ── MC4 fuse 2 A ──┬── buck IN+        buck OUT+ (5.0 V) ── breakout 5V / VIN
panel − ──────────────────┼── buck IN−        buck OUT− ────────── breakout GND
                          │
                          └── 100 k ──┬── GPIO 34              (panel voltage)
                                     4.7 k ── GND
                                     100 nF ── GND

reference cell + ──┬── GPIO 35                                  (sun)
                   R_cell
reference cell − ──┴── GND

DS18B20: red 3V3 · black GND · yellow GPIO 4, 4.7 k from GPIO 4 to 3V3   (temperature)
DS3231:  VCC 3V3 · GND · SDA GPIO 21 · SCL GPIO 22                         (clock)
```

- **All grounds meet at the breakout's GND,** the panel's − included.
- **GPIO 34 and 35 must stay as they are:** they are on ADC1, the only analog inputs that work with Wi-Fi on.
- The divider's top resistor sits at panel voltage (up to about 48 V): keep its terminal apart from the 3.3 V side, and keep the panel leads away from the ESP32's antenna end.

## 4. The reference cell

### 4.1 Choosing the resistor

The cell is read **near short circuit**, where its current rises in proportion to the light. The resistor turns that current into a small voltage, well below the cell's working voltage (about 6 V), so the cell stays in its linear region.

- **R_cell = 1.0 V ÷ the cell's label I_sc.** For example: I_sc 180 mA → 5.6 Ω; I_sc 100 mA → 10 Ω.
- Full sun then gives about 1.0 V at GPIO 35. A vertical wall's clear noon gives less; the dial's threshold (a third of clear noon) stays well above 0.1 V.
- The firmware reads GPIO 35 at its **2.5 dB range** (about 0.1–1.25 V), where the ESP32 reads small voltages most accurately.
- Power in the resistor: under 0.2 W. A ¼ W resistor is enough.

### 4.2 Placing it

- **In the panel's plane,** facing the same way, fixed to the aluminium frame (bracket or bonded), not shading the panel.
- **At the edge most like the panel's average light.** Where shadows cross the wall, at the side the shadow reaches first or last, as the artist's proof shows.
- Its lead enters the box through its own gland, with a drip loop.
- Clean it when the panel is cleaned.

## 5. Firmware changes

Small, and in one place: `readSunI()` and the build flags.

| Change | Now | MVP |
| --- | --- | --- |
| Build flags | `SUN_SENSE 1` (MOSFET pulse) | New `SUN_CELL 1`: `PANEL_SENSE 1`, `USE_RTC 1`, `SUN_SENSE 0` |
| Sun reading | Pulse GPIO 25 high, read GPIO 35, divide by `SHUNT_OHM × SENSE_GAIN` | Read GPIO 35 (analogReadMilliVolts, averaged), divide by `R_CELL`: the cell's current in amps. No pulse, no GPIO 25 |
| ADC range | 11 dB | `analogSetPinAttenuation(35, ADC_2_5db)` at start-up |
| Constants | `SHUNT_OHM`, `SENSE_GAIN` | `R_CELL` (per the resistor fitted) |
| Calibration | Admin page, *Calibrate*, on a clear noon | **Unchanged**: same button, same rule; it now calibrates the cell |
| Dawn and dusk gates | Panel voltage (divider) | Unchanged |
| Rules | rules-1, rules-2 | Unchanged |

Readings are now **continuous and silent**: no 1 ms short of the panel every 10 s. They can be taken as often as the firmware likes.

## 6. Build and test

1. **Bench, USB only:** ESP32 on the breakout, clock and probe; set the clock from the admin page; the page and the temperature work.
2. **Bench, the cell:** cell and resistor on GPIO 35, outdoors in sun and shade; the reading follows the light; full sun about 1 V.
3. **Panel day:** buck set to 5.0 V first, then the panel, fuse and divider; check the divider's reading against a multimeter on the panel; the wall wakes at dawn and seals at dusk.
4. **Calibrate** on a clear day near solar noon, then let the dial run for a week. Compare with the sky.
5. **The artist's proof outdoors through a winter:** terminals, damp (desiccant), heat in summer. Check every terminal at each seasonal visit.

## 7. What the MVP gives up (against the carrier)

| Carrier v1 | MVP |
| --- | --- |
| The panel itself is the sensor | A reference cell on its frame (1) |
| One soldered board | Modules and screw terminals: more connections to check |
| Protection on board (TVS, input diode, fuses) | The inline fuse and MC4 polarity; nothing else |
| AUX output, switched 5 V, spare headers, microSD | None. A garden node or an add-on takes its power from the panel through its own converter. The SUNSET I/O board connects to the breakout's pins instead of the carrier's headers |
| A designed and quoted board | Nothing to design: parts from a list |
