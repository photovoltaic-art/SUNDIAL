# Carrier board v1 — where each part goes

*Added 26 Oct 2026, answering the manufacturer's question: the schematic joins parts by net name, so it does not show which capacitor or resistor belongs next to which part.*

**Connectivity is complete.** Every pin connection is in the schematic and the netlist, checked by `verify.py` (205 pin connections, 0 mismatches). A part tied to `+5V`, `+3V3` or `GND` is connected to that whole net; what the drawing does not show is **where it should sit**. This page says, part by part. The same information is in the *Placement* column of [bom.csv](bom.csv), from [placement.py](placement.py).

**Priority:** **critical** = within a few mm, short direct traces to the named pins · **near** = same area, short trace · **free** = anywhere sensible.

## Critical

| Part | Place at | Why |
| --- | --- | --- |
| C6 100 nF | U2 pin 5 (VS) to U2 pin 2 (GND) | U2 supply decoupling |
| C7 10 nF | J14 pin 5 (ESP32 GPIO 35) to GND, with R6 | Filter on the sun-current reading, at the ADC input |
| C11 1 µF | U3 pin 2 (VDD) to U3 pin 4 (GND) | Supplies the gate-driver current pulses |
| R4 10 Ω | Q1 gate, between U3 pin 5 (OUT) and Q1 gate | Keep the U3 → R4 → Q1 gate loop short |
| R21 100 kΩ | Directly across Q1 gate and source pads | Holds Q1 off at dawn |
| D0 | Right after J1, in the sun loop J1 → D0 → Q1 → RSH1 | High current; copper area for cooling |
| C5 100 nF | J14 pin 4 (GPIO 34) to GND, with R2 | Filter on the panel-voltage reading, at the ADC input |
| C3 470 µF, C4 100 nF | J14 pin 15 (ESP32 VIN) to J14 pin 14 (GND) | Bulk and high-frequency decoupling for the ESP32's Wi-Fi peaks |
| C10 100 nF | U1 pin 2 (VCC) to GND | RTC decoupling |
| D3 ESD | J4 pin 2 (probe data), short path to GND | Clamp at the cable entry |
| C8 10 µF, C9 100 nF | J8 pin 4 (card VDD) to GND | microSD decoupling |
| C12 1 µF | U4 pin 5 (IN) to GND | Load-switch input |
| C13 1 µF | U4 pin 1 (OUT) to GND | Load-switch output |

## Near

| Part | Place at | Why |
| --- | --- | --- |
| R6 1 kΩ | J14 pin 5 (GPIO 35), with C7 | The filter sits at the ADC end; the trace from U2 OUT to R6 may be longer |
| R5 10 kΩ | U3 pin 3 (IN) | Driver input held low at boot or with JP1 open |
| D6 (not fitted) | Q1 drain (PV+), short path to the star ground | TVS footprint |
| R1 100 kΩ, R2 4.7 kΩ | R2 at J14 pin 4 (GPIO 34) with C5; R1 beside R2, its top end on PV_F after F1 | Keep VDIV short and away from the Q1 loop; up to 60 V on R1's top end |
| F1, D1 | Off the Q1 drain node, in series to J2 (buck input) | Board-supply branch, not in the measured path |
| D2 TVS | J3 (buck output terminal) | Where 5 V enters the board |
| R7, R8 10 kΩ | Across J6 and J7 (the supercap terminals) | Supercap balancing |
| BT1 | U1 pin 14 (VBAT) | Backup cell |
| R13 100 Ω | Between J4/D3 and the ESP32 side of DQ | Series protection, after D3 |
| R12 4.7 kΩ, R20 (not fitted) | J4/J5 | 1-Wire pull-up |
| R14, R15, R16, R17 10 kΩ | J8 pins 2, 3, 7, 10 | microSD pull-ups |
| R18 100 kΩ, R19 0 Ω | U4 pin 4 (EN) | Enable pull-down and link from GPIO 27 |
| D4 | J11 pin 2 (5V SW) | Flyback clamp for a relay coil |
| F4, D5 | High-current path D0 → F4 → D5 → J12; D5 beside J12 with copper for cooling | AUX output |

## Free

R9 and LED1 (visible when the box is open), R10 and R11 (I²C pull-ups, anywhere on SDA/SCL, near U1 or J13), F2 and F3 (between the rails and J11/headers).

The shunt RSH1, the Kelvin traces to U2, the star ground and the high-current loops are set by the layout rules in [CARRIER.md](../CARRIER.md).
