# Data accounts: setup checklist for later

Written 11 Oct 2026. Of the 12 sources in [dostep_do_zrodel_danych.xlsx](dostep_do_zrodel_danych.xlsx), none needs an account. Three things are needed only for the **two sources added later** (ionosphere maps and Starlink orbits) and for **DONKI used as validation**. Everything below is free. You create the accounts and send the email yourself.

| # | What | Unlocks for the thesis | Needed when | Effort |
|---|---|---|---|---|
| 1 | NASA Earthdata Login | IGS TEC (GIM) ionosphere maps on CDDIS: the direct measure of what disturbs GNSS | Before the GNSS-impact analysis | 5 min, instant |
| 2 | Space-Track.org account | Historical Starlink orbital elements (orbit decay during storms), the impact data for satellite operators | Before the satellite-impact analysis | 10 min, approval can take a few days |
| 3 | Email to CCMC about DONKI | Their blessing to use DONKI for validating the platform's explanations | Before the evaluation chapter, ideally once the method is fixed | 10 min |

Not needed: GFZ, NOAA SWPC, NASA OMNI, DONKI API, Richardson–Cane, SSC, NCEI, Belsk, EPN RINEX files, CelesTrak (including SupGP Starlink ephemerides) all work without any login.

---

## 1. NASA Earthdata Login (for CDDIS)

- [ ] Register at https://urs.earthdata.nasa.gov/users/new (use your university email; choose "Education/Research" as the use).
- [ ] Confirm the email link.
- [ ] Log in once at https://cddis.nasa.gov/archive/ in a browser and accept the CDDIS application if asked.
- [ ] Put the credentials in a `.netrc` file so scripts can download without typing a password. On Windows the file is `C:\Users\areka\_netrc` (on Linux/WSL `~/.netrc`, permissions 600):
  ```
  machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD
  ```
  Never commit this file to git or paste it into the thesis repository.
- [ ] Test one file:
  ```
  curl -n -c cookies.txt -b cookies.txt -L -O https://cddis.nasa.gov/archive/gnss/products/ionex/2024/132/
  ```
  (lists day 132 = 11 May 2024; then download the final IGS map file shown there).

**What you get:** global ionosphere maps (TEC every 1–2 h, IONEX format) since 1998, folder `gnss/products/ionex/YYYY/DDD/`. Since late 2022 the files use long names (`IGS0OPSFIN_..._GIM.INX.gz`), before that short ones (`igsgDDD0.YYi.Z`). Python readers exist (e.g. a small IONEX parser, or `xarray` after conversion).

**Terms:** NASA open data, no redistribution restrictions. Cite the IGS products and CDDIS (Noll 2010, *Adv. Space Res.* 45, 1421–1440) and acknowledge "NASA CDDIS".

**To check when you get there (not verified today):** whether IGS ROTI maps (scintillation index, produced by UWM Olsztyn) are on CDDIS or only on the IGS/UWM site. CDDIS describes access only through Earthdata HTTPS; the old anonymous FTP is gone.

---

## 2. Space-Track.org

- [ ] Register at https://www.space-track.org/auth/createAccount. Give your real name, university and purpose, e.g. "Master's thesis at [university]: effect of geomagnetic storms on LEO orbit decay (Starlink)". Accounts are for approved users and are reviewed, so allow a few days.
- [ ] Read and accept the User Agreement (summary below).
- [ ] Test with one query after logging in (in the browser or with the `spacetrack` Python package):
  ```
  https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/44713/EPOCH/2024-05-05--2024-05-20/orderby/EPOCH/format/csv
  ```
  (44713 = STARLINK-1007; replace with the satellites you choose).

**What you get:** the full history of orbital elements (TLE/OMM) for every Starlink since 2019, which lets you measure how fast altitude dropped during storms such as Feb 2022 and May 2024. CelesTrak SupGP (no account) has more precise SpaceX ephemerides, but only recent ones, so Space-Track is the source for history.

**Terms that matter for the thesis** (User Agreement and API guidelines, read 11 Oct 2026):
- **Your own login only.** No sharing the password; one person, one account; no second account to get around limits.
- **Redistribution:** basic data (TLE/OMM, satellite catalogue, decay data) may be redistributed **with citation**; anything more needs an Orbital Data Request. So: do not publish the raw downloaded files in a public repo; publish your derived results (decay rates, plots) and cite "Space-Track.org, USSPACECOM".
- **API limits:** fewer than 30 requests per minute and 300 per hour. Download history in a few large queries (many satellites or a long date range per query) and cache locally. Excessive use gets the account suspended.
- **Renewal:** access must be renewed periodically; keep the email you registered with working.

---

## 3. Email to CCMC about DONKI

Why: the DONKI page says "CCMC requests that event and validation studies with data from DONKI be performed with the knowledge and collaboration" of the submitting forecasters/researchers. The thesis uses DONKI to check the platform's explanations, which is a validation use. It is a courtesy request, not a permission gate; data access stays open either way.

- [ ] Send when the evaluation method is settled (so you can describe it in one or two sentences).
- [ ] To: gsfc-ccmc-support@lists.hq.nasa.gov (general CCMC support). Optional CC: Dr. Leila Mays, m.leila.mays@nasa.gov (NASA official responsible for the CCMC site and DONKI).
- [ ] CC your supervisor if they want to be in the loop.
- [ ] Save their reply in `email_promotor/` or here; cite it in the thesis acknowledgements.
- [ ] Use the acknowledgement text from the CCMC publication policy (linked from the DONKI page) in the thesis.

**Draft (fill in the brackets):**

> **Subject:** Use of DONKI data for validation in a Master's thesis
>
> Dear CCMC team,
>
> I am a Master's student at [university, faculty], working under the supervision of Prof. [name] Surma. My thesis builds a prototype platform that explains geomagnetic storms and their likely effects for GNSS users and satellite operators, using GFZ Kp/Hp30, NOAA SWPC and NASA OMNI data.
>
> I would like to use DONKI as a reference for evaluation: for storms between 2010 and 2026, I plan to compare the causes the platform identifies (CME arrival, high-speed stream, interplanetary shock) with the corresponding DONKI entries (CME, IPS, HSS, GST and their linked events). The data would be retrieved through the public DONKI API, used only for non-commercial academic research, and treated as experimental research information, as stated on your website.
>
> Following your request that validation studies with DONKI data be carried out with the knowledge of CCMC, I wanted to let you know about this work and ask whether you have any guidance on using the catalogue this way, for example known limitations of entries before 2020 or a preferred acknowledgement. I would be glad to share the results once the thesis is finished.
>
> Kind regards,
> [Your full name]
> [university email]

---

## Optional, only if the scope grows

- **EUREF-IP NTRIP registration** (https://www.epncb.oma.be, real-time GNSS streams): only if the live platform should compute GNSS errors itself. Hourly RINEX files need no account.
- **RTGMS data request** to GUGiK / Instytut Łączności PIB (rtgms.pl): a short email asking for an archive of detected GNSS interference, if the hand-collected jamming counterexamples turn out too few.

Sources checked 11 Oct 2026: [Space-Track user agreement](https://www.space-track.org/documentation#/user_agree), [CDDIS archive access](https://www.earthdata.nasa.gov/centers/cddis-daac/archive-access), [DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/), [CCMC contact](https://ccmc.gsfc.nasa.gov/contact/). The IONEX folder layout, the Noll 2010 citation and the example NORAD ID are from my own knowledge; check them on first use.
