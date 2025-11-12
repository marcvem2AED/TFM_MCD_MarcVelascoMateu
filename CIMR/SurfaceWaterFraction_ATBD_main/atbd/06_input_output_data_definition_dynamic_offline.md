(iodddyn)=
# Input and Output Data Definition for Dynamic Offline Preparation

## Input data (NWP)

| Name | Description | Units | Static/Dynamic | Source | Data Type | Shape |
| ---  | ---         | ---   | ---       | ---  | ---  | ---   |
| $skt$ | Skin temperature |  K | Dynamic | ECMWF HRES IFS | float | (3600, 1800) |
| $tp$ | Total Precipitation | mm/s | Dynamic | ECMWF HRES IFS | float | (3600, 1800) |

## Output data (NWP)

| Name | Description | Units | Static/Dynamic | Source | Data Type | Shape |
| ---  | ---         | ---   | ---       | ---  | ---  | ---   |
| $skt$ | Skin temperature |  K | Dynamic | ECMWF HRES IFS | float | EASE v2 (3 km) |
| $tp$ | Total Precipitation | mm/s | Dynamic | ECMWF HRES IFS | float | EASE v2 (3 km) |