# iCARE_cloud
to learn and to use iCare data: NWC SAF GEO cloud products.

this repo will be connected to CCuR later and working directly with the big volume of data.
## documentation:

this work has a doc word file prepared for publications in ./doc/publication:
- Microsoft word live editing link (login not required):
https://1drv.ms/w/s!AhhWTWH2RB5fjetdI4NDwqHBFknlIA

- Google Drive real time backup (without live editing):
https://docs.google.com/document/d/1YAUEVlxqM1g7M8y9fNNj1f-l_JvcCOyy/edit?usp=sharing&ouid=115400583048984110222&rtpof=true&sd=true
this Google backup is done by "Sync Folder Pro", to my local google Drive.
to edit locally, using file in this path.


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
- the box: Lon: -2,112; lat: 12,-52. (to be confirm)


## data

### 1. general info:
1. the downloaded geo info files (`MSG+0415.1km.hdf` ) from
(http://www.icare.univ-lille1.fr/archive?dir=GEO/STATIC/MSG+0000/), 
and and `MSG+0000.1km.hdf` from (http://www.icare.univ-lille1.fr/archive?dir=GEO/STATIC/MSG+0415/)
, are converted to netcdf by the code `h4tonccf_nc4` downloaded
from the site [hdfeos](http://hdfeos.org/software/h4cflib.php),
which is now in my Shell dir. this code works well for 1km resolution files (MSG+415.1km.hdf)

2. However, the coarse version namely `MSG+0415.3km.hdf` and 
`MSG+0000.3km.hdf` at 3km resolution seem not in good format, can not be read by 
`h4tonccf_nc4`. Differences are already seen in HDF viewer.

3. file name: 


    `MSG+0000` ->  `S_NWC_CMA_MSG1_globeI-VISIR_20170827T120000Z.nc`


    `MSG+0415` ->  `S_NWC_CMA_MSG3_globeM-VISIR_20170827T120000Z.nc`
   

    `icare.lonlat.nc` -> the output of this piece of code, controled by the 
    `parameter of "add_lon_lat" in the file of "cloud.yaml"`

    icare.lonlat.reg.nc -> if we select a small area from the bigdomain, we will get 
    a regular projection, this is the output of this piece of code to test a samll selection.

### 1. MSG+0415:

attention: we are using MSG+0415, the projection of field is centered at 41.5 deg East.

the info of coords are restored in an HDF or binary file.
This piece of code read it and add it to the raw non-coordinated nc files.



