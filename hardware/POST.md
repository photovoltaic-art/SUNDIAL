# The post: a free-standing SUNDIAL panel

A SUNDIAL panel on its own post, for a site with no suitable wall: a café's or bar's outdoor seating area, on private ground. It is the same panel, the same sundial and the same carrier board as a wall panel, with one addition: **USB sockets that charge phones from the panel's own sun, while the sun shines.**

> Status: design, not yet built, 23 Oct 2026. **No battery, and no change to the carrier board:** the charger hangs off the board's existing AUX output and switched 5 V (CARRIER.md 9 and 10). Structural figures here are indicative; an engineer signs off the post and base before anything is built.

---

## 1. When to use it

- **Where no wall works:** none faces within about 20° of south (the noon-shadow test, [GNOMON.md](GNOMON.md)), or none can be used.
- **On private ground,** in an outdoor seating area, with the owner's written consent. Not on the street or other public land.
- **It counts as one of SUNDIAL's nine panels.** It is a mounting, not a new kind of panel: it records Sole, shows the dial and runs the event like the other eight.

---

## 2. What stays the same

| | Wall panel | Post |
| --- | --- | --- |
| Panel | Trina TSM-185DC01, portrait, vertical, due south | The same |
| Sundial | 45 cm gnomon at 50° on the centre line; hour lines and date marks on the glass, no numbers | The same parts and template |
| Board | Carrier v1, unchanged, no battery | The same; AUX and switched 5 V now used (4) |
| Firmware | SUNDIAL | SUNDIAL, plus the charger switch (4.3) |
| Awake | Dawn to dusk | The same; the sockets are live only while the sun allows |
| Sole record | Short-circuit current every 10 s | Unchanged: the sun sensor reads the short-circuit current, which a load on AUX doesn't affect, and D5 keeps the charger out of the pulse (CARRIER.md 10) |

**Easier than a wall:** the post is simply turned to face due south when it is set. No stand-offs, no packing, no wall test. The noon shadow falling straight down the noon line is the check, as on every panel.

---

## 3. The post

### 3.1 Form

- **A single frame, front and back in view.** The panel hangs vertical on two uprights (or one central post), facing due south, with its back to the north. Both faces are honest: the glass and gnomon to the south, the backsheet, the junction box and the board's box to the north.
- **Heights, for the gnomon's safety:**

| | Height above the ground |
| --- | --- |
| Panel bottom edge | about 1.00 m |
| Gnomon tip (45 cm at 50°: about 29 cm below the root, 35 cm out) | about 2.30 m |
| Gnomon root, panel top edge | about 2.60 m |
| USB sockets (4.2) | about 0.90–1.00 m, table height, on the post |

  The gnomon tip stays above head height, capped as on every panel. The whole object is about the height of a café parasol.
- **Material:** galvanised or stainless steel uprights, the panel fixed to them through the same M6 holes and aluminium angle as the wall stand-offs. Nothing touches the glass.
- **Cables** run inside the upright to the board's box, mounted high on the back, out of reach.

### 3.2 Wind and base (indicative)

A 1.3 m² panel standing in the open catches the wind like a sign board. As a first estimate for an exposed coastal site in Sardinia: a peak wind pressure of roughly 0.9 kN/m² and a force coefficient of about 1.8 give a load of about **2 kN** at about 1.8 m, an overturning moment of about **4 kN·m** at the base.

| Base | What it takes | Fit for a seating area |
| --- | --- | --- |
| **Bolted to an existing concrete slab** (chemical anchors through a steel base plate) | A sound slab, the owner's consent to drill | **Preferred** where the slab exists: small, neat, removable |
| **A small concrete footing** | Digging; the owner's consent | Permanent; for gravel or soil |
| **Ballast** (a steel tray loaded with paving slabs or planters) | Roughly **a tonne** for a base about 1.2 m square | Possible, but bulky; takes seating space |

The engineer's calculation replaces these figures. The post and base are also designed so the panel can be lifted off and the post unbolted, so the host can have the space back.

---

## 4. USB charging from the sun

### 4.1 Wiring

```
 PV panel ──► carrier J1 ──► (D0) ──► F4 (3 A) ──► D5 ──► J12 AUX ──► USB charger module ──► sockets
                                                                         ▲
                     GPIO 27 ──► U4 load switch ──► J11 "5V SW" ──── EN ─┘
```

- **Power:** from **AUX (J12)**, the carrier's output for spare panel power. At about 36 V, the v1 fuse of 3 A allows over 100 W, more than a vertical panel ever gives.
- **Switch:** the board turns the charger on and off through **J11 `5V SW`** (U4, GPIO 27) into the module's enable input, or a small relay if the module has none.
- **The module:** a wide-input DC-DC charger (input rated above the panel's open-circuit voltage on its label, with margin: 60 V or more) with one **USB-C PD** and one **USB-A** output, about 30 W in total. It must **hold its input voltage up** (input-voltage regulation, or an adjustable undervoltage cut-off set around 28–30 V): when phones ask for more than the panel can give, the charger must back off, not drag the panel's voltage down.

### 4.2 The sockets

- **Two sockets,** USB-C and USB-A, in a vandal-resistant, weatherproof panel-mount housing (IP67 with caps), at table height on the post.
- **A small shelf** under them to rest a phone while it charges.
- **No wireless charging:** it wastes a third of the energy and runs warm in the sun.
- **A small plate:** the panel number, and "charges while the sun shines · at your own risk". Nothing else, as the manifesto asks.

### 4.3 Firmware

- **The panel comes first.** The charger is enabled only when the panel's voltage (GPIO 34) is comfortably above the board's needs, and cut the moment it sags, so the board never browns out. The supercaps cover the moment of switching.
- **Off at dusk,** with the rest of the panel. Nothing special is needed for the 1 ms sun pulse every 10 s: D5 isolates the charger, which rides through on its own capacitors.
- **Honest measure.** The board cannot measure the energy the charger delivers (the AUX path bypasses the shunt, and SUNDIAL deliberately has no energy meter: SUNDIAL.md 1). It can count what it knows: **minutes the sockets were live**. If an energy figure is wanted, a current monitor (INA226 class) on the I2C header J13, in the AUX line, gives it without changing the board; then the dial page could say *this panel gave 38 Wh to phones today*.

### 4.4 What to expect

- About **50–60 W at noon in June** from a vertical panel, much less in winter and under cloud: enough for two phones at full speed around midday, a slow trickle early and late.
- Phones cope with the charge stopping and starting as clouds pass; the charger simply follows the sun.

---

## 5. In a seating area

- **Shade:** parasols, awnings and trees that shade the panel shade its record too. That is honest (the panel records its own sun), but site the post where the shade is predictable, and note it in the round log.
- **People around it:** the gnomon above head height, its end capped; nothing sharp below 2 m; the board's box high on the back.
- **Cleaning:** a café terrace is dusty and greasy. Clean the glass on every round (SUNDIAL.md 5), more often if the record shows it.
- **The host:** the café or bar gets a sundial on its terrace and free charging for its customers, in daylight. No money and no endorsement either way, as for wall owners.

---

## 6. Permissions

Lighter than a wall over a street, because it is on private ground, but not none:

- **The owner's written consent:** for a permanent installation, access for the round and the yearly visit, and the right to remove (as for walls, SUNDIAL.md 5).
- **Heritage and landscape:** in the centro storico or another protected area, a visible structure on private ground may still need the comune's or the Soprintendenza's agreement (possibly an *autorizzazione paesaggistica*). Check before building.
- **Structure:** the engineer's sign-off of post and base (3.2).
- **Liability:** public liability insurance covering the structure and the sockets, as for the wall panels' gnomons.

---

## 7. Open questions and bench tests

| Question | Notes |
| --- | --- |
| Charger module | Which wide-input USB-C PD module holds its input voltage up; test it on a real panel under passing cloud |
| One post or two | A central post is lighter to look at; two uprights hold the panel more simply |
| Energy figure | Minutes only, or a current monitor on J13 for watt-hours |
| Watering | A post with a closed IBC tank and a sun-watered flower bed is specified for SUNSET: [garden-node.md](https://github.com/photovoltaic-art/SUNSET/blob/main/garden-node.md) |
| Bench | A panel on a test stand, the carrier, the charger and two phones for a day: the board never browns out; the sun record stays clean |
| Base | Slab, footing or ballast at the first candidate site |
