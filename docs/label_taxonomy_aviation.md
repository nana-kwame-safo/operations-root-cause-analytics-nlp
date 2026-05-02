# Aviation Label Taxonomy (Draft)

This document summarizes the current human-readable working taxonomy for `Anomaly_1` to `Anomaly_22` in the aviation demonstration domain.

## Validation Note

These names are interpretive working labels derived from model features and should be validated against source documentation or expert review before operational use.

All entries are currently marked:

- `taxonomy_status = "draft_from_model_features_pending_domain_review"`

## Evidence Basis

The draft taxonomy was refined from local model evidence using:

- top positive TF-IDF feature coefficients per label from the trained One-vs-Rest Logistic Regression estimators
- representative labeled examples inspected locally against label assignments

No raw narrative rows are reproduced in this document.

## Working Labels

| Label ID | Display Name | Short Name | Feature Evidence Snapshot |
|---|---|---|---|
| `Anomaly_1` | Draft MEL and Maintenance Deferral Indicator | MEL Deferral | `minimumequipmentlist`, `defer`, `writeup`, `logbook`, `mechanic` |
| `Anomaly_2` | Draft Clearance Compliance and Airspace Entry Indicator | Clearance Airspace | `fail to`, `inadvertent`, `classb`, `violate`, `clearance` |
| `Anomaly_3` | Draft Rejected Takeoff Indicator | Rejected Takeoff | `abort`, `reject`, `abortedtakeoff`, `takeoff`, `runway` |
| `Anomaly_4` | Draft Runway/Taxi Excursion and Braking Indicator | Excursion Braking | `grass`, `taxiway`, `brake`, `overrun`, `runway` |
| `Anomaly_5` | Draft Surface Movement Conflict Indicator | Surface Conflict | `taxiway`, `hold short`, `activerunway`, `groundcontrol`, `runway` |
| `Anomaly_6` | Draft Assigned Altitude/Clearance Deviation Indicator | Assigned Altitude | `assignedaltitude`, `clearance`, `autopilot`, `overshoot`, `deviate` |
| `Anomaly_7` | Draft Vertical Profile Deviation Indicator | Vertical Profile | `flightlevel`, `descend`, `climb`, `altitudedeviation`, `feet` |
| `Anomaly_8` | Draft Heading/Course Navigation Deviation Indicator | Heading Course | `turn`, `course`, `direct`, `degree`, `navigate` |
| `Anomaly_9` | Draft Airspeed Management Indicator | Airspeed Control | `airspeed`, `overspeed`, `autothrottle`, `knot`, `slow` |
| `Anomaly_10` | Draft Turbulence/Wind Aircraft Handling Indicator | Handling Upset | `turbulent`, `wind`, `encounter`, `damage`, `glideslope` |
| `Anomaly_11` | Draft Terrain Proximity Warning Indicator | Terrain Warning | `terrain`, `groundproximitywarningsystem`, `terrainwarning`, `lowaltitude`, `alert` |
| `Anomaly_12` | Draft Traffic Collision Avoidance Indicator | TCAS Traffic | `trafficalertandcollisionavoidancesystem`, `resolutionadvisory`, `trafficadvisory`, `separate`, `climb` |
| `Anomaly_13` | Draft Weather and Icing Encounter Indicator | Weather Encounter | `thunderstorm`, `instrumentmeteorologicalconditions`, `deice`, `weather`, `cloud` |
| `Anomaly_14` | Draft Controlled/Restricted Airspace Indicator | Airspace Restriction | `airspace`, `temporaryflightrestriction`, `classb`, `penetrate`, `violate` |
| `Anomaly_15` | Draft Unstable Approach Indicator | Unstable Approach | `glideslope`, `high`, `fast`, `stabilize`, `final` |
| `Anomaly_16` | Draft Go-Around/Missed Approach Execution Indicator | Go-Around | `goaraound`, `miss approach`, `execute`, `went around`, `final` |
| `Anomaly_17` | Draft Landing Configuration/Clearance Coordination Indicator | Landing Configuration | `gearup`, `land clearance`, `tower`, `gear`, `to land` |
| `Anomaly_18` | Draft Bird/Wildlife or Ground Object Strike Indicator | Strike Event | `bird`, `birdstrike`, `struck`, `ingest`, `wingtip` |
| `Anomaly_19` | Draft Engine/System Mechanical Condition Indicator | Engine Mechanical | `engine`, `inoperative`, `fail`, `maintain`, `manual` |
| `Anomaly_20` | Draft Smoke/Fume/Fire Indicator | Smoke Fume Fire | `smoke`, `odor`, `fume`, `fire`, `evacuate` |
| `Anomaly_21` | Draft Onboard Medical Event Indicator | Medical Event | `medicalemergency`, `doctor`, `paramedic`, `oxygen`, `passenger` |
| `Anomaly_22` | Draft Passenger Security and Cabin Disturbance Indicator | Cabin Security | `passenger`, `security`, `police`, `flightattendant`, `seat` |

## Limitations

- Labels remain interpretive and should not be treated as definitive root-cause determination.
- Coefficient-based cues highlight correlated terms, not causal proof.
- Domain review is required before high-stakes operational usage.
