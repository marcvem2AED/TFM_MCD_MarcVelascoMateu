(iodd)=
# Algorithm Input and Output Data Definition (IODD)


## Input L1 Data

| Name                   | Description                                                                                      | Units       | Data Type | Shape              |
|------------------------|--------------------------------------------------------------------------------------------------|-------------|-----------|--------------------|
| L2PP Land TB K-band  | Level-2 Pre-Processed TBs at 18.7 GHz (H pol.)          | K           | float      | l1b  |
| L2PP Land Uncert. K-band | Total (and component) uncertainty of K-band L2PP Land TB (H pol.)                       | K           | float      | l1b  |
| L2PP Land Lat/Long K-band | Latitude and Longitude of the K-band L2PP Land TB                                             | degrees  | float    | l1b  |

## Input L2 Data

### Nominal Scenario [^footnoteL2input]

| Name    | Description                                  | Units              | Data Type | Shape              |
| ------- | --------------------------------------------| -------------------| ----------| -------------------|
| L2 SM LCX    | Soil Moisture (L/C/X-bands)                     | m³/m³ | float     | EASE v2 (3 km)  |
| L2 MMVI X-VOD   | X-band Vegetation Optical Depth            | -                  | float     | EASE v2 (3 km)  |

### Backup Scenario

| Name | Description                      | Units | Data Type | Shape              |
|------|----------------------------------|-------|-----------|--------------------|
| SM$^{ini}$ |  Initial value Soil Moisture (L/C/X-bands, rolling archive)  | m³/m³     | float      | EASE v2 (3 km) |
| X-VOD$^{ini}$  | Initial value of X-VOD (rolling archive) | -     | float      | EASE v2 (3 km) |

## Auxiliary Data

| Name | Description | Units | Type | Source | Data Type | Shape |
| ---  | ---         | ---   | ---       | ---  | ---  | ---   |
| $skt$ | Skin temperature |  K | Dynamic | ECMWF HRES IFS | float | EASE v2 (3 km) |
| $tp$ | Total Precipitation | mm/s | Dynamic | ECMWF HRES IFS | float | EASE v2 (3 km) |
| Water <br> Fraction | Fraction of permanent water bodies  |  - | Static | CIMR LOLM | float | EASE v2 (3 km) |
| Urban <br> Fraction | Fraction of urban area | - | Static | CIMR LCC | float | EASE v2 (3 km) |
| Frozen <br> Fraction | Fraction of permanently frozen area  | - | Static | CIMR LCC  | float | EASE v2 (3 km) |
| Distance to Coast (3 km)| Distance from the coastline                                        | km     | Static         | LOLM | float     | EASE v2 (3 km)            |
| LUT              | Lookup table of land reference emissivities for different SM and VOD | K    | Static         | [Static Offline Chain](./05_static_offline_preparation.md)| float     | (5, 11)       |

## Output Data

| Name                   | Description                                              | Units      | Data Type | Shape             |
|------------------------|----------------------------------------------------------|------------|-----------|-------------------|
| SWF                    | CIMR L2 Surface Water Fraction retrieval                 | fraction   | float     | EASE v2 (3 km)  |
| SWF Uncert.            | L2 Surface Water Fraction retrieval uncertainty          | fraction   | float     | EASE v2 (3 km)  |
| EASE Lat/Long          | EASE2 Latitude/Longitude                                 | degrees    | float     | EASE v2 (3 km)  |
| EASE row/column index  | Row/column index in EASE2 grid                           | -          | int       | EASE v2 (3 km)  |
| Land UTC time          | Sensing time                                             | ms         | long      | EASE v2 (3 km)  |
| status_flag            | Status flags of L2 SWF                                   | n/a        | 16-bit flag | EASE v2 (3 km) |


[^footnoteWaterMask]: The Water Fraction and Waterbody distance should be consistent with the corrections applied in the CIMR L1B/L2Bridge {doc}`[RD-2] <01_applicable_ref_docs>`.

[^footnoteL2input]:  An extra flagging for snow cover and frozen conditions is conducted in the Extra Consistency Step {doc}`[RD-4] <01_applicable_ref_docs>`.