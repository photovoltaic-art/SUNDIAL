# Where each passive and small part goes on the board (added 26 Oct 2026, answering Rush PCB).
# The schematic joins parts by net name, so it does not show which capacitor or resistor belongs to which part.
# RSH1/RSH2 (shunt) and the high-current paths are covered by the layout rules in CARRIER.md.
# ref -> (priority, place next to, why). Priority: "critical" = within a few mm, short direct traces;
#                                                  "near" = same area, short trace; "free" = anywhere sensible.
PLACEMENT = {
    # 1. Sun sensor
    "C6":  ("critical", "U2 pin 5 (VS) to U2 pin 2 (GND)", "U2 supply decoupling"),
    "R6":  ("near", "J14 pin 5 (ESP32 GPIO 35), together with C7", "RC filter on ISENSE: put the filter at the ADC input"),
    "C7":  ("critical", "J14 pin 5 (GPIO 35) to GND, with R6", "RC filter on ISENSE"),
    "C11": ("critical", "U3 pin 2 (VDD) to U3 pin 4 (GND)", "Gate-driver supply decoupling: it supplies the gate current pulses"),
    "R4":  ("critical", "Q1 gate pad, between U3 pin 5 (OUT) and Q1 gate", "Gate resistor: keep the U3 -> R4 -> Q1 gate loop short"),
    "R21": ("critical", "Directly across Q1 gate and source pads", "Gate-source pull-down: holds Q1 off at dawn"),
    "R5":  ("near", "U3 pin 3 (IN)", "Holds the driver input low while the ESP32 boots or JP1 is open"),
    "D6":  ("near", "Q1 drain (PV+), short path to the star ground", "Footprint only: TVS on PV+"),
    "D0":  ("critical", "Right after J1, in the sun loop J1 -> D0 -> Q1 -> RSH1", "Input diode: high current, copper area for cooling"),
    # 2. Divider
    "F1":  ("near", "Off the Q1 drain node (PV+), start of the board-supply branch", "Board-supply fuse (not in the measured path)"),
    "D1":  ("near", "Between F1 and J2 (buck input)", "Reverse polarity; blocks Q1 pulses from the buck"),
    "R1":  ("near", "Next to R2; its top end on PV_F after F1", "Divider top (up to 60 V: keep clearance)"),
    "R2":  ("near", "J14 pin 4 (ESP32 GPIO 34), with C5", "Divider bottom: keep VDIV short and away from the Q1 loop"),
    "C5":  ("critical", "J14 pin 4 (GPIO 34) to GND, with R2", "Divider filter at the ADC input"),
    # 3. 5 V rail
    "D2":  ("near", "J3 (buck output terminal)", "TVS where 5 V enters the board"),
    "C3":  ("critical", "J14 pin 15 (ESP32 VIN) to J14 pin 14 (GND)", "Bulk capacitor for the ESP32's Wi-Fi current peaks"),
    "C4":  ("critical", "J14 pin 15 (VIN), next to C3", "High-frequency decoupling at VIN"),
    "R7":  ("near", "J6 (upper supercap terminal), across +5V and MID", "Supercap balancing"),
    "R8":  ("near", "J7 (lower supercap terminal), across MID and GND", "Supercap balancing"),
    "R9":  ("free", "Next to LED1", "LED resistor"),
    "LED1": ("free", "Visible when the box is open", "5 V present indicator"),
    # 5. Clock
    "C10": ("critical", "U1 pin 2 (VCC) to GND", "RTC supply decoupling"),
    "BT1": ("near", "U1 pin 14 (VBAT)", "Backup cell"),
    "R10": ("free", "On SDA, near U1 or J13", "I2C pull-up (one set for the whole bus)"),
    "R11": ("free", "On SCL, near U1 or J13", "I2C pull-up"),
    # 6. Probes
    "D3":  ("critical", "J4 pin 2 (DQ_T), short path to GND", "ESD clamp at the cable entry"),
    "R13": ("near", "Between J4/D3 and the ESP32 side of DQ", "Series protection resistor, after D3"),
    "R12": ("near", "J4/J5", "1-Wire pull-up"),
    "R20": ("near", "J4/J5, beside R12", "Footprint only: stronger pull-up"),
    # 7. microSD
    "C8":  ("critical", "J8 pin 4 (VDD) to GND", "Card bulk decoupling (inrush on insert)"),
    "C9":  ("critical", "J8 pin 4 (VDD), next to C8", "Card high-frequency decoupling"),
    "R14": ("near", "J8 pin 2 (CS)", "Pull-up; also keeps GPIO 5 high at boot"),
    "R15": ("near", "J8 pin 3 (MOSI)", "Pull-up"),
    "R16": ("near", "J8 pin 7 (MISO)", "Pull-up"),
    "R17": ("near", "J8 pin 10 (detect)", "Pull-up"),
    # 9. Power take-off
    "C12": ("critical", "U4 pin 5 (IN) to GND", "Load-switch input capacitor"),
    "C13": ("critical", "U4 pin 1 (OUT) to GND", "Load-switch output capacitor"),
    "R18": ("near", "U4 pin 4 (EN)", "Keeps the switched output off at boot"),
    "R19": ("near", "U4 pin 4 (EN), on the trace from GPIO 27", "0 ohm link"),
    "D4":  ("near", "J11 pin 2 (5V SW)", "Flyback clamp for a relay coil on 5V SW"),
    "F2":  ("free", "Between the +5V rail and J11 pin 1", "Protects the board from add-ons"),
    "F3":  ("free", "Between +3V3 and the header/J11 3V3 pins", "Protects the board from add-ons"),
    # 10. AUX
    "F4":  ("near", "High-current path D0 -> F4 -> D5 -> J12", "AUX fuse holder"),
    "D5":  ("near", "Next to J12, with copper for cooling", "AUX isolation diode"),
}
