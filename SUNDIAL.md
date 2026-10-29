# SUNDIAL — three layers, specified against carrier v1

SUNDIAL is the first work of PVA (Photovoltaic Art, [photovoltaic.art](https://photovoltaic.art)). Each SUNDIAL panel is three things at once, in order of importance:

1. **A sundial.** A recycled PV panel that tells solar time with its gnomon. No visible digital layer.
2. **A self-powered monitor.** It records its own sun every day, collected on foot and published as **Sole**.
3. **An annual event.** **SUNDIAL** turns a week of each panel's data into artworks, with a visitors' book.

This document takes the carrier board v1 ([hardware/CARRIER.md](hardware/CARRIER.md)) as fixed and specifies what each layer needs, what the hardware allows, and what changes in the software. **PVA runs all three.**

> Status: draft v6, 20 Oct 2026. Written against firmware draft 6.1 (`pva-fw-6.1`, rules-1) and carrier spec v1. Nothing here changes the carrier board. v5 narrows PVA to three layers: the notice board, structured feedback and service-phase firmware are dropped. Feedback lives on as the SUNDIAL visitors' book. v6 applies a full review: pages built into the firmware so yearly updates keep the data, calibration before each event, corrected storage figures, key handling on the walker's phone, no visitor clock-setting, and permissions and upkeep (section 5).

**No content goes into a panel, except the visitors' book during the event.** Between events the panels tell the time with a shadow and record the sun; the only admin actions are downloads and small clock corrections. During each event they also take the visitors' book, and the admin ticks which lines to show. The firmware is one line, 6.2, changed at most once a year at the spring visit, and a firmware change never touches the panel's data (4.4).

---

## 1. The fixed hardware

| Resource | On carrier v1 | What it means |
| --- | --- | --- |
| Processor | ELEGOO ESP32 (original ESP32, 2 cores, ~320 KB RAM, no PSRAM) | Enough for a small web server and the admin login. Drawing happens on the visitor's phone, as the dial already does |
| Flash | 4 MB: 1.9 MB app, ~2 MB LittleFS, no second app slot | Firmware can only be changed by opening the box and using USB. From 6.2 the pages are built into the firmware, so LittleFS holds **data only**: the event archives plus about four weeks of raw logs in summer |
| microSD | Socket J8 fitted, unused by firmware 6 | Not needed by any layer. Kept for the future |
| Clock | DS3231 + CR2032, no charging | Time survives the night. Drift is about 1 minute a year; the round corrects it. The coin cell lasts years at backup current and is checked at the spring visit. **Visitors can never set the clock** (4.1) |
| Power | Panel → buck → 5 V; two 10 F supercaps in series (5 F) | Ride-through is under a minute at the board's draw (about 20 J between 5 V and the dev board's dropout, at 0.4–0.6 W). The supercaps bridge sun-sensor pulses and clouds. Twilight serving runs on the remaining daylight, not on the supercaps |
| Off every night | No battery, by design | RAM is wiped every night, and with it the salt used to tell phones apart. This is a privacy feature (4.2) |
| Sensors | Panel volts (GPIO 34), short-circuit current every 10 s (GPIO 35), panel temperature (J4), optional second probe (J5) | Sunlight, heat and site. **No measure of energy delivered:** the board draws under 1 W from a 185 W panel, so the panel is effectively unloaded (3.1) |
| Radio | Wi-Fi access point, open, up to 10 phones at once, plain HTTP | No TLS: anything sent on the open network can be read by anyone in range (4.3). Pages must work in the phones' captive-portal mini-browser |
| Interfaces on the object | None: no screen, no buttons | Every interaction is on the visitor's phone |
| Expansion | I2C header, 9 spare GPIO, UART, switched 5 V, AUX panel power | Not used by any layer. The free-standing post uses AUX and switched 5 V for USB charging in daylight ([hardware/POST.md](hardware/POST.md)) |

**What the hardware rules out, whatever the software:** running at night; knowing who a visitor is; measuring energy produced; any backhaul; and updating firmware or pages without opening the box.

---

## 2. Layer 1 — the sundial

**Purpose:** a recycled panel on a wall that is also a real vertical sundial, readable by anyone, every day, with no phone and no electricity. This is the layer most people will ever meet.

**Specified in** [hardware/GNOMON.md](hardware/GNOMON.md) (and, where no wall works, a free-standing post on private ground: [hardware/POST.md](hardware/POST.md)): a 45 cm gnomon at 50° on the panel's centre line; hour lines on the glass for solar hours 7–17, **with no numbers**; three date marks on the noon line for the winter solstice, the equinoxes and the summer solstice; due-south mounting with the wall test and the noon-shadow check. Everything that carries load bolts to the frame; only the tape lines are on the glass.

**What the passer-by sees:** a panel, its shadow on a fan of thin lines, and a small wall plate with the panel's number and a QR code. **No visible digital layer.** The Wi-Fi and the dial on the phone are found only by those who look.

**Software:** none. The physical dial and the digital dial read the same solar time, and that is the only link between them.

**To test on the artist's proof:** the tape's loss of current, how the lines read from the street, and the date marks at the next solstice or equinox (README, To do).

---

## 3. Layer 2 — Sole, the sun monitor

**Purpose:** all year, every year, the nine panels record Bosa's sun in the background. The record is collected on foot every fortnight and published on the SUNDIAL website as **weekly editions of 63 dials**: nine panels × seven days, the same grid as the SUNDIAL sheet. Over the years the editions become a continuous portrait of the sun in nine streets of Bosa. **PVA runs it.**

**The split:**

| Where | What it does | Changes |
| --- | --- | --- |
| **The panel** | Serves only the SUNDIAL archive (section 4). Keeps logging every day in the background, as firmware 6 already does | **None.** Firmware 6.2 as specified for SUNDIAL |
| **The round** | Every fortnight, PVA collects the raw data from each panel: two weekly editions per round | A routine, no new code (3.2) |
| **The website** | A **Sole** tab beside the map and the SUNDIAL sheets: the editions, built from the downloads | Import and edition tools, pages (3.3, 3.4) |

### 3.1 What a Sole dial shows

The same dial as SUNDIAL, drawn by the website's tools instead of the panel:

- **Time:** solar noon at the top, 12° per hour; short winter days make visibly shorter arcs.
- **Sun:** the ring of 15-minute sections, ochre for sun, blue for shade.
- **Heat:** the red line, the panel's warming since sunrise.
- **Presence:** the black dots for visitors in each solar hour (anonymous counts; few after the run).
- **Seal:** the horizon line at Bosa's sunset.
- **A day the panel did not wake,** or whose data was lost: the black outline, as in SUNDIAL.

**Rules-2: one change from rules-1, the sun threshold.** SUNDIAL calls a section "sun" when the current is above a third of one **clear-noon reference measured just before the event** (`iref`, 4.4). That works for the event week and fails over a year, because the panel is **vertical**:

- In June, Bosa's noon sun is about 73° high and strikes the glass at a steep angle (cos of incidence ≈ 0.29).
- In December it is about 26° high and strikes almost head-on (≈ 0.90).

Clear-noon current in winter is roughly **three times** the June value, so a summer reference would draw winter shade as sun. Rules-2 uses a modelled reference instead:

```
expected_clear(t) = K × cos(incidence(t)) + D
cos(incidence) = cos(sun altitude) × cos(sun azimuth − 180°)     (vertical, due south)
section is sun if more than half its minutes have  isc_avg > SUN_FRACTION × expected_clear(t)
```

- `K` comes from the existing calibration: `iref` divided by cos(incidence) at the moment it was taken. That moment is in the admin action log (4.3), so **no new calibration and no firmware change** are needed. Each year's pre-event calibration gives a new `K`; the tools use, for each day, the calibration in force on that day.
- `D` is a small diffuse-light floor, set once from an overcast day's data.
- The panels are packed out to face due south at installation ([hardware/GNOMON.md](hardware/GNOMON.md)), so the facing angle is 180° for all nine.
- Rules-2 works on the **1-minute sun log** (`isc_avg`), which firmware 6 keeps every day. Rules-1 counted the 10-second readings on the panel; outside the exhibition those are not stored, so rules-2 counts minutes instead.

Each SUNDIAL year keeps the rules it was drawn with; Sole is always rules-2, and every edition says so. **The SUNDIAL prints remain the only canonical artworks;** Sole editions are the record.

**What can honestly be said.** The panel measures **sunlight reaching this wall**, not energy produced: it is effectively unloaded (the board draws under 1 W from a 185 W panel). The figures beside the dials are therefore:

- **hours of direct sun** (sun sections × 0.25 h), the headline figure: *horas non numero nisi serenas*;
- first and last sun of the day;
- panel temperature, minimum and peak;
- time awake.

Never "kWh produced".

### 3.2 The fortnightly round

**When:** every second **Monday**, or any day soon after. A week (Monday to Sunday) is complete once Sunday's sunset has passed, so a Monday round collects **two complete weeks**: two editions. A partial current week waits for the next round.

**Slack:** the raw logs run at about 35–40 KB a day in summer, mostly the 1-minute sun log. With five event archives kept on the panel (4.4), about 1.1 MB is left for them: roughly **four weeks in summer**, longer in winter (shorter days, smaller logs). Firmware 6 prunes the oldest raw sessions only past that, so **one missed round costs nothing; two in a row lose data in summer.** The import tool reports any days that were pruned before collection.

**At each panel** (round key; Safari on iPhone or Chrome on Android, not the Wi-Fi pop-up, which cannot save files; about 3–5 minutes):

1. **Status:** clock, storage used, probe and sun sensor OK, sessions since the last visit.
2. **Clock nudge** if it has drifted (round key, up to ±5 min).
3. **Download all raw data.** Firmware 6 exports everything still held each time, up to about 2 MB, which takes some seconds over the panel's Wi-Fi. The import tool removes the overlap with earlier downloads.
4. **Quick physical check:** clean the glass, look at the gnomon, wall plate and box seal.
5. **One line in the round log:** date, panel, OK or the issue found.

About an hour for the trail; 26 rounds a year.

**After the walk:**

1. Copy the nine downloads into PVA's private raw archive (dated, never edited).
2. Run the import tool: merge, remove overlaps, cut into days.
3. Run the edition tool for each newly completed week.
4. Commit the new edition data and push: GitHub Pages updates the Sole tab.

The raw downloads stay private with PVA. The public repo receives only the derived data needed to draw the editions.

### 3.3 The website pages

**Navigation:** About · Bosa 2027 · Map · Sun (Sole, in Italian) (README, The website). The year's SUNDIAL sheet appears on the Bosa page; a preview on invented data is there and in `sun.html` until these pages are built.

**SUNDIAL** (`docs/sundial/YEAR/`): one page per event, the canonical sheet as a web page, 9 × 7 dials with title and dates. Tap a dial for that day's figures and the chosen lines from that panel's book. Built during the run from the daily walks, frozen after the final walk. `docs/sundial/` lists the years, newest first.

**Sole** (`docs/sole/`):

- **The latest edition first:** 63 dials, nine panels across (same order as the map) by seven days down (Monday to Sunday). Title "SUNDIAL Bosa · Sole", the edition number, the ISO week and its dates.
- **Tap a dial** for the day: sun hours, first and last sun, temperature minimum and peak, time awake.
- **Under the grid:** the week's sun hours per panel, as nine figures, and the sunniest and shadiest wall of the week.
- **Earlier editions:** a list by week, newest first, each opening the same view. Two new editions appear after each round.
- **Numbering:** *Sole n. 1* is the first full week after SUNDIAL 2027, then one number per week, with no gaps: a week with no data at all still gets its number and shows nine outlines.
- **Event weeks are in Sole too,** drawn by rules-2 like every other week, so the record has no hole. The edition notes that SUNDIAL ran that week and links to its sheet.
- Italian and English, like the map.

### 3.4 Tools and data

| Item | What | Size |
| --- | --- | --- |
| `tools/pva_import.py` | Round downloads → per-panel, per-day records. Removes overlaps across downloads, keeps the calibration moment from the action log, reports pruned or missing days. This is the "import script" already on the README's to-do list, extended | M |
| `tools/sole_edition.py` | Per-day records → one week's edition: rules-2 sun sections, heat curve, presence, sunrise and sunset, day figures. Writes `docs/data/sole/YYYY-Www.json` and updates `docs/data/sole/index.json` | M |
| Rules-2 in `tools/pva_rules.py` | The seasonal threshold beside rules-1, selected by version, so the same drawing code serves the print, the SUNDIAL page and Sole | S |
| `docs/sole/index.html` | Draws the editions in the browser from the JSON, with the same dial code as the panel page | M |
| `docs/sundial/YEAR/index.html` | Each year's SUNDIAL sheet, from that event's downloads and chosen book lines | M |
| Map awake windows | `pva_import.py` also writes each panel's usual awake hours per month into the map's `PANELS` list, replacing the hand-typed `window` values in `docs/map.html` | S |
| Round log | A simple CSV kept by PVA: date, panel, status, issue | — |

**Public data per edition** (about 30–60 KB): for each panel and day, the 15-minute sun sections, the 5-minute temperatures, visitors per solar hour, sunrise, sunset and the day figures. Nothing else from the raw logs is published.

**Optional later:** a print-ready PDF of any edition from `pva_rules.py`, for small weekly prints or a yearly book of editions.

**Storage between rounds:** each year's SUNDIAL archive (4.4) takes about 150 KB of flash from the raw-log buffer. With the limit of five events, the buffer stays at about four weeks in summer, twice the fortnightly round.

---

## 4. Layer 3 — the annual event

**Purpose:** once a year, for about seven days, each panel's day of sun becomes a dial drawn live on the visitor's phone and sealed at Bosa's sunset. The 63 dials of the week make the year's canonical four-colour screen print. Visitors can leave a line in each panel's book. **SUNDIAL · La Meridiana 2027** is the first.

### 4.1 The event as built

Largely built in firmware 6.1 and `index.html`:

- **Sunset:** the seal is at Bosa's sunset (`sunTimes`). Each panel's own sun and shade, including early shade, is recorded per 15-minute section from the short-circuit current. A panel in shade before sunset loses nothing; its shade is drawn as blue.
- **After sunset:** twilight mode (80 MHz, 2 dBm) serves the sealed image on the last light. The map marks panels that stay awake in twilight.
- **Presence:** phones on the Wi-Fi are counted per solar hour (a salted hash kept in RAM for one hour); only counts are kept.
- **Storage:** LittleFS only. No SD card is needed.

**Changes for firmware 6.2 (frozen by May 2027, then changed only for bugs or at an annual visit):**

| Change | Why | Size |
| --- | --- | --- |
| **Security** (4.3): challenge-and-response login, two derived keys, lockout, action log | The admin key currently travels in clear on an open network | S–M |
| **The visitors' book** (4.2) | Visitor interaction at very little extra cost | S–M |
| **Rules version check:** firmware, page and `pva_rules.py` all report the year's rules (`rules-1` for 2027), and the import tool refuses data that doesn't match | The print and the live dial must be the same drawing | S |
| **Between events:** outside the window, the panel page shows the archive of past events (4.4) and no longer offers "today" | The panel's public face for the rest of the year | S |
| **Archive by year:** `/art/` days and chosen book lines kept per event; the oldest event is removed when the setup key sets a new event beyond the limit of five (4.4) | Annual events accumulate | S |
| **Pages built into the firmware:** `index.html`, `admin.html`, the panel's title and the map address compiled in (gzipped, about 10 KB). LittleFS holds data only | A yearly update then flashes the firmware alone and never touches the archive or uncollected logs. Uploading a LittleFS image would wipe them | S |
| **No visitor clock-setting** when the clock module is fitted: `/sync` is ignored. A panel that has lost its time (dead coin cell) records undated data and waits for the round | Otherwise any passer-by could misdate a whole day | S |
| Import script and separations script | Already on the README's to-do list | M |

### 4.2 The visitors' book

**What the visitor sees.**
- Under today's dial is a short form: one line for the panel (up to 140 characters) and an optional first name or town (up to 30 characters).
- A notice under the form: *"This panel's book is read tomorrow. Chosen lines appear here beside the day's dial, and on the SUNDIAL website."*
- Past days in the gallery show their dial with that day's chosen lines. A day not yet read shows the dial alone.

**The day's rhythm.** It is the same as the dial:

| When | What happens |
| --- | --- |
| Day N, sunrise to sunset | Visitors write. Entries are kept on the panel, unseen by anyone |
| Day N, sunset | The book closes with the seal. The form disappears; nothing more is added to day N |
| Day N+1, any time the panel is awake | The admin opens day N's book on the admin page, ticks the lines to show and saves, like clearing an inbox. Then the download is taken |
| During the run | Nothing is deleted. Unticked lines stay hidden on the panel; ticked lines are shown beside day N's dial (4.3) |
| After the walk | The website's exhibition page is updated with the same ticked lines, so panel and site always match |
| The morning after the last day | One final walk reads the last book, while the panels are still up |

**Nothing new is uploaded to the panel.** The admin only sends back a list of which entries to show, and every one of them is already on the panel. The dial is never re-sent either; it is drawn from data the panel already holds.

**Rules:**
- **Select, never edit.** A line is shown as written or not at all.
- **One entry per phone per day per panel,** enforced by the same in-RAM salted hash as presence. It is never written anywhere and is wiped at night. This is a soft limit, which is enough here.
- **Cap per day:** about 200 entries per panel. After that the form says the day's book is full.
- **Only while the clock is known** and inside the exhibition window, so every entry belongs to a dated day.
- **Text only.** Control characters are stripped. Lines are always shown as text (`textContent`), never as HTML, on the visitor page, the admin page and the website, so nobody can inject markup.

**Firmware:**

| Item | Detail |
| --- | --- |
| `POST /book` | Plain HTML form, no JavaScript needed (works in every captive-portal browser). Returns a short thank-you page. Refused after sunset, outside the window, when the day is full, or when this phone has already written today |
| Raw entries | `/book/DATE.csv`: `id, epoch, name, text`. **Not under `/art/`**, which is served publicly by `serveStatic` |
| Chosen lines | `/art/DATE.book.json`: written by the panel when the admin saves a selection; public, beside the day's other `/art/` files |
| `GET /admin/book?day=` | Day N's entries, behind the admin login |
| `POST /admin/book` | Day and the list of chosen ids. Writes `DATE.book.json`. The admin can change the selection at any time during the run |
| Export | Adds a "visitors' book" section with all raw entries, so the archive and catalogue have the whole book |
| `POST /admin/book/clear` | **Setup key only,** and only after the exhibition window has ended: deletes all raw entries in `/book/`, on the final walk, once the last download is saved. The ticked lines in `/art/` stay |
| `/art/list` | Says which days have chosen lines, so the gallery knows what to fetch |

**Pages:**
- `index.html`: the form under today's dial, while open; chosen lines under each gallery day.
- `admin.html`: a "Book" section with one checkbox per entry, newest first, a count, and **Save selection**.
- The website's exhibition page: each day's chosen lines from the downloads, added by the import script.

**Storage:** 200 entries × about 200 bytes × 7 days is under 300 KB in the worst case, and much less in practice. It fits in LittleFS beside the dial data; no card is needed.

**Privacy:**
- The visitor writes; the panel keeps no one. No identifier is stored.
- The optional name is the only personal detail, and the visitor chooses to give it.
- Unchosen lines stay hidden on the panel until the final walk, then are deleted. Chosen lines stay with the year's archive.
- The full book lives only in the downloads, kept by PVA for the archive and catalogue.
- The download crosses the open Wi-Fi in clear. For a 7-day run this is an accepted risk.

**Its place in SUNDIAL:** the visitors' book is the project's only way for people to talk back, and it belongs to the event. Between events the panels take no input at all.

### 4.3 Security: protecting the artwork from the admin side

**The risk.** In firmware 6.1 every admin call carries the key in the web address (`?key=…`), over plain HTTP, on an open network. Anyone nearby capturing Wi-Fi traffic during the round could read it. So could anyone running a fake `panel-0N` network that the walker joins by mistake.

With the key, a person could:
- reset the clock, so a day seals at the wrong time or lands on the wrong date;
- change the exhibition dates, ending the run or stopping days being recorded;
- recalibrate the sun sensor with a bad reading;
- download raw data;
- read unread comments, or change or delete the book.

**What the hardware already rules out.** There is no update path over Wi-Fi, so nobody can replace the firmware or the pages remotely. Taking over a panel needs the box opened and a USB cable. The worst remote outcome is damaged days on the panel, not a hijacked artwork.

**What protects the print regardless.** The raw 5-minute and 1-minute logs are kept apart from the dial files, and no admin call deletes them. Any damaged day can be redrawn faithfully from raw data by `pva_rules.py` for the print and the website. Only the live display of that day is at risk.

**Measures (firmware 6.2):**

| Measure | What it does | Effect on the walker |
| --- | --- | --- |
| **Challenge and response** | `GET /admin/nonce` gives a one-time number, valid for 60 s. Each admin call carries an HMAC-SHA256 of key + number + exact action + parameters. The key never travels, so listening or a fake network captures nothing reusable, and a captured answer works once, for one action. HMAC is written in plain JS in `admin.html`, because WebCrypto is unavailable on `http://192.168.4.1` | None: the page does it |
| **Two keys** | **Round key:** status, download, the book's tick boxes, and clock corrections of up to ±5 minutes. **Setup key:** clock beyond ±5 min, exhibition dates, sun calibration, clearing the book after the run. Once the run starts, nothing reachable with the round key can break the dial | None on the daily walk; the setup key stays at home |
| **Keys derived from masters** | Each panel's key = HMAC(master, panel name), for both the round master and the setup master. Panels still each have their own key (one panel's key opens no other), but the walker carries one round master and the admin page derives each panel's key from the name it reports | Easier: one key for the trail instead of nine |
| **No deleting during the run** | Raw comments stay until the final walk (4.2). Raw logs are never deleted by any admin call | Easier: no daily "close" step |
| **Rate limit and lockout** | One attempt per second; after 5 wrong answers the admin side closes for 10 minutes. Brute force becomes impossible; the worst a nuisance can do is delay the walker | Only if a wrong key is typed |
| **Action log** | `/log/admin.csv`: time, key used (round or setup), action, parameters, result. Included in every download, so tampering is visible the next day and can be undone from raw data | None |
| **Long random masters** | At least 128 bits, generated, kept off the repo. Each panel holds only its own two derived keys (in `panel_config.h`, compiled in); the masters are never stored on a panel | None |
| **Where the masters live on the walker's phone** | All nine panels share one web origin (`192.168.4.1`), so a remembered key works on every panel, and a fake network at the same address could read it silently. Rule: **the round master may be remembered by the browser; the setup master is always typed and never stored.** A stolen round key can only download, tick book lines and nudge the clock by ±5 minutes; nothing it opens can damage the dial | The round master is entered once; the setup master is typed at the yearly visits |
| **Tamper screws** | Security screws on each box, so the USB port behind the panel can't be reached casually. Boxes are opened once a year, at the pre-event visit (4.4) | A special screwdriver bit when a box is opened |

**What remains possible, and accepted.** Jamming the Wi-Fi; occupying all 10 connections; a fake network showing visitors a fake page. An open network cannot prevent these, none of them touches the stored artwork, and each ends when the person leaves.

**Visitor side** (from 4.2): book entries are always shown as text, never as HTML; one entry per phone per day; 200 per day per panel.

### 4.4 The annual cycle

| When | What |
| --- | --- |
| **Spring** | **Annual visit** (setup key, tamper bit). First take a full download from each panel, so nothing uncollected can be lost. Then open each box: flash the new firmware **only** if something changed for the year (rules, title, theme), never erasing flash or uploading a LittleFS image, so the archive and logs stay; check the supercaps, the coin cell, the probe and its cable, the box seal and vent; clean the glass. Set the new exhibition dates; if that takes the panel beyond five events, the oldest is removed from the panel (it stays on the website). This is the only time in the year the boxes are opened |
| **The two weeks before the event** | **Calibration** (setup key, over Wi-Fi, no box opening): on a clear day near solar noon, tap Calibrate on each panel. rules-1 needs a reference from the event's own season; a spring reading would be too high and draw June sun as shade |
| **The event week** | Daily walk: status, download, the book's tick boxes (4.2). The website's SUNDIAL page for the year builds up day by day |
| **The morning after the last day** | Final walk: last book read, final download, raw book entries cleared (setup key) |
| **After the event** | The year's print: canonical sheet, separations, screens; prints sold by the print shop. The SUNDIAL page for the year is frozen |
| **All year** | Sole: the fortnightly round and two editions per round (section 3) |

**Per year:**
- **One name and one rules version.** Each event states which rules drew it. 2027 is `rules-1`. Later years may keep it or change it; a sealed year never changes.
- **One print, one website page, one panel archive entry.**
- **Panel archive:** the page shows the latest event first, earlier events below. During the event the raw book can reach 300 KB; after the final walk it is cleared, and the event keeps only its dial files and chosen lines, about 150 KB with LittleFS's 4 KB minimum per file. **The panel keeps the last five events (about 0.75 MB);** the website keeps them all.
- **First installation only:** the README's "erase all flash" step is for a new board, before any data exists. It is never used at an annual visit.

---

## 5. Permissions and upkeep

SUNDIAL is a **permanent installation**: a sundial and monitor all year, with an event once a year. That is a different request from a seven-day exhibition, and it needs settling before installation.

**Permissions:**
- **Wall owners:** written consent for each site, for a permanent installation that may grow into SUNSET in year 2 ([GROWTH.md](https://github.com/photovoltaic-art/PVA/blob/main/GROWTH.md)), with access for the fortnightly round and the yearly visit, and the right to remove.
- **Comune and heritage authorities:** authorisation for permanent fixtures in the centro storico. This is the most likely obstacle; raise it first, with the sundial as the lead: a public timepiece on a recycled panel, no visible electronics, no advertising.
- **The framing that may help:** a *patto di collaborazione* under a regolamento per l'amministrazione condivisa dei beni comuni, if Bosa has adopted one (check the Labsus register). The panels would be a sundial trail cared for by PVA alongside the Comune.
- **Public liability insurance** for objects fixed to walls above a street; the gnomon projects about 35 cm.
- **A panel on a post** (private ground, no suitable wall) needs the ground owner's consent, a structural sign-off and, in a protected area, possibly the comune's or the Soprintendenza's agreement ([hardware/POST.md](hardware/POST.md) 6).

**Upkeep, per year:**

| Item | Interval | Note |
| --- | --- | --- |
| Glass | Every round | Clean; dirt lowers the sun current and shifts the record |
| Supercaps | Check yearly; replace about every 3–5 years | They age fastest in heat; behind a panel in a Sardinian summer, expect the short end |
| Coin cell (CR2032) | Check yearly; replace about every 5 years | A dead cell means undated days until the round |
| Box seal, vent, glands | Yearly | IP65 box; check for water and insects |
| Probe and cable | Yearly | Sun and heat on the panel back |
| Gnomon, lines and marks, fixings | Yearly, and after storms | Stainless M6; check torque, that the noon shadow still falls down the noon line, and that no tape is lifting |
| Wall plate | Every round | Number and QR code legible |
| Panel | As needed | A failed panel or board is replaced; the day lost shows as the outline |
| Post and USB sockets (post panels only) | Every round; base yearly | Sockets and caps intact; base fixings tight ([hardware/POST.md](hardware/POST.md)) |

**Spares held by PVA:** one complete carrier board with ESP32 and buck converter, flashed and keyed as a spare; supercaps; coin cells; a probe; fixings.

---

## 6. Build order

| Step | Contents | When |
| --- | --- | --- |
| Permissions | Wall owners, Comune and heritage, insurance (section 5) | Before anything is fixed to a wall |
| Firmware 6.2 | Security, visitors' book, rules version check, between-events archive, archive by year, pages built in, no visitor clock-setting | On the pilot panel first; frozen by May 2027 |
| Event tools | Import script (daily walk → SUNDIAL page), separations script, `docs/sundial/2027/` | Before the run |
| Calibration | Each panel, clear day near solar noon (4.4) | The two weeks before the event |
| **SUNDIAL 2027** | The first event | Summer 2027 |
| Sole tools | `pva_import.py` extended (including the map's awake windows), `sole_edition.py`, rules-2 in `pva_rules.py`, `docs/sole/` | From the first full week after the run; no panel changes |
| Every year after | The annual cycle (4.4) and upkeep (section 5) | Spring visit, calibration, summer event, fortnightly Sole all year |

## 7. Settled

| Question | Answer |
| --- | --- |
| Timekeeping | DS3231 with coin cell, corrected on the round; visitors never set the clock |
| After-sunset serving | Twilight mode on the remaining daylight; the supercaps only bridge seconds |
| Visitor tracking | Counts only; a salted hash in RAM, wiped at night. The panel keeps no one |
| Visitor input | Only the event's visitors' book: select, never edit; one person ticks the boxes |
| Admin security | Challenge and response, round and setup keys, lockout, action log, tamper screws; setup master never stored on a phone |
| Yearly updates | Firmware only, with pages built in; never erase flash or upload a LittleFS image; full download first |
| Calibration | In the two weeks before each event; Sole uses the calibration in force on each day |
| Monitoring | Sole on the website, weekly editions of 63 dials, rules-2, fortnightly round, run by PVA |
| What the panel claims | Sun hours and temperature, never energy produced |
| Notice board, structured feedback, service firmware | Dropped: outside the core proposition |

---

## 8. Beyond SUNDIAL: the battery tier

Carrier v1 also runs a second kind of node, **unchanged**: an **interactive node** for SUNSET (PVA no. 2, formerly GO TO BED), powered from a 12 V LiFePO₄ battery and a Victron SmartSolar MPPT 75/15 instead of straight from its panel. **The power tier follows the load, not the role:** a node that only serves pages stays a wall node; a node that moves, flips, lights or releases something is an interactive node.

| | Wall node (SUNDIAL) | Interactive node |
| --- | --- | --- |
| Panel connects to | Carrier J1 | MPPT → battery → MPPT load output → carrier J1 |
| JP1 | On | **Off, and the sun sensor compiled out:** Q1 would otherwise short the battery |
| Sun reading | Short-circuit current (light) | Victron PV power over VE.Direct on J10 (energy harvested) |
| GPIO 34 reads | Panel voltage | Battery voltage |
| Firmware | Wall build | Interactive build |

**Year 2:** under PVA's growth model, SUNDIAL's own nine panels become SUNSET's nodes at the spring visit: four as wall nodes by a firmware update, five as interactive nodes on this battery tier. The gnomons stay, so the sundials outlive the change; Sole carries on if each interactive node has a reference sun sensor ([GROWTH.md](https://github.com/photovoltaic-art/PVA/blob/main/GROWTH.md)). **So the year-1 site plan chooses each panel's site for its year-2 role too**, and the permissions request says the panels may grow into SUNSET.

One board, two wirings, two firmware builds; the jumper says which. SUNSET, its nine panels and the full battery-tier specification are in their own repository: **[photovoltaic-art/sunset](https://github.com/photovoltaic-art/sunset)** (start with SUNSET.md; the tier is in battery-tier.md). Nothing in it affects SUNDIAL.
