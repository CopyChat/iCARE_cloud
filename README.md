# iCARE_cloud
to learn and to use iCare data

## information:
### 1. link of data: 
- ftp://ftp.icare.univ-lille1.fr/SPACEBORNE/GEO/MSG+0000/S_NWC/ 
- http://www.icare.univ-lille1.fr/archive?dir=GEO/MSG+0000/S_NWC/ `Il faut se créer un compte: les produits SAF NWC 
ne sont pas accessibles "librement" (cf. PJ).`
### 2. link of geo info:
Tu trouveras les fichiers lat et lon pour MSG à l’URL:
http://www.icare.univ-lille1.fr/archive?dir=GEO/STATIC/MSG+0000/
utilisable avec les produits S_NWC 
(et non pas seulement avec le L1B comme indiqué pour le moment dans le README).

### 3. data area:
- the box: Lon: -2,112; lat: 12,-52.


## data

### 1. general info:
1. the downloaded geo info files (`MSG+0415.1km.hdf` ) from
(http://www.icare.univ-lille1.fr/archive?dir=GEO/STATIC/MSG+0000/), 
and and `MSG+0000.1km.hdf` from (http://www.icare.univ-lille1.fr/archive?dir=GEO/STATIC/MSG+0415/)
, are converted to netcdf by the code `h4tonccf_nc4` downloaded
from the site [hdfeos](http://hdfeos.org/software/h4cflib.php),
which is now in my Shell dir.

2. However, the coarse version namely `MSG+0415.3km.hdf` and 
`MSG+0000.3km.hdf` seem not in good format, can not be read by 
`h4tonccf_nc4`. Differences are already seen in HDF viewer.

3. file name: 

    `MSG+0000` ->  `S_NWC_CMA_MSG1_globeI-VISIR_20170827T120000Z.nc`

    `MSG+0415` ->  `S_NWC_CMA_MSG3_globeM-VISIR_20170827T120000Z.nc`

### 1. MSG+0000

