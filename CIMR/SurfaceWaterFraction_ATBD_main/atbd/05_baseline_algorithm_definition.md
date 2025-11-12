(baseline)=
# Baseline Algorithm Definition

This section describes the baseline SWF retrieval algorithm. The algorithm is based on the methodology proposed by {cite:p}`Du2016,Du2017,Du2018`, adapted to the available microwave channels and specific overpass time of CIMR.

## Retrieval Method

The Tau-Omega model equation {eq}`emissivity_1` describes the surface emissivity of terrestrial surfaces $e_p$ as observed by satellites under conditions where the land is not frozen and free of snow {cite:p}`Jones2010`.


```{math}
:label: emissivity_1
\epsilon_p = f_w \cdot \epsilon_{pw} + (1-f_w) \cdot \epsilon_{pl}
```

```{math}
:label: emissivity_2
\begin{aligned}
\epsilon_{pl} &= (1-\omega)(1-\gamma)\left[1 + R_p \gamma \right] + (1-R_p)\gamma \\
\gamma &= \exp[-\tau \sec(\theta)]
\end{aligned}
```

```{math}
:label: emissivity_3
\epsilon_{pw} = f(\epsilon_w, S_r)
```
where the subscript $p \in H,V$ indicates polarization, and $ \epsilon_{w}$ and $ \epsilon_{l}$ represent the emissivities of water and land, respectively. The surface water term $f_w$ refers to the fractional water within the sensor field of view (i.e., Surface Water Fraction, SWF). The symbol $ \gamma$ denotes the microwave transmissivity through the vegetation layer and $\theta$ is the incidence angle, $\tau$ refers to the vegetation optical depth (VOD) and $\omega$ to the vegetation scattering albedo. $ R_{p}$ represents the soil reflectivity of a rough surface. $ \epsilon_{w}$ is the permittivity of water, and $ S_{r}$ is the surface water roughness. It must be noted that dependencies on the incidence angle $\theta$ are omitted for clarity in all emissivity and reflectivity terms. For the same reason, dependencies of vegetation parameters on polarization have been omitted.

Although the Tau-Omega model provides a theoretical framework to describe the relationship between surface emissivity and water fraction, applying it directly for SWF retrieval requires knowledge of multiple surface parameters, including VOD, vegetation scattering albedo, soil roughness and dielectric properties.

Due to the complexity and limited availability of these input parameters at global scale and high resolution, a simplified retrieval method is proposed. This method is based on the use of a Difference Ratio (DR), which approximates SWF from observed surface emissivity and pre-computed reference emissivities for water and land, as showed in the mathematical description presented below.

### Reference Emissivity Estimation for Land and Water Endmembers

A Look-Up Table (LUT) containing reference K-band microwave emissivities was developed to characterize pure endmember conditions for land and water (see [static offline preparation](./05_static_offline_preparation.md)).



## CIMR Level-1b pre-processing and re-sampling approach

The CIMR SWF processor ingests L2PP Land files produced by the CIMR L1B/L2Bridge {doc}`[RD-2]<01_applicable_ref_docs>`. L2PP Land files contain K-band brightness temperature (TB) observations (V and H polarizations) in swath geometry. In the L2 SWF Processor, annotations on L2PP Land files are applied to correct for water spillover efects in coastal areas (not near inland water bodies), and to compensate OZA variations across feeds and along the scan. The L2PP top-of-atmosphere (TOA) brightness temperatures are then corrected for atmospheric effects to obtain bottom-of-atmosphere (BOA) brightness temperatures, using the pre-computed atmospheric parameters provided by the L1B/L2Bridge. The corrected BOA brightness temperatures are then mapped onto a 3 km global EASE grid with the RGB resampling toolbox {doc}`[RD-3] <01_applicable_ref_docs>`.

## Algorithm Assumptions and Simplifications

By calculating land reference emissivities from a reference dataset (LPDR), the algorithm assumes unbiased SWF, SM and VOD estimations to construct the look-up table. Additionally, for the reference emissivities, the changes over soil and water surface roughness are not accounted. Soil and vegetation temperatures are accounted through the skin temperature ($T_{skin}$ ).

## Level-2 end to end algorithm functional flow diagram

{numref}`swf_diagram` shows the algorithm flow for the L2 SWF retrieval algorithm. For clarity, this algorithm is expected to run separately on ascending and descending overpasses.

```{figure} /static_imgs/swf_diagram.jpg
--- 
name: swf_diagram
---
CIMR L2 Surface Water Fraction estimation flow diagram
```
## Atmospheric correction

As a first step, the L2PP brightness temperatures are converted from top-of-atmosphere (TOA) to bottom-of-atmosphere (BOA) values, using atmospheric parameters provided by the L1B/L2 Bridge. Neglecting sky contributions, the TOA brightness temperature can be expressed as {cite:p}`Delannoy2015, Prigent2006`:
As a first step, the L2PP brightness temperatures are converted from top-of-atmosphere (TOA) to bottom-of-atmosphere (BOA) values, using atmospheric parameters provided by the L1B/L2 Bridge. Neglecting sky contributions, the TOA brightness temperature can be expressed as {cite:p}`Delannoy2015, Prigent2006`:


```{math}
:label: atm_1
TB^{TOA}_p = TB^{up}_{atm} + \Gamma \cdot TB^{BOA}_p + \Gamma (1-e_p^{surf}) TB^{dw}_{atm},
```
where $p \in H, V$ indicates polarization, $TB^{up}_{atm}$ is the unpolarized upwelling brightness temperature, $TB^{dw}_{atm}$ is the unpolarized downwelling brightness temperature, $\Gamma$ is the one-way atmospheric transmittance, $e_p^{surf}$ is the emissivity of the land surface (including contributions from the soil and vegetation). The BOA brightness temperature and surface emissivity are related as $TB^{BOA}_p = e_p^{surf} T_{eff}$, where $T_{eff}$ is the effective temperature, assumed equal to $T_{skin}$. Assuming that the downwelling atmosphere brightness temperature is reflected in a purely specular manner, Equation {eq}`atm_1` can be rearranged to yield {cite:p}`Delannoy2015`

```{math}
:label: atm_2
TB^{BOA}_p = T_{eff} \frac{TB^{TOA}_p \cdot \Gamma^{-1} - (1 + \Gamma^{-1})TB^{up}_{atm}}{T_{eff} - TB^{dw}_{atm}}.
```

The uncertainty of the atmospheric terms shall be propagated into the $TB^{BOA}_p$ uncertainty.

#### Input data

- L2PP Land TBs (TOA) at K-band (H polarization).  
- L2PP Land TBs (TOA) at K-band (H polarization) uncertainty.
- L2PP Land atmospheric terms at K-band: $TB^{up}_{atm}$, $TB^{dw}_{atm}$, $\Gamma$.  

#### Output data

- L2PP Land TBs (BOA) at K-band (H apolarization).  
- L2PP Land TBs (BOA) at K-band (H apolarization) uncertainty.  

## Resampling

After the atmospheric correction, the BOA L-band brightness temperature (TBs) is resampled to the 3 km EASE2 grid. The resampling process uses the {term}`RGB toolbox`, as described in {doc}`[RD-3] <01_applicable_ref_docs>`. The toolbox is expected to propagate TB uncertainties.

#### Input data

- L2PP Land TBs (BOA) at K-band (H polarization).  
- L2PP Land TBs (BOA) at K-band (H polarization) uncertainty.

#### Output data

- L2PP Land TBs (BOA, gridded at 3 km) at K-band (H polarization).  
- L2PP Land TBs (BOA, gridded at 3 km) at K-band (H polarization) uncertainty. 

## SWF retrieval approach

The SWF (Surface Water Fraction) retrieval approach follows the next steps:

1. **Observed emissivity calculation**: Emissivity is calculated as the K-band TB data from CIMR divided by $T_{skin}$ temperature from ECMWF.

2. **SWF Calculation through DR**: The final SWF is derived using the DR method. This method compares the observed emissivity with the reference land emissivity, relative to the emissivity difference between pure water and land. The model is applied exclusively to non-frozen pixels (to be defined in future versions).

### Mathematical description

```{math}
:label: swf_eq
f_w = \frac{\epsilon_H^{obs} - \epsilon_{Hl}^{ref}}{\epsilon_{Hw}^{ref} - \epsilon_{Hl}^{ref}}
```

where $ \epsilon_{H}^{obs}$ represents the actual satellite emissivity observation for $ H$ polarization, $ \epsilon_{Hw}^{ref}$ denotes the emissivity from the reference water endmember pixel and $ \epsilon_{Hl}^{ref}$ is the emissivity from the reference land endmember pixel.

A 16-bit status flag is provided alongside the retrieval. Bit-by-bit, the flag indicates:
(0) Fraction of permanent waterbodies exceeding 50% (if the waterbody fraction is 100%, no retrieval is attempted),
(1) Distance from the coastline lower than or equal to 6 km,
(2) Fraction of urban areas exceeding 25%,
(3) Fraction of permanently frozen areas exceeding 5%,
(4) Precipitation rate exceeding 1 mm/hr,
(5) Unphysical retrievals,
(6) Presence of RFI.

Additional flagging for snow cover and frozen conditions is conducted during the Extra Consistency Step {doc}`[RD-4] <01_applicable_ref_docs>`.

### Input data

* Level-2 Pre-Processed TB (non water-corrected) at 18.7 GHz (H polarization).
* CIMR L2 Soil Moisture (L/C/X-band, gridded at 3 km). 
* CIMR L2 Soil Moisture (L/C/X-band, gridded at 3 km) uncertainty.
* CIMR L2 X-band Vegetation Optical Depth (gridded at 3 km).
* CIMR L2 X-band Vegetation Optical Depth uncertainty (gridded at 3 km).

Note that the CIMR L2 Soil Moisture and Vegetation Optical Depth variables at 3 km resolution are derived from the 9 km nested EASE2 grid used in the L2 SM and MMVI products.

### Output data

* CIMR L2 Surface Water Fraction.
* CIMR L2 Surface Water Fraction uncertainty.
* CIMR L2 Surface Water Fraction status flag.
* Latitude, longitude, EASE 2 grid row and column, UTC time.

### Auxiliary data

* LUT with land emissivities for different SM and VOD ranges of values.
* Water emissivity at K-band (H pol.).
* Skin temperature, total precipitation, permanent water areas, urban, permanent frozen and distance to coast.

A full list of input, output, and auxiliary data is provided in the [IODD](06_input_output_data_definition.md).

### Uncertainty quantification

The current approach presents an error propagation scheme, based on input uncertainties and partial derivatives.

We assume the following sources of uncertainty:

- $TB_{H}$ (brightness temperature): $\sigma_{TB}$,
- $T_{skin}$ (skin temperature from ECMWF): $\sigma_{T_{skin}}$,
- $\epsilon_{Hl}^{ref}$ (reference land emissivity) from LUT standard deviations: $\sigma_{Hl}$,
- $\epsilon_{Hw}^{ref}$ (reference freshwater emissivity): $\sigma_{Hw}$

The total uncertainty of the SWF is expressed by its variance:

```{math}
:label: sigma_swf
\sigma^2_{f_w} =
\left( \frac{\partial f_w}{\partial \epsilon_H^{obs}} \right)^2 \sigma^2_{\epsilon} +
\left( \frac{\partial f_w}{\partial \epsilon_{Hl}^{ref}} \right)^2 \sigma^2_{Hl} +
\left( \frac{\partial f_w}{\partial \epsilon_{Hw}^{ref}} \right)^2 \sigma^2_{Hw}
```

where $\sigma_{\epsilon}$ is the standard deviation of the observed emissivity, which depends on $\sigma_{TB}$ and $\sigma_{T_{skin}}$. The standard deviation $\sigma_{TB}$ arises from the random noise and calibration uncertainty of the L1B TB. $\sigma_{Hw}$ is static, and $\sigma_{Hl}$ is obtained from a LUT that depends on SM and VOD. The calculation of $\sigma_{\epsilon}$ is detailed below.

#### Partial Derivatives of SWF: Step-by-Step Derivation

We start from the expression:

```{math}
:label: swf_delta
f_w = \frac{\epsilon_H^{obs} - \epsilon_{Hl}^{ref}}{\epsilon_{Hw}^{ref} - \epsilon_{Hl}^{ref}} = \frac{\epsilon_H^{obs} - \epsilon_{Hl}^{ref}}{\Delta}
```

Derivative with respect to $\epsilon_H^{obs}$ :

$\Delta$ is constant with respect to $\epsilon_H^{obs}$:

```{math}
:label: partial1
\frac{\partial f_w}{\partial \epsilon_H^{obs}} = \frac{1}{\Delta}
```

Derivative with respect to $\epsilon_{Hl}^{ref}$ :

```{math}
:label: partial2
\frac{\partial f_w}{\partial \epsilon_{Hl}^{ref}} =
\frac{-\Delta + (\epsilon_H^{obs} - \epsilon_{Hl}^{ref})}{\Delta^2} =
\frac{\epsilon_H^{obs} - \epsilon_{Hw}^{ref}}{\Delta^2}
```

Derivative with respect to $\epsilon_{hw}^{ref}$ :

```{math}
:label: partial3
\frac{\partial f_w}{\partial \epsilon_{Hw}^{ref}} =
\frac{-(\epsilon_H^{obs} - \epsilon_{Hl}^{ref})}{\Delta^2} =
\frac{\epsilon_{Hl}^{ref} - \epsilon_{H}^{obs}}{\Delta^2}
```

The total uncertainty of the SWF estimate is then calculated applying error propagation:

```{math}
:label: sigma_swf2
\sigma_{f_w}^2 =
\left( \frac{1}{\Delta} \right)^2 \sigma_{\epsilon}^2 +
\left( \frac{\epsilon_{H}^{obs} - \epsilon_{Hw}^{ref}}{\Delta^2} \right)^2 \sigma_{Hl}^2 +
\left( \frac{\epsilon_{Hl}^{ref} - \epsilon_{H}^{obs}}{\Delta^2} \right)^2 \sigma_{Hw}^2
```

Note that the observed emissivity $\epsilon$ is computed from the ratio:

```{math}
:label: emissivity_u
\epsilon = \frac{TB_{H}}{T_{skin}}
```

To estimate its uncertainty, we apply error propagation:

```{math}
:label: emissivity_uncert_derivation
\sigma_{\epsilon}^2 =
\left( \frac{\partial \epsilon}{\partial TB_{H}} \right)^2 \sigma_{TB}^2 +
\left( \frac{\partial \epsilon}{\partial T_{skin}} \right)^2 \sigma_{T_{skin}}^2
```

The computation of the partial derivatives is:

- $\frac{\partial \epsilon}{\partial TB_{H}} = \frac{1}{T_{skin}}$
- $\frac{\partial \epsilon}{\partial T_{skin}} = -\frac{TB_{H}}{T_{skin}^2}$

Substituting into the formula:

```{math}
:label: emissivity_uncert
\sigma_{\epsilon}^2 =
\left( \frac{1}{T_{skin}} \right)^2 \sigma_{TB}^2 +
\left( \frac{TB_{H}}{T_{skin}^2} \right)^2 \sigma_{T_{skin}}^2
```

```{note}
Uncertainty values are computed per pixel and propagated into the final `SWF_uncertainty` output product, alongside a `status_flag` to indicate suspect input values (e.g. low confidence $T_{skin}$).
```

### Output Variables

* `surface_water_fraction`: Main SWF retrieval value.
* `swf_uncertainty`: Estimated variance of SWF from analytical error propagation.
* `status_flag`: Coded flag for quality control and traceability of uncertainty contributions.

### Prototype implementation

The figures below show the surface water fraction retrieved over CONUS, along with the input data used (Windsat TB and LPDR SM and VOD) from July 15, 2017. As expected, SWF values predominantly range between approximately 0 and 0.3 {cite:p}`Du2017`.

```{figure} ./static_imgs/swf_retrieval.png
---
name: swf_retrieval
---
Illustration of the retrieval of SWF over partially inundated areas where SM and VOD data is available over CONUS on July 15, 2017.
```

### Research and development

Research and development efforts aim to enhance the SWF retrieval by integrating machine learning methods applied to K- and Ka-band data, complementing the existing Difference Ratio (DR) method. In parallel, ongoing work focuses on refining the uncertainty characterization.