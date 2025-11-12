(abstract)=
# Abstract

This ATBD presents the development of a Surface Water Fraction (SWF) retrieval algorithm. The algorithm is an evolution of previous work, adapted from techniques used with AMSR-E W-band and K-band, and SMAP L-band observations. 

The proposed approach employs K-band and follows a two-step process. Initially, a lookup table (LUT) of microwave emissivities at K-band (18.7 GHz) for pure land and water conditions is constructed from a global spectrum of vegetation and soil conditions. The SWF retrievals are then calculated on a pixel-by-pixel basis through a h-pol difference ratio (DR) method, comparing observed conditions against the reference emissivities for pure land and water scenarios.