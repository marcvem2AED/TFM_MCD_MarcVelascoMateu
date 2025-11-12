(offlinedynamic)=
# Dynamic Offline Preparation

## Algorithm NWP Inputs

The only dynamic field from ECMWF’s HRES High-Resolution Integrated Forecast System ({term}`IFS`) used as input to the algorithm is the skin temperature ($T_{\text{skin}}$), which is resampled to the 3 km grid. For flagging purposes, the dynamic field of total precipitation ($tp$) from ECMWF HRES IFS and the one-way atmospheric transmittance ($\Gamma$) provided by the L1B/L2 Bridge are also used.

## Research and Development

To reduce dependence on auxiliary data, the ECMWF $T_{\text{skin}}$ input may be replaced with CIMR L2 LST retrievals.