# SUNDIAL

> **Work in progress.** Not yet licensed for reuse; a forkable release is planned after field testing at SUNDIAL 2027. See [FORK-TASKS.md](FORK-TASKS.md).

Nine end-of-life solar panels placed around Bosa, each powering only itself. Same sun, different data.

SUNDIAL is the first work of **PVA (Photovoltaic Art)**, a manifesto for new uses of end-of-life PV panels: [photovoltaic.art](https://photovoltaic.art). It is a public art installation and the proof of concept for PVA. **A SUNDIAL is nine panels;** that is its one rule.

Each panel is three things at once, in order of importance:

1. **A sundial.** A recycled panel on a wall that tells solar time with its gnomon. No visible digital layer: anyone can read it, every day, with no phone.
2. **A self-powered monitor.** Behind the panel, a small board records the panel's own sun every day. The record is collected on foot every fortnight and published on the SUNDIAL website as **Sole**: weekly editions of 63 dials, nine panels by seven days.
3. **An annual event.** Once a year, for about a week, the **event** turns each panel's day of sun into an image drawn live on the visitor's phone through the panel's own Wi-Fi, sealed at sunset. Visitors can leave a line in each panel's book. The week becomes one four-colour screen print.

First event: **SUNDIAL · La Meridiana**, Bosa, summer 2027. SUNDIAL 2027 is a bare-bones trial of the technology and the dial: there is no story or media layer.

The three layers are specified against the carrier board in **[SUNDIAL.md](SUNDIAL.md)**. PVA runs all three. **In year 2 the same nine panels grow into SUNSET** (4 by a firmware update, 5 with a battery and new hardware), each then owned separately; the sundials stay ([PVA growth model](https://github.com/photovoltaic-art/PVA/blob/main/GROWTH.md)). The same carrier board also runs PVA's second work, [SUNSET](https://github.com/photovoltaic-art/sunset), in its own repository.

> Status: drafts, not yet compiled or tested on hardware. Firmware draft 6 records everything the dial needs (sun sections, heat, presence); the panel page and `tools/pva_rules.py` both draw rules v1. Firmware 6.2 (security, visitors' book, pages built into the firmware, event archive by year) and the Sole tools are specified in SUNDIAL.md, not yet written.

## How it fits together

| Layer | What it is | When | Where |
| --- | --- | --- | --- |
| **Sundial** | Gnomon, hour lines and date marks on the glass (no numbers), and the wall plate ([hardware/GNOMON.md](hardware/GNOMON.md)) | Always | On the wall |
| **Sole** | The panels' daily record of sun, collected every fortnight, published as weekly editions of 63 dials | All year | The SUNDIAL website |
| **The annual event** | Each day's dial drawn live and sealed at sunset; the visitors' book; one print per event | One week a year | The panel's own Wi-Fi, then the website |

| Part | What it is | Where it runs |
| --- | --- | --- |
| The panel | PV panel + ESP32 + temperature probe + clock module, no battery, no internet | On a wall in Bosa |
| The dial | Each day's image, drawn on the visitor's phone from the panel's data | The panel's own Wi-Fi during SUNDIAL; the website for Sole |
| The visitors' book | One line per visitor per panel per day, read and chosen the next day | The panel's own Wi-Fi, during SUNDIAL |
| The website | About (the introduction), Bosa 2027 (the event), the map, Sun (Sole) | The SUNDIAL website (this repo's `docs/`); the sheet and Sole are previews on invented data until the real pages are built (`docs/sundial/`, `docs/sole/`) |
| The girasole | A sunflower and a chalkboard: the Heliotropist legend re-enacted, drawn by visitors | First stop of the route during SUNDIAL, moveable |
| The print | The whole event as one 9 × 9 four-colour screen print | Made after each event from the collected data |

Between events the panel's page shows the archive of past SUNDIAL events, and the panels take no input.

A visit during SUNDIAL: the flyer's QR code opens About → the map → at a pin, join that panel's Wi-Fi → the dial opens on its own → leave a line in the book → leave the Wi-Fi, and the panel's link returns to the map. The rest of the year: read the sundial on the wall; the wall plate's QR code opens About with a card for that panel (see *The website*, below).

## Repository

```
SUNDIAL.md                    the three layers specified against carrier v1: sundial, Sole, the annual event
docs/                         the website, the only part published (see The website, below)
  index.html                  About: the introduction; a panel card from the wall plates' ?p=N
  bosa.html                   Bosa 2027: the event, a visit, the print, data and privacy; preview sheet (invented data)
  map.html                    the map
  sun.html                    Sun (Sole in Italian): preview editions (invented data)
  assets/                     site.css; dial.js (the panel page's drawing rules, the event dates, preview data)
  sundial/, sole/, data/      planned: real SUNDIAL sheets and Sole editions (SUNDIAL.md 3.3)
firmware/panel_page_server/
  panel_page_server.ino       ESP32 firmware
  partitions.csv              4 MB flash layout for the ELEGOO ESP32 (~2 MB for pages and data)
  partitions_16mb.csv         16 MB layout for an ESP32-S3 (~9.9 MB)
  panel_config.example.h      template for per-panel settings
  data/                       copied into each panel's flash
    index.html                the panel page: today's dial, gallery of past days, live data
    admin.html                admin page: status, clock, exhibition dates, sun-sensor calibration, raw data download
    media/title.txt           this panel's name
    media/map.txt             the map's web address
texts/
  introduction.en.md          the exhibition introduction and the Heliotropism back story (draft)
  introduction.it.md          the same in Italian
  print-enquiry.md            for the print shop: the project, the print, the proposal, eleven questions
  print-enquiry.it.md         the same in Italian
  pva_sample_a4.pdf           A4 sample sheet of the dial (invented data), made by tools/sample_a4.py
  pva_sample_a4.it.pdf        the same in Italian
  pva_poster_mockup.pdf       A4 mock-up of the full print, 63 tiles (invented data), made by tools/poster_mockup.py
  pva_poster_mockup.it.pdf    the same in Italian
  pva_poster_pv_mockup.pdf    the wall version: 63 dials cut as solar cells on black (and .it.pdf)
  slow-art-sun-record.md      Slow Art: Sun Record, a year of Campbell–Stokes sunshine cards in 14 frames, plus sun-drawing workshops
budget/
  SUNDIAL-budget.xlsx         the cost of the nine panels and the first event (draft), and the script that builds it
hardware/
  CARRIER.md                  the carrier board: everything factory-fitted except the ESP32 and buck converter
  PVA_carrier_board_spec_v1.pdf  the same as a PDF, for sending to a board designer
  carrier/                    the carrier board schematic draft (KiCad project, PDF, netlist, BOM): start at carrier/README.md
  GNOMON.md                   the panel as a sundial: the face, gnomon, date marks, installation, wall test
  sundial-exploded.png/.svg   every part of a panel: front, side, plan, the enclosure exploded
  POST.md                     the free-standing panel: post, base, USB charging from the sun
tools/
  pva_rules.py                the dial rules as drawing code (canonical print, separations); rules-2 for Sole planned
  pva_import.py, sole_edition.py  planned: round downloads → SUNDIAL pages and Sole editions (SUNDIAL.md 3.4)
  sample_a4.py                A4 sample sheet, invented data
  poster_mockup.py            A4 mock-up of the canonical print, invented data
  requirements.txt
```

## The website

In the repository's GitHub Pages settings, publish from the `docs` folder on the main branch, then point the instance's domain at it (Bosa: `bosa.photovoltaic.art`). Only `docs/` is published; the panel files stay in the repo but never appear online. English only for now.

| Page | For | Notes |
| --- | --- | --- |
| `index.html` (About) | Everyone: what SUNDIAL is | Buttons to Bosa 2027 and the map |
| `bosa.html` (Bosa 2027) | Visitors planning a visit | Dates, a visit step by step, the print, privacy; the sheet is a **preview** on invented data |
| `map.html` | Visitors on the route | Pins, which panels are likely awake, the visitor's position; a one-line tip on first open |
| `sun.html` (Sun) | The year-round record (Sole in Italian) | Sample editions, **preview** on invented data, until `sole_edition.py` writes the real ones |

**Where each link goes:**

| Link | Address | Lands on |
| --- | --- | --- |
| Flyer QR code | `https://bosa.photovoltaic.art/` | About |
| Wall plate QR code, panel N | `https://bosa.photovoltaic.art/?p=N` | About, opening with a "You are here: panel N" card: how to read the sundial, its Wi-Fi name, and during the event how to see today's dial; buttons to the map |
| Panel page, "back to the map" | `map.txt`: `https://bosa.photovoltaic.art/map.html` | The map, for visitors mid-walk |

**The event dates** live in one place: `EVENT` at the top of `docs/assets/dial.js`. Set the dates and `confirmed: true` when they are fixed; the wall plates' panel card follows them.

**Pins** are placed on site: open the map with `?edit` after the address (`map.html?edit`), drag the pins, tap **Copy positions** and paste them into the `PANELS` list at the top of `docs/map.html`.

## Preparing a panel

1. **Settings.** Copy `panel_config.example.h` to `panel_config.h` and set the panel's Wi-Fi name (`panel-01` … `panel-09`) and a long, unique admin key. `panel_config.h` is ignored by git; keep the keys somewhere safe.
2. **Build stage.** Set the four switches at the top of the firmware (see the table below). Pins are preset for the ELEGOO 30-pin board; on an ESP32-S3, set them by hand.
3. **Media.** Edit `data/media/title.txt` (panel name) and `data/media/map.txt` (map address).
4. **Build.** Arduino IDE, ESP32 core 3.x; libraries OneWire, DallasTemperature, RTClib. ELEGOO: board *ESP32 Dev Module*, Flash 4 MB, Partition Scheme *Custom* (uses `partitions.csv` in the sketch folder). ESP32-S3: board *ESP32S3 Dev Module*, Flash 16 MB, PSRAM OPI, and rename `partitions_16mb.csv` to `partitions.csv`.
5. **Flash.** Erase all flash first (essential on any board that ever held keys), upload the firmware, then upload `data/` with the LittleFS uploader. **First installation only:** erasing or uploading `data/` wipes the panel's archive and logs. From firmware 6.2 the pages are built into the firmware, and a later update flashes the firmware alone, after a full download (SUNDIAL.md 4.4).
6. **Set up on site.** Join the panel's Wi-Fi, open `http://192.168.4.1/admin.html`, enter the key, set the clock from your phone and set the exhibition's first and last day.
7. **Calibrate the sun sensor** (if fitted): on a clear day near solar noon, tap **Calibrate now**, **in the two weeks before each event**. On a vertical panel the noon current changes strongly with the season, so the reference must come from the event's own season. Until then the panel still logs the raw current, and the dial's sun sections are drawn as outline.

| Stage | Hardware | `BENCH` | `PANEL_SENSE` | `USE_RTC` | `SUN_SENSE` |
| --- | --- | --- | --- | --- | --- |
| 1, bench | ESP32 on USB, temperature probe | 1 | 0 | 0 | 0 |
| 1, panel | + panel, buck converter, supercapacitor | 0 | 0 | 0 | 0 |
| 2, full | + voltage divider, DS3231 clock, protection | 0 | 1 | 1 | 0 |
| 2, sun | + sun sensor (MOSFET, shunt, INA180) | 0 | 1 | 1 | 1 |
| Desk test | any ESP32 on USB, no sensors at all | 1 | 0 | 0 | 0, plus `BENCH_FAKE 1` |

`BENCH_FAKE 1` invents a temperature curve and a sun with passing clouds, so the dial shows every layer on the desk. It refuses to compile unless `BENCH` is 1.

Without the divider (`PANEL_SENSE 0`) there is no dawn gate or dusk close: the supercapacitor smooths the start, and the board simply runs until the light fails. Without the clock (`USE_RTC 0`), the first visitor's phone sets the time each day.

## Installation: the admin checklist (per panel)

**In the workshop**

1. **Settings.** `panel_config.h` from the example: Wi-Fi name (`panel-01` … `panel-09`) and a long, unique admin key, recorded somewhere safe.
2. **Media.** `title.txt` (panel name) and `map.txt` (map address).
3. **Stage switches** to match the hardware fitted. `BENCH` back to `0` before installing.
4. **Flash.** Arduino IDE, ESP32 Dev Module, Custom partitions: erase all flash, upload the firmware, upload `data/` with the LittleFS uploader.
5. **Power chain.** Buck converter set to exactly 5.0 V before anything is connected; then fuse, diode, supercapacitor, TVS.
6. **Sensors.** Probe on GPIO 4 · divider on GPIO 34 · DS3231 on GPIO 21/22 · sun sensor gate on GPIO 25, amplifier on GPIO 35.
7. **Bench test.** On USB: set the clock, set the exhibition dates to today, check status (clock module fitted, probe found, voltage plausible), watch a dial form.
8. **Face and frame.** Apply the hour lines and the three date marks from the template; drill the frame; fit the 45 cm gnomon at 50° and the stand-off brackets ([hardware/GNOMON.md](hardware/GNOMON.md)).

**On site**

9. **Permission** from the wall owner and the Comune (and heritage authorities in the centro storico) **for a permanent installation**, plus public liability insurance (SUNDIAL.md section 5).
10. **Wall test.** Compass for a first reading, then the noon-shadow test: which edge packs out, and by how much.
11. **Mount.** Cut the stand-offs, hang, spirit level against the glass; box on the deep side, probe on the panel back.
12. **Wall plate** beside the panel: its number and the QR code, which opens `/?p=N` for that panel.
13. **Solar-noon check.** The shadow falls straight down the noon line; adjust the stand-offs if not.
14. **Admin page.** Join the panel's Wi-Fi, open `http://192.168.4.1/admin.html`, enter the key, set the clock and the exhibition dates.
15. **Calibrate the sun sensor** on a clear day near solar noon, in the two weeks before the event starts. Uncalibrated, every section draws as an outline.
16. **Map pin.** `map.html?edit`, drag the pin, copy the positions into `docs/map.html`, push.

**The girasole (once, for the whole trail)**

- **Sow** two or three dwarf sunflowers in large pots in early to mid May, so one is still in bud, and turning with the sun, in the solstice week. Keep the best.
- **Set up** the pot and a chalkboard, with ochre and blue chalk, in front of a south-facing wall: the first stop of the route. It is moveable; place its pin (the flower) with `?edit` like the panels.

**During the run**

17. **Daily round, any time the panels are awake.** Each panel's status; yesterday's visitors' book, ticking the lines to show; a raw-data download (Safari on iPhone or Chrome on Android, not the Wi-Fi pop-up, which cannot save files). At the girasole, at sunset: photograph the chalkboard, then wipe it for the next day; water the plant.
18. **Upkeep.** Clean the glass; replace a failed board or panel. A day lost shows in the gallery as the black outline.

**After the run**

19. **Final walk, the morning after the last day:** read the last book, final download from every panel, clear the raw book entries (setup key). Then the seven chalkboard photographs → canonical sheet and separations → print. **The panels stay up:** the sundial carries on, and so does the record.

**All year (Sole)**

20. **Fortnightly round, every second Monday:** status, clock check, full download, clean the glass, check gnomon, plate and box; one line per panel in the round log. Then import, build the two new weekly editions, push. Details: SUNDIAL.md 3.2.

**Every year (SUNDIAL.md 4.4)**

21. **Spring visit:** full download first; firmware only if something changed (never erase, never upload `data/`); check supercaps, coin cell, probe, seals; set the new event's dates.
22. **The two weeks before the event:** calibrate every panel.

## The visitor's experience

1. A flyer or a wall plate: scan the QR code.
2. The map opens on mobile data: the route, the girasole and nine pins, the visitor's own position, which panels are likely awake now.
3. The first stop, the girasole: the legend re-enacted. A young sunflower turning with the sun, and a chalkboard. The visitor adds a mark, ochre for sun or blue for shade, and writes the time beside it.
4. At a pin: a panel, which is also a sundial telling solar time.
5. Join the open Wi-Fi `panel-0N`; the page opens by itself. No internet is involved.
6. Today's dial forming live, or sealed after sunset: the same rule as the chalkboard, drawn by the panel. Tap it for the day's facts.
7. Under today's dial: the visitors' book, one line for this panel. Chosen lines appear the next day.
8. Below: the gallery of earlier days, each with its chosen lines; a day the panel did not wake is the black outline.
9. A strip at the bottom: panel temperature, time awake, sunset.
10. Leave the Wi-Fi, back to the map, on to the next panel.

The visitor's phone counts once per solar hour as a dot on the dial, never identified.

## To do

- [ ] **The artist's proof** (*prova d'artista*): one panel, a complete SUNDIAL, made before the nine and kept by PVA outside the edition. It is the pilot panel below: proving the carrier, gnomon and hour lines, bench-testing every firmware build, and showing the comune and hosts ([GROWTH.md](https://github.com/photovoltaic-art/PVA/blob/main/GROWTH.md), the path).
- [ ] **Import script:** turn an admin download into tile data for `pva_rules.py`, the canonical sheet and the website page.
- [ ] **Separations script:** one file per ink for the screen print.
- [ ] **Website page** for the canonical sheet, filled after each day's round.
- [ ] **Calibration** of every panel before the run; prove the step on the pilot.
- [ ] **"How to read the dial" key** in the panel page's info overlay, as well as on the flyer and website.
- [ ] **Italian and English** on the panel page, info overlay and map.
- [ ] **Wall plate design:** the number, and the QR code to `/?p=N`; the panel's node logo (SUNSET [logos/](https://github.com/photovoltaic-art/SUNSET/tree/main/logos)) sits in the centre of the QR code, with the QR's highest error correction (level H) so it still scans; panel N carries node N's logo, so one plate serves SUNDIAL and SUNSET. The logo is a sign to be recognised, not a code: the QR does the scanning. Test the scan on several phones before ordering plates.
- [ ] **"Stay connected"** wording on the flyer or wall plate: some phones warn about or drop a network with no internet.
- [x] **After the last day:** the panel page shows the archive of past events (SUNDIAL.md 4.1).
- [ ] **Firmware 6.2** (SUNDIAL.md 4.1): challenge-and-response admin login with round and setup keys, lockout and action log; the visitors' book; pages built into the firmware; no visitor clock-setting when the clock module is fitted; rules version check; event archive by year.
- [ ] **Permissions** for a permanent installation: wall owners, Comune and heritage, insurance (SUNDIAL.md section 5). Say the panels may grow into SUNSET in year 2.
- [ ] **Site plan with year-2 roles:** choose each of the nine sites for its SUNSET role too (walls spread; the gateway pair together near footfall; the auction where people pass; the arm in shade; the set near the sunset spot): [GROWTH.md](https://github.com/photovoltaic-art/PVA/blob/main/GROWTH.md) 1.
- [ ] **Sole tools and pages:** rules-2 in `pva_rules.py`, `pva_import.py`, `sole_edition.py`, `docs/sole/` and `docs/sundial/` (SUNDIAL.md 3.3–3.4).
- [ ] **First compile and bench test** of firmware draft 6.
- [ ] **The girasole:** sunflower variety and sowing in May; a moveable chalkboard and its stand; where it stands on the route.
- [ ] **Test the face on the artist's proof** (hardware/GNOMON.md, the face): hour lines and date marks on the glass, no numbers, 45 cm gnomon. Measure short-circuit current near solar noon with and without the tape; check the lines read from the street; at the next solstice or equinox, check the tip's noon shadow touches its mark. Fallback: unnumbered brackets on the frame edge.

**Optional**

- [ ] **The wall version** (a second artwork, only if time allows): the 63 dials as solar cells, 210 mm squares with 30 mm corner cuts, 2 mm gaps between columns and 4 mm between rows, on a black board, about 1.95 × 1.96 m. Print on Dispa (3.8 mm all-paper board, UV print and machine cut, Pixartprinting) or on laminated card from a copier; proof first. Mock-up: `texts/pva_poster_pv_mockup.pdf`.
- [ ] **Exhibition catalogue:** a bound book of the images, about 70 pages, printed on demand (Pixartprinting): the introduction, the 63 dials one per page, the canonical sheet, how to read a dial, the Heliotropist legend. Check the page count fits their binding (often a multiple of 4).

## Hardware per panel

Each panel is also a vertical sundial, mounted vertical and facing due south: see [hardware/GNOMON.md](hardware/GNOMON.md) for the gnomon, the drilling template, the installation and the noon-shadow wall test. Where there is no suitable wall, a panel can stand on its own post on private ground, such as a café's seating area, with USB sockets that charge phones from its sun in daylight: [hardware/POST.md](hardware/POST.md).

**Stage 1:** 36 V 180–185 W PV panel (the panels chosen are the Trina TSM-185DC01: [hardware/GNOMON.md](hardware/GNOMON.md)) · DC-DC buck converter (8–60 V in), set to exactly 5.0 V with a multimeter **before** connecting anything · 5.5 V 4 F supercapacitor across the 5 V output (in the shaded box: it ages fast in heat) · ELEGOO ESP32 30-pin on a screw-terminal breakout · DS18B20 waterproof probe on the panel back, data on GPIO 4, 4.7 kΩ from GPIO 4 to 3.3 V.

**Stage 2 adds** (or the carrier board in `hardware/CARRIER.md`, which fits all of this): fuse and reverse-polarity diode on the panel side · SMAJ5.0A TVS diode across 5 V · panel-voltage divider 100 kΩ / 4.7 kΩ + 100 nF into GPIO 34 (must be GPIO 32–39: the other analog pins stop working with Wi-Fi on) · DS3231 clock module on GPIO 21/22.

**Sun sensor:** logic-level N-MOSFET (≥60 V, ≥20 A) across the panel, after an input Schottky diode (≥100 V, ≥15 A, so a reversed panel cannot overheat the MOSFET) and before the fuse and the 1N5408 (the short-circuit current must not run through the fuse), gate on GPIO 25 (100 Ω series, 10 kΩ pull-down) · 5 mΩ shunt in its source leg · INA180A3 (gain 100) across the shunt, on 3.3 V, output to GPIO 35. Every 10 s the panel is shorted for about a millisecond and its short-circuit current read; the supercapacitor carries the board through the pulse. If the shunt or gain differ, change `SHUNT_OHM` and `SENSE_GAIN`.

## The dial (rules v1, draft)

- **Time:** solar noon at the top; 12° per hour; Bosa's solstice day (15 h 03 m) spans 180°, shorter days proportionally less.
- **Sun:** a ring of 15-minute solar sections, ochre when this panel is in direct sun, blue when it is not (shade, cloud, or the sun behind the panel), from a short-circuit current reading (above a third of the panel's clear-noon current = sun).
- **Heat:** a red line rising from the axis, the panel's warming since sunrise; +40 °C reaches the ring, with no upper limit.
- **Presence:** one black dot per solar hour, for visitors in that hour: small 1–5, medium 6–10, large 11+.
- **Seal:** the black horizon line; nothing after sunset enters the dial.
- **A panel that did not wake:** the ring outline and the axis only, in black.
- **Inks:** ochre, red, blue, black, translucent, printed in that order.

*Horas non numero nisi serenas* — I count only the sunny hours.

## What a panel records

| File | Contents | Who sees it |
| --- | --- | --- |
| `/art/DATE.csv` | every 5 min: volts, temperature, sun current | visitors (exhibition days, sealed at sunset) |
| `/art/DATE.sun.csv` | each 15-minute solar section: sun 1 / 0 / −1 unknown, readings, readings above, mean current | visitors |
| `/art/DATE.vis.csv` | each solar hour: distinct phones | visitors |
| `/log/…`, `/archive/…` | every 5 min record, sun current every minute, visitors per hour, every day | admin only, as one CSV |

## Data and privacy

Visitors are counted, never identified: a phone is told apart only by a salted hash kept in memory for one hour; the salt changes at every power-on and is never stored. The panel keeps no one.

The visitors' book keeps only what the visitor writes: a line and an optional first name or town. Lines are read the next day; chosen lines appear on the panel and the website, the rest are deleted from the panel after the final walk. The full book is kept by PVA for the archive and catalogue.

Raw data stays on each panel and is downloaded only through the admin page; visitors see the exhibition days' images, nothing else. The public website publishes only what the editions need: sun sections, temperatures, visitors per hour, and the day's figures.
