# SUNDIAL — making the repo forkable

**Goal:** any town can fork this repository and run its own SUNDIAL (sundial, Sole and an annual event) without asking anyone, and without hunting through the code for Bosa.

> Status: task list, 20 Oct 2026. **State: Visible** — public but not yet licensed for reuse. **Released** when every task is done, the system has been field-tested at SUNDIAL 2027, and the licences are added (the last step). Assumes the firmware 6.2 and tools specified in [SUNDIAL.md](SUNDIAL.md). Bosa remains the reference instance.

---

## Summary

**The one rule:** a SUNDIAL is **nine panels**. A fork may make its own single-panel artist's proof to test and show with, outside its edition, as Bosa's is (PVA GROWTH.md, the path). Everything else (the town, the walls, the event's name and dates, the languages, the stories) belongs to the fork.

**The one request:** a link back to this repository, wherever the fork is presented: its website, flyer and wall plates. It is a request, not a licence condition.

**The model:** fork and run separately. Each town has its own repository, website, keys, data and print. There is no central server and no network between towns. Improvements can be offered back, but nobody has to.

**What stands in the way today:**

1. **Bosa is built in.** Coordinates, time zone and the dial's day-length scale are written into four places (firmware, `pva_rules.py`, the panel page, the map), plus Bosa text in the tools.
2. **One panel model.** The carrier is sized for the Trina 185 W; other end-of-life panels need a compatibility check.
3. **One latitude.** The sundial drawings are calculated for 40.3° N.
4. **No guide.** The knowledge needed is spread across README, SUNDIAL.md, CARRIER.md and hardware/GNOMON.md, with Bosa's texts but no templates.
5. **No safe key set-up.** Nothing stops a copier from installing the example keys.

**The fix, in one sentence:** move everything that belongs to Bosa into **one folder (`site/`)**, make every part of the system read from it, add a guide, check automatically that no Bosa remains outside that folder, prove it in the field, and only then add the licences.

The repo has no licence yet, so nothing in it may legally be reused. That is deliberate until release.

---

## Checklist

### 1. Work-in-progress notice

- [x] One line at the top of the README: *"Work in progress. Not yet licensed for reuse; a forkable release is planned after field testing at SUNDIAL 2027."*

### 2. One site folder

Everything town-specific moves into `site/`. A fork replaces this folder and nothing else.

- [ ] `site/site.json` — the single source:
  - town name, project title, event name
  - latitude, longitude, time zone (POSIX string for the firmware and IANA name for the website)
  - wall facing: south in the northern hemisphere, north in the southern
  - the nine panels: number, name, Wi-Fi name, map position, wall direction
  - languages (first language and second)
  - website address and the acknowledgement link
- [ ] `site/texts/` — the town's introduction and legend, print enquiry, notices (Bosa's current `texts/` moves here).
- [ ] `site/plates/` — wall plate artwork (number, QR code, acknowledgement line).
- [ ] **Remove constants from code:**
  - [ ] firmware: `LAT`, `LNG`, `TZ_INFO` come from a generated `site_config.h` (2.1)
  - [ ] `tools/pva_rules.py`: reads `site.json`
  - [ ] panel page and map: read the site values (the panel page already receives `lat`/`lng` from `/art/list`)
  - [ ] `sample_a4.py`, `poster_mockup.py`: town name, dates and languages from `site.json`
- [ ] **The dial's scale is calculated, not typed:** the longest day of the year (solstice day length) is computed from the latitude, replacing Bosa's fixed 15 h 03 m in three files. At 40.3° N it gives 903 minutes, so Bosa's dials are unchanged.
- [ ] **Southern hemisphere:** the sun model, the rules-2 incidence formula and the dial direction follow the hemisphere from `site.json`.

**2.1 Generated config.** `tools/site_build.py` reads `site.json` and writes:
- `firmware/panel_page_server/site_config.h` (coordinates, time zone, titles, languages)
- the `PANELS` list and map centre for `docs/index.html`
- the website's titles and footer

Generated files are marked "do not edit" and rebuilt by one command.

### 3. One image, nine panels

**Keep it simple:** SUNDIAL has no money in it, so nothing on a panel is worth much to a thief beyond its admin keys. It keeps its light security (SUNDIAL.md 4.3) and borrows none of SUNSET's.

**One firmware image for all nine panels.** The town's values (from `site.json`) are compiled in; **the panel's identity is not.** Its name and two keys are written to its flash once, at installation, so the first and the ninth panels run the very same file, and a fork has one build to check, not nine.

- [ ] Move the panel name, Wi-Fi password and admin keys out of `panel_config.h` into a small settings area in flash (NVS).
- [ ] `tools/pva_keys.py`:
  - generates the round master and setup master (128-bit, random)
  - derives each panel's two keys from the panel names in `site.json`
  - writes nine small settings files to a folder outside the repo
  - prints the masters once, for the operator to store
- [ ] `tools/pva_provision.py`: writes one panel's settings to its flash over USB, one command at installation; reads back the name to confirm.
- [ ] The firmware **refuses to start** (a clear notice on the serial port and the panel page) with no settings, the example key (`change-me`) or an empty key.
- [ ] `.gitignore` covers settings files, key folders, raw downloads and round logs (already partly there).

### 4. Reproducible build

- [ ] `tools/build.sh` (arduino-cli): pinned ESP32 core version, pinned library versions (OneWire, DallasTemperature, RTClib), board settings, partition table. One command builds **the one image** for the town.
- [ ] `firmware/VERSIONS.md`: firmware version, rules version, the core and library versions it was tested with.
- [ ] A **tagged release** for each tested firmware (the first: the version used at SUNDIAL 2027), so a fork can build exactly what was proven.

### 5. Hardware for any panel and any latitude

- [ ] **Carrier design files in the repo:** KiCad project, schematic PDF, BOM with part numbers, Gerbers and pick-and-place files, under `hardware/carrier/` once drawn (CARRIER.md already asks for them to be handed over).
- [ ] **Panel compatibility table** in CARRIER.md:
  - open-circuit voltage up to 50 V (board rated 60 V; cold mornings add about 10 %)
  - short-circuit current ranges and the shunt or gain to use for each, so the sun reading stays within the ESP32's input range
  - frame depth and size limits for the sundial fixings
- [ ] `tools/sundial_template.py`: from latitude and panel size, prints the **gnomon angle** (90° − latitude), the **hour-line angles**, and a **drilling template** to scale (PDF), the same tables SUNDIAL.md gives for Bosa.
- [ ] SUNDIAL.md: the Bosa figures stay as the worked example; a short section explains the southern-hemisphere mirror (wall faces north, morning on the right).

### 6. Website

- [ ] `docs/` works for any town from the generated site values: map, SUNDIAL pages, Sole.
- [ ] README: publishing the fork's own site with GitHub Pages, and an optional own domain.
- [ ] The acknowledgement link in the footer, ready to switch on at release (§10).

### 7. The guide and templates

- [ ] **`REPLICATE.md`** (Italian and English), in the order a town works:
  1. Find nine end-of-life panels (sources; the compatibility table)
  2. Choose nine walls (facing, shade, Wi-Fi reach, access)
  3. Permissions (wall owners, Comune and heritage, insurance)
  4. Fork, fill in `site.json`, run `site_build.py`
  5. Order or build nine carrier boards
  6. Generate keys, build and flash
  7. Build the sundials, install, wall test
  8. Calibrate in the two weeks before the first event
  9. The first event: daily walks, the book, the print
  10. Sole: the fortnightly round, all year
  11. Every year: the spring visit and the annual cycle
- [ ] `templates/` (Italian and English, fill-in-the-blanks):
  - [ ] wall-owner consent letter
  - [ ] request to the Comune and heritage authorities
  - [ ] privacy notice for the visitors' book (the local operator is responsible for it)
  - [ ] print-shop enquiry (from Bosa's)
  - [ ] event introduction (structure only; the story is the town's own)
  - [ ] wall plate
- [ ] A **cost and time sheet**: parts per panel, board order, fixings, print, and the hours for building, installing, each round and each event. *Costs drafted for Bosa, 25 Oct 2026: [budget/SUNDIAL-budget.xlsx](budget/SUNDIAL-budget.xlsx); the hours are still to add.*

### 8. Checking it works

- [ ] **Automatic check (GitHub Actions)** on every push:
  - [ ] build the firmware with the pinned versions
  - [ ] run the tools on invented data (the desk test's `BENCH_FAKE` output) and build a sample SUNDIAL page and Sole edition
  - [ ] **search for Bosa leakage**: Bosa's coordinates or name anywhere outside `site/` fail the check
- [ ] **Fork rehearsal:** fork to a test repository, fill `site.json` for a different town and latitude (one northern, one southern), build everything, run the desk test, and confirm the dials, map and sundial template are right with no Bosa in sight.
- [ ] Fix whatever the rehearsal finds.

### 9. Field test

- [ ] SUNDIAL 2027 run on the forkable structure (§2–§4 in place), plus at least one full Sole cycle.
- [ ] Fixes from the field test applied; the tested firmware tagged (§4).

### 10. Release: licences and the request (last)

Only when every item above is ticked and the field test (§9) is done.


- [ ] `LICENSE` — **code** (firmware, tools, website): **MIT**. Permissive, matches "a request, not a condition".
- [ ] `hardware/LICENSE` — **hardware** (carrier board, sundial drawings): **CERN-OHL-P v2** (the permissive open hardware licence).
- [ ] `texts/LICENSE` — **texts, dial rules as artwork, images**: **CC BY 4.0**. Credit can be given by the link back.
- [ ] README section **"Licences and the one rule"**: which licence covers what; the nine-panel rule; the link request.
- [ ] `ACKNOWLEDGEMENT.md` — the requested link and a suggested line in Italian and English, e.g. *"Based on SUNDIAL, a work of PVA (Photovoltaic Art) — photovoltaic.art · github.com/photovoltaic-art/SUNDIAL"*, with where to place it: website footer, flyer, wall plate text.
- [ ] The acknowledgement line built into the website footer and the panel page by default, so a fork keeps it unless it removes it.

**Note:** licences cannot enforce a panel count. The nine-panel rule is stated in the README as the definition of a SUNDIAL; a fork with another number is free to exist, but is not a SUNDIAL.

- [ ] README: replace the work-in-progress notice with **"Licences and the one rule"** and a line saying the repo is forkable.
- [ ] Tag **v1.0**: the field-tested version.

### 11. Optional

- [ ] `CONTRIBUTING.md`: how to offer an improvement back (issue or pull request), and what is in scope (bugs, panel compatibility, translations).
- [ ] A **list of towns** in the README, for forks that send their link, so the instances can find each other without being networked.

---

## Order of work

| Step | Tasks | Why in this order |
| --- | --- | --- |
| 1 | Work-in-progress notice (§1) | Says clearly that the repo is visible but not yet reusable |
| 2 | Site folder, generated config, calculated scale (§2) | The core change; everything else reads from it |
| 3 | Keys and build (§3, §4) | Safe and repeatable panels |
| 4 | Hardware files, compatibility table, sundial template (§5) | Needed before another town orders parts |
| 5 | Website and guide (§6, §7) | The town-facing part |
| 6 | Automatic check and fork rehearsal (§8) | Proof that the structure works |
| 7 | Field test (§9) | Proof that the system works |
| 8 | **Release: licences, acknowledgement, v1.0 tag (§10)** | Last: the licences are what make the repo forkable |

Steps 1–3 can be done before SUNDIAL 2027 without touching how Bosa runs.
