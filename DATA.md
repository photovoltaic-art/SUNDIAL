# SUNDIAL data: the panel as a long-term logger

> Status: draft 1, 25 Nov 2026. Builds on the logger layer in [hardware/MVP.md](hardware/MVP.md), section 9.

Every SUNDIAL panel keeps a record of what the weather was like at its wall: sun, air temperature, humidity, pressure, and the panel's own heat and voltage. The record is **historical, not live**. It is collected on the fortnightly round, archived openly, and shared with every other SUNDIAL through **openSenseMap**. Anyone can browse and download it on the website.

---

## 1. Principles

1. **The panel's card is the original record.** Everything else is a copy: the archive, openSenseMap and the website. If a copy is lost, it can be rebuilt from the card or the archive.
2. **Store raw readings, never results.** Dew point, daily figures and the dial are worked out later, by tools anyone can rerun.
3. **Use standard names and units.** Columns are named after the **CF Conventions standard names**, with SI units and UTC times. Any climate tool can read the files without a translation table.
4. **Open by default.** The data is published under the **ODC Public Domain Dedication and Licence (PDDL) 1.0**, the same licence openSenseMap uses for everything it holds, so one rule covers every copy.
5. **No visitor data leaves the panel's own records.** Wi-Fi visit counts and the visitors' book belong to the artwork (SUNDIAL.md), not the weather record. They are never sent to openSenseMap.

## 2. The path of the data

```
panel card (raw, 1 minute, years)
   │  fortnightly round: admin download of a date range
   ▼
pva_import.py (on the collector's laptop)
   ├─► checks: SHA-256 of each day, gaps, values out of range (flagged, never deleted)
   ├─► archive: the public data repo, 10-minute values per panel and day
   ├─► openSenseMap: the same 10-minute values, one box per panel
   └─► website: static JSON for the Sun page and the Data page
once a year: the full raw year → Zenodo (a DOI for each town's year)
```

## 3. On the panel's card

### 3.1 Files

```
/station.json                 the panel's description (3.3)
/log/2027/06/21.csv           one file per day, one row per minute while the panel is awake
/log/2027/06/21.sha256        written at the dusk close; a missing hash means the day did not close cleanly
/log/admin.csv                the existing admin action log, copied here too
```

Each line is appended and the file closed after every write (MVP.md 9.2). A day that lost power before dusk keeps every line written so far; only its hash is missing, and the import tool reports it.

### 3.2 Columns (the 1-minute raw log)

| Column | CF standard name, or a SUNDIAL name where CF has none | Unit | From |
| --- | --- | --- | --- |
| `time` | `time` (ISO 8601, UTC, `2027-06-21T05:31:00Z`) | — | DS3231 |
| `sun_rel` | `sundial_relative_irradiance` (SUNDIAL): the reading divided by the calibrated clear noon | 1 (0 to about 1.2) | Sun cell (KXOB25) |
| `sun_raw` | `sundial_reference_cell_current` (SUNDIAL) | A | Sun cell (KXOB25) |
| `t_air` | `air_temperature` | K in the file; °C on the website | SHT-30 |
| `rh_air` | `relative_humidity` | 1 (0–1) in the file; % on the website | SHT-30 |
| `p_air` | `air_pressure` (at the station, not reduced to sea level) | Pa | BME280 |
| `t_panel` | `sundial_panel_back_temperature` (SUNDIAL) | K | DS18B20 |
| `v_panel` | `sundial_panel_voltage` (SUNDIAL), close to open circuit | V | Divider |
| `t_box`, `rh_box` | `sundial_enclosure_temperature`, `sundial_enclosure_relative_humidity` (SUNDIAL) | K, 1 | BME280, maintenance only |
| `flags` | Problems found by the firmware, e.g. `sht_err`, `bme_err`, `brownout` | text | Firmware |

**Kelvin and fractions in the file, °C and % on screen.** The file follows CF strictly so that conversion happens once, in the import tool, never by hand.

Missing values are empty fields, never zero. Every SUNDIAL-specific name is defined in this table, and the table is the contract: a fork may add columns at the end but never rename or reuse one.

### 3.3 station.json

```json
{
  "station_id": "bosa-03",
  "town": "Bosa",
  "edition": "SUNDIAL",
  "lat": 40.2981, "lon": 8.4987, "elevation_m": 12,
  "mount": { "surface": "wall", "azimuth_deg": 180, "tilt_deg": 90, "height_m": 2.4 },
  "panel": { "model": "Trina TSM-185DC01", "installed": "2027-05-01" },
  "sensors": [
    { "column": "t_air,rh_air", "model": "SHT-30 (Adafruit 4099)", "shield": "8-plate, ASA", "height_m": 2.0, "wall_distance_m": 0.15 },
    { "column": "p_air,t_box,rh_box", "model": "BME280", "position": "enclosure" },
    { "column": "t_panel", "model": "DS18B20", "position": "panel back, centre" },
    { "column": "sun_rel,sun_raw", "model": "ANYSOLAR KXOB25-05X3F", "r_cell_ohm": 39, "position": "gnomon mount, beside the root" }
  ],
  "calibrations": [ { "time": "2027-05-20T11:02:00Z", "iref_A": 0.142 } ],
  "osem_box_id": "",
  "licence": "PDDL-1.0"
}
```

The location is the wall's, already public on the map. The file travels with every download, so the archive always knows which sensor made which reading, and where.

## 4. The import: pva_import.py

Already planned in SUNDIAL.md (3.4). For the logger it also:

- **Checks each day** against its SHA-256 hash and reports days without one.
- **Removes overlaps** between rounds (a day downloaded twice is kept once).
- **Flags, never deletes:** values outside physical limits (air −20 to 55 °C, humidity 0–100 %, pressure 900–1080 hPa), a sensor stuck on one value for an hour, jumps no weather can make. A flagged value stays in the raw archive and is left out of the public averages.
- **Makes 10-minute values** (the mean of the minutes in each block, only if at least 7 of the 10 are present). Ten minutes is the usual interval for weather-station records, and it is what openSenseMap and the website receive.
- **Keeps an upload log** (`uploads.csv`: panel, day, sent, response), so each day goes to openSenseMap once and only once.

## 5. The archive

| Where | What | Size |
| --- | --- | --- |
| **Public data repo** (`photovoltaic-art/sundial-data`, one folder per town) | 10-minute CSVs per panel and month, plus each panel's station.json history | About 1 MB per panel a year |
| **Zenodo**, once a year per town | The full raw 1-minute year, the hashes, the round log and the import tool's version | About 15 MB per panel a year |

The Zenodo deposit gives each town's year a DOI: a citable, permanent record that outlasts GitHub, openSenseMap and PVA.

## 6. openSenseMap: the network

**One openSenseMap box per panel.** A town's nine panels are nine boxes, all given the **group tag `SUNDIAL`**, plus the town's own tag (`SUNDIAL-Bosa`).

**The group tag is the network.** Any town that forks SUNDIAL and tags its boxes joins the network automatically. PVA runs no server and keeps no list, and anyone can find every SUNDIAL by the tag.

### 6.1 The box

| Field | Value |
| --- | --- |
| Name | `SUNDIAL Bosa 03` |
| Exposure | outdoor |
| Location | from station.json |
| Group tags | `SUNDIAL`, `SUNDIAL-<town>` |
| Description | One line and a link to the town's SUNDIAL page: what the panel is, and that its data arrives every fortnight, not live |
| Upload security | Box access token on (openSenseMap security setting) |

### 6.2 Sensors on each box

| Title | Unit | Type | From column |
| --- | --- | --- | --- |
| Air temperature | °C | SHT-30 | `t_air` |
| Relative humidity | % | SHT-30 | `rh_air` |
| Air pressure | hPa | BME280 | `p_air` |
| Sun (relative) | % | Sun cell (KXOB25) | `sun_rel` × 100 |
| Panel temperature | °C | DS18B20 | `t_panel` |

These use openSenseMap's usual titles and units (°C, %, hPa), so SUNDIAL boxes sit beside every other weather box on its map. The panel voltage and the box's own readings stay in SUNDIAL's archive only.

**"Sun (relative)" is not W/m².** It is a percentage of the wall's own clear noon, on a vertical wall. The sensor's description says so, so nobody mixes it with horizontal irradiance from other stations.

### 6.3 Upload

- `POST /boxes/{boxId}/data`, with an `Authorization` header carrying the box's access token. The body is a JSON array of `{ "sensor": <sensorId>, "value": <number>, "createdAt": <ISO 8601 UTC> }`, so each reading keeps its own time, however late it is sent.
- Sent in batches of one day per box, by pva_import.py after each round.
- **Check before building** against the live API documentation: the batch-size limit, any limit on how old `createdAt` may be, and the endpoint itself. openSenseMap is moving to a new platform (`beta.opensensemap.org`), so keep the uploader to one small function that can be changed in one place.

### 6.4 What openSenseMap is, and is not

- **A mirror and a meeting place:** the network's shared map, searchable by tag, downloadable by anyone, under the same PDDL licence.
- **Not the archive.** If openSenseMap closes or changes, SUNDIAL's record is untouched: re-upload from the archive to whatever replaces it.

## 7. The website

Two pages, both static, both forkable, no server:

| Page | What it shows | Built from |
| --- | --- | --- |
| **Sun** (exists, SUNDIAL.md 3) | This town's weekly editions of 63 dials, now with a small weather line under each dial: air temperature range, humidity, pressure trend | Static JSON made by pva_import.py |
| **Data** (new) | **The network map:** every box tagged `SUNDIAL`, in every town, fetched live from openSenseMap's public API (it allows browser requests). Click a panel: its station.json, a chart of any month, and download links (10-minute CSV from the data repo, the yearly raw file from Zenodo, the openSenseMap page) | openSenseMap API for the map; the data repo for this town's files |

Charts are drawn on the visitor's device, as the dial already is. Every chart says plainly: **"Historical record. Collected every fortnight. Not a forecast."**

## 8. For forks

A town that forks SUNDIAL:

1. Builds the panels with the logger layer (MVP.md 9).
2. Fills in each panel's station.json.
3. Creates nine openSenseMap boxes with the sensors in 6.2 and the tags `SUNDIAL` and `SUNDIAL-<town>`.
4. Runs pva_import.py with its own tokens, archive folder and Zenodo deposits.

It then appears on every SUNDIAL's Data page, Bosa's included, with no change anywhere else.

## 9. To do

- [ ] Firmware: the `LOGGER 1` build (MVP.md 5): card files, the columns in 3.2, the hash at dusk, a date-range download.
- [ ] `tools/pva_import.py`: checks, 10-minute values, archive, openSenseMap upload, upload log, website JSON.
- [ ] Create `photovoltaic-art/sundial-data` (PDDL licence file, one folder per town).
- [ ] Register the artist's proof as the first openSenseMap box; test a two-week back-dated upload.
- [ ] `docs/data.html`: the network map and the per-panel download page.
- [ ] Zenodo: a community or account for Photovoltaic Art; first deposit after the first full year.
