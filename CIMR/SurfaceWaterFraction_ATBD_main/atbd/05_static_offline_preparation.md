(offlinestatic)=
# Static Offline Preparation

## Algorithm Input Parameters

(sec:static_offline)=
#### Reference emissivity for freshwater (water endmember)

To obtain a reliable reference value for the open-water emissivity $(\epsilon_{hw}^{\text{ref}})$, observations were restricted to pixels fully located within large, non-frozen freshwater lakes. Water salinity was not considered due to its negligible impact on the K-band signal. These pixels were carefully selected to avoid contamination from mixed land–water coastlines. Only pixels classified as 100% water according to the Global Lakes and Wetlands Database (GLWD) v2 total area fraction were retained. The GLWD version 2 {cite:p}`Lehner2025` provides a 15-arcsecond (~500 m) global map of 33 inland waterbody and wetland types, representing 18.2 million km² of aquatic ecosystems worldwide. 

Emissivities were computed using ERA5 skin temperature over lakes. A two-component Gaussian Mixture Model was fitted to the emissivity histogram, retaining the Gaussian corresponding to the main component to derive a reference value. An atmospheric correction following {cite:p}`Delannoy2015` was applied. 

```{math}
:label: emissivity_eq
\epsilon = \frac{TB^{BOA}_H}{T_{\text{skin}}}
```

Where:
- $TB^{BOA}_H$ is the bottom-of-atmosphere (BOA) K-band brightness temperature, observed by WindSat at horizontal polarization (H pol.), and corrected for atmospheric effects. 
- $T_{\text{skin}}$ is the surface skin temperature obtained from ECMWF.

The resulting mean emissivity for open freshwater bodies was estimated to be:

```{math}
\epsilon_{Hw}^{\text{ref}} = 0.354
```

This value was treated as constant for the water endmember, given the low variability of freshwater emissivity. It is consistent with literature estimates {cite:p}`Jones2010`.

#### Reference land emissivities (land endmember)

To construct the LUT for land emissivity, global estimates were derived using one year of WindSat $TB^{BOA}_H$ data {cite:p}`Meissner2023` combined with the K-band Surface Water Fraction (SWF) product from the LPDR dataset {cite:p}`Du2017`. The SWF product served as a screening criterion to ensure that only pure land surfaces were used in the analysis. Pure land endmembers were identified as grid cells where the SWF value was below 0.02, indicating negligible surface water influence. For these pixels, the surface emissivity at horizontal polarization was computed using the same equation described previously {eq}`emissivity_eq`.

Unlike the water case where a fixed emissivity value was sufficient, land emissivity exhibits some variability depending on surface conditions. To account for this, a Look-Up Table (LUT) of reference land emissivities was constructed across discrete intervals of Soil Moisture (SM) and Vegetation Optical Depth (VOD) following a similar approach as {cite:p}`Du2018`. We selected the year 2017 and globally identified all pure land pixels, which were binned according to their SM and VOD values. The corresponding emissivity values within each bin were then averaged. These mean values were then used to fill the LUT with representative reference emissivities for each SM–VOD combination ({numref}`rangesVODSM_H`).

```{table} Representative reference emissivities for SM–VOD bins
:name: rangesVODSM_H
| SM Bins \ VOD Bins | 0.00-0.05 | 0.05-0.10 | 0.10-0.15 | 0.15-0.20 | 0.20-0.25 | 0.25-0.30 | 0.30-0.40 | 0.40-0.50 | 0.50-0.60 | 0.60-0.70 | 0.70-1.00 |
|--------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| 0.00-0.10          | 0.78       | 0.82       | 0.85       | 0.87       | 0.89       | 0.91       | 0.92       | 0.93       | 0.94       | 0.93       | 0.94       |
| 0.10-0.20          | 0.90       | 0.85       | 0.85       | 0.87       | 0.89       | 0.90       | 0.92       | 0.93       | 0.94       | 0.94       | 0.94       |
| 0.20-0.30          | 0.78       | 0.85       | 0.86       | 0.86       | 0.88       | 0.89       | 0.90       | 0.92       | 0.93       | 0.94       | 0.95       |
| 0.30-0.40          |            |            | 0.80       | 0.87       | 0.87       | 0.86       | 0.89       | 0.91       | 0.93       | 0.94       | 0.94       |
| 0.40-0.50          | 0.76       |            | 0.84       |            | 0.83       | 0.87       | 0.78       | 0.91       | 0.94       |            | 0.94       |
```

It should be noted that this LUT will require reprocessing once CIMR in-flight data becomes available.

## Static Flags 

Several static layers are used to flag CIMR SWF retrievals.

Static maps of the distance to coastline are derived from the CIMR {term}`LOLM`. Additionally, static maps of permanently snow-covered or frozen areas, permanent wetlands, and distance to coastline are obtained from the CIMR {term}`LCC`.

