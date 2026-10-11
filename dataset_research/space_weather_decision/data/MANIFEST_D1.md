# MANIFEST D1 - GFZ geomagnetic indices and NASA CCMC DONKI event catalogues

Retrieved 2026-10-10 through the user's built-in browser with same-origin `fetch()` (public, no login). Each CSV was built in the browser (UTF-8/ASCII, comma-separated, LF line endings, one header row, file ends with exactly one newline). It was then copied into the container in chunks that end at line boundaries. A file was saved only when the container SHA-256 matched the SHA-256 computed in the browser, and every file matched. No values were hand-edited. Retrieval times come from the browser clock and are in UTC.

| File | Rows | Cols | First | Last | SHA-256 |
|---|---|---|---|---|---|
| gfz_kp_ap_Ap_SN_F107_daily_2025-07-01_to_2026-10-09.csv | 466 | 22 | 2025-07-01 | 2026-10-09 | 2d1b0e72854b2e9932bdab507b3340a21c47ca364a028253283950210a5c583a |
| gfz_Hp30_selected_storms.csv | 1104 | 4 | 2003-10-28T00:00 | 2026-01-21T23:30 | a81b042cb1518b77e3ba2813eb6a5997a45d2312bb4c9c517378f8fa5ba0e098 |
| donki_gst_2010-01-01_to_2026-10-09.csv | 201 | 11 | 2010-04-05T12:00Z | 2026-10-04T18:00Z | 5e5896d0bd5b12df690855d83b6c954af977eb87a07248a56446f73a07848b1a |
| donki_cme_linked_to_gst.csv | 148 | 10 | 2010-08-01T08:20Z | 2026-08-04T13:23Z | 753efa940dfd8e5a9df2f11b68211297602b7aab9deb1e034d818ad55114ac30 |
| donki_ips_earth_2010-01-01_to_2026-10-09.csv | 683 | 5 | 2010-04-05T07:54Z | 2026-10-09T10:41Z | b63620c6f836f38781ba97a0de437119df2ce53b0c0af7af448e3f2cfbbfa36f |

(Row counts exclude the header row.)

---

## 1a. gfz_kp_ap_Ap_SN_F107_daily_2025-07-01_to_2026-10-09.csv

- **Source URLs** (host kp.gfz.de worked, so the fallback kp.gfz-potsdam.de was not needed):
  - https://kp.gfz.de/app/json/?start=2025-07-01T00:00:00Z&end=2026-10-10T00:00:00Z&index=Kp
  - https://kp.gfz.de/app/json/?start=2025-07-01T00:00:00Z&end=2026-10-10T00:00:00Z&index=ap
  - https://kp.gfz.de/app/json/?start=2025-07-01T00:00:00Z&end=2026-10-10T00:00:00Z&index=Ap
  - https://kp.gfz.de/app/json/?start=2025-07-01T00:00:00Z&end=2026-10-10T00:00:00Z&index=SN
  - https://kp.gfz.de/app/json/?start=2025-07-01T00:00:00Z&end=2026-10-10T00:00:00Z&index=Fobs
  - https://kp.gfz.de/app/json/?start=2025-07-01T00:00:00Z&end=2026-10-10T00:00:00Z&index=Fadj
- **Retrieved:** 2026-10-10T15:51:30Z
- **Columns:** date, kp_00UT, kp_03UT, kp_06UT, kp_09UT, kp_12UT, kp_15UT, kp_18UT, kp_21UT, ap_00UT, ap_03UT, ap_06UT, ap_09UT, ap_12UT, ap_15UT, ap_18UT, ap_21UT, Ap, SN, F107_obs, F107_adj, kp_status. All requested indices were available, including SN, Fobs and Fadj.
- **Values:** Values are as returned by the API. Kp is in thirds (for example 7.667) and printed in shortest form, so `2.0` is written as `2`. ap, Ap and SN are integers. F10.7 is in sfu. Each hour label is the start of a 3-hour interval, following the API's datetime convention.
- **Licence / citation:**
  - JSON `meta` field, verbatim: `{"license":"CC BY 4.0","source":"GFZ Potsdam"}`.
  - The GFZ format description (https://kp.gfz.de/app/format/Kp_ap_Ap_SN_F107_format.txt) says the files are CC BY 4.0 "except for the sunspot numbers ... which have the CC BY-NC 4.0 license". The SN data come from WDC-SILSO, Royal Observatory of Belgium.
  - Requested citation: Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. and Morschhauser, A. (2021), The geomagnetic Kp index and derived indices of geomagnetic activity, Space Weather, https://doi.org/10.1029/2020SW002641.
  - F10.7 is provided by DRAO / Natural Resources Canada.
- **Caveats:**
  - **kp_status:** The API status field takes the values `def` (definitive) and `pre` (preliminary), as documented in https://kp.gfz.de/app/format/json.txt. It never returns `now`. kp_status is therefore `def` when all 8 Kp values of the day are def; otherwise it holds the returned non-def status. That gives 457 days `def` (through 2026-09-30) and 9 days `pre` (2026-10-01 to 2026-10-09). ap carries the same status pattern as Kp.
  - **Ap:** Preliminary from 2026-10-01.
  - **SN:** Preliminary from 2026-04-01, which is 192 of 466 days. Any value may still be revised.
  - **Missing F10.7:** F107_obs and F107_adj are `-1` on 2026-05-09. This is GFZ's missing-data code and was kept as returned, so treat it as NaN.
  - **Partial last day excluded:** The query end is inclusive, so the API also returned a single 2026-10-10T00:00Z Kp/ap value. That partial day was left out, and the last full day is 2026-10-09. Daily indices end on 2026-10-09.
  - **Completeness:** There are no gaps, and every day has 8 Kp and 8 ap values.
  - **Overlap with the existing series:** This series overlaps the user's existing series (which ends 2025-07-20) from 2025-07-01 to 2025-07-20. Use the overlap to check consistency.

## 1b. gfz_Hp30_selected_storms.csv

- **Source URLs** (index=Hp30, half-hourly; each end is inclusive):
  - https://kp.gfz.de/app/json/?start=2003-10-28T00:00:00Z&end=2003-11-01T23:30:00Z&index=Hp30 (Halloween2003, 240 rows)
  - https://kp.gfz.de/app/json/?start=2015-03-16T00:00:00Z&end=2015-03-19T23:30:00Z&index=Hp30 (StPatricks2015, 192 rows)
  - https://kp.gfz.de/app/json/?start=2017-09-06T00:00:00Z&end=2017-09-09T23:30:00Z&index=Hp30 (Sep2017, 192 rows)
  - https://kp.gfz.de/app/json/?start=2024-10-09T00:00:00Z&end=2024-10-12T23:30:00Z&index=Hp30 (Oct2024, 192 rows)
  - https://kp.gfz.de/app/json/?start=2025-11-11T00:00:00Z&end=2025-11-13T23:30:00Z&index=Hp30 (KpSumTop2_2025-11-12, 144 rows)
  - https://kp.gfz.de/app/json/?start=2026-01-19T00:00:00Z&end=2026-01-21T23:30:00Z&index=Hp30 (KpSumTop1_2026-01-20, 144 rows)
- **Retrieved:** 2026-10-10T15:56:54Z
- **Columns:** datetime_utc (start of the 30-min interval, `YYYY-MM-DDTHH:MM`), Hp30, status, storm_window
- **Top Kp-sum days:** The two days with the highest daily Kp sum in file 1a are 2026-01-20 (sum 57.000, Ap 144) and 2025-11-12 (sum 51.334, Ap 137). The third-highest is 2025-09-30 (46.000). Each top day was taken with one day before and one after. The windows do not overlap, and rows are sorted by time.
- **Licence / citation:**
  - JSON `meta`, verbatim: `{"license":"CC BY 4.0","source":"GFZ Potsdam"}`.
  - The Hpo format file (https://kp.gfz.de/app/format/Hpo_Hp30.txt) asks for two citations:
    - Yamazaki et al. (2024), ESS Open Archive, https://doi.org/10.22541/essoar.171838396.68563140/v1
    - Matzka et al. (2024), Geomagnetic Hpo index V3.0, GFZ Data Services, https://doi.org/10.5880/Hpo.0003
- **Caveats:**
  - **status is empty in every row:** The GFZ JSON API gives no status for Hp30. The format note json.txt says status is "not available for Hp30 and Hp60", and adding `&status=def` returned identical data. In the Hpo text files the D flag is documented as always 0.
  - **Value range:** Hp30 is open-ended, unlike Kp, and reaches 12 during Halloween 2003. No missing values (-1) occur in these windows.

## 2. donki_gst_2010-01-01_to_2026-10-09.csv

- **Source:**
  - The specified legacy endpoint https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/GST... could not be used. Navigating to https://kauai.ccmc.gsfc.nasa.gov/DONKI/ redirected to the CCMC announcements page. That page says that from 2026-09-30 the API base https://ccmc.gsfc.nasa.gov/DONKI-API/get/... replaces the kauai WS endpoint and that parameters and formats are unchanged.
  - The new API also rejects any range over 60 days. A request for the full range returned "API Error: Date range cannot exceed 60 days". Year-by-year requests were therefore not possible.
- **URLs used:** `https://ccmc.gsfc.nasa.gov/DONKI-API/get/GST?startDate=S&endDate=E`, over 103 consecutive windows of 60 days. The windows run from S=2010-01-01 (2010-01-01..2010-03-02, 2010-03-02..2010-05-01, ...) to the last window, 2026-10-04..2026-10-09.
  - Adjacent windows share their boundary day because endDate is inclusive. Records were de-duplicated by gstID: 205 raw records gave 201 unique ones, and every duplicate was byte-identical.
  - A cross-check with monthly windows for 2015 and 2024 gave an identical ID set (47 storms).
- **Retrieved:** 2026-10-10T16:03:10Z to 16:04:11Z
- **Columns:** gst_id, start_time, kp_max, kp_max_time, kp_sources, n_kp_values, linked_cme, linked_ips, linked_hss, linked_flr, linked_other. The linked_* columns are `;`-separated activityIDs classified by `-CME-`, `-IPS-`, `-HSS-` or `-FLR-` in the ID; any other ID goes to linked_other.
- **Terms:** The DONKI Rules-of-the-Road (https://ccmc.gsfc.nasa.gov/tools/DONKI/) ask that event and validation studies be done with the knowledge and collaboration of the submitting forecasters, model developers and CCMC. They describe the data as "prototyping quality and in research context". The DONKI disclaimer says the data are provided "as is" without warranty. CCMC's publication policy gives sample acknowledgement statements. No explicit licence string is attached to the API data.
- **Caveats:**
  - **Field name:** The API field is `allKpIndex`, not "allKpValues".
  - **Kp values:** All Kp values come from NOAA. From 2023 onward NOAA gives fractional values such as 5.67, 6.33 and 8.67, while earlier values are integers. kp_max_time is the earliest observedTime of the maximum value.
  - **Coverage:** Records start on 2010-04-05; DONKI has no GST before that.
  - **Missing links:** 16 storms have no linked events (null).
  - **linked_flr:** Empty for every storm, because no flare is linked directly to a GST.
  - **linked_other:** Contains magnetopause-crossing (`-MPC-`) IDs.
  - **gstID "none":** One record has the literal gstID `none` (start 2016-02-17T21:00Z, Kp 6 at 2016-02-19T00:00Z, https://ccmc.gsfc.nasa.gov/DONKI/view/GST/10233/-1). It was kept as returned and may duplicate the 2016-02-17T21:00:00-GST-001 storm.
  - **Revisions:** DONKI records can be revised (versionId), so a later retrieval may differ.

## 3. donki_cme_linked_to_gst.csv

- **URLs used:** `https://ccmc.gsfc.nasa.gov/DONKI-API/get/CME?startDate=S&endDate=E`, with the same 103 windows of 60 days covering 2010-01-01 to 2026-10-09 and default parameters (all analyses returned).
  - This returned 10,433 raw records, or 10,266 unique CME IDs. The largest window held 369 records, so there is no sign of truncation.
  - Only CMEs whose activityID appears in linked_cme of file 2 were kept.
- **Retrieved:** 2026-10-10T16:05:36Z to 16:07:07Z
- **Linked CMEs:** All 148 linked CME IDs were found, so **0 linked CME IDs were not found**.
- **Columns:** activity_id, start_time, source_location, active_region_num, speed_kms, half_angle_deg, type, n_analyses, linked_events (`;`-separated, as returned), n_most_accurate
- **n_most_accurate column:** This is an extra column, not part of the requested schema. It gives the number of analyses flagged isMostAccurate=true.
- **Terms:** As for file 2 (DONKI Rules-of-the-Road and disclaimer).
- **Caveats:**
  - **Analysis selection:** speed, half-angle and type come from the first cmeAnalyses entry with isMostAccurate=true, in the API's array order; if no entry is flagged, the first analysis is used.
  - **Several analyses flagged:** 37 of the 148 CMEs have two or more analyses flagged isMostAccurate=true (n_most_accurate > 1), and the flagged entries can differ substantially. For example, 2015-03-15T02:00:00-CME-001 has both 750 km/s type C and 1000 km/s type O. Review these rows if speed matters.
  - **Empty fields:** source_location is empty for 40 CMEs and active_region_num for 64.
  - **Type codes:** S, C, O and R are DONKI's speed classes.
  - **Odd link:** One CME (2017-07-14T01:36:00-CME-001) lists a linked event literally named `none`; it was kept as returned.

## 4. donki_ips_earth_2010-01-01_to_2026-10-09.csv

- **URLs used:** `https://ccmc.gsfc.nasa.gov/DONKI-API/get/IPS?startDate=S&endDate=E&location=Earth`, with the same 103 windows of 60 days.
  - The location filter is supported. On two test windows (2015-03-01..2015-04-30 and 2024-04-01..2024-05-31) it returned exactly the `location=="Earth"` subset of the unfiltered query.
  - This gave 693 raw records and 683 unique activityIDs.
- **Retrieved:** The CSV was built from the 2026-10-10T16:11:56Z to 16:12:51Z run. An earlier run, 16:09:00Z to 16:10:14Z, returned the identical ID set.
- **Columns:** activity_id, event_time, location, catalog, linked_events (`;`-separated, as returned)
- **Terms:** As for file 2.
- **Caveats:**
  - **Catalogue:** All rows are from the M2M_CATALOG.
  - **Missing links:** 102 shocks have no linked events.
  - **Duplicates:** Three boundary-day duplicates differed only in the order of the instruments list, which is not exported; the first occurrence was kept.
  - **Cross-check with file 2:** All 119 IPS IDs linked from GSTs in file 2 are present.
  - **Uneven coverage:** Shocks per year vary a lot (for example 4 in 2018 and 83 in 2024), which reflects DONKI curation effort as well as solar activity. Do not treat the counts as a homogeneous climatology.

## Not done / skipped

- **Legacy kauai DONKI endpoint:** Not usable (redirects since the migration on 2026-09-30). The new official API was used instead.
- **Browser access:** No logins, form submissions, downloads or consent dialogs were needed or used.
