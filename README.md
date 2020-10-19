# gefs_plumes
plume diagrams from NCEP GEFS grib files

Example python code to generate plume diagrams (http://schumacher.atmos.colostate.edu/weather/ens.php#plumes) from NCEP GEFS grib files. Our structure is to have one file per ensemble member (e.g., all 384 hours of member c00 are in one file, all 384 hours of member p01 in another file, etc.), so that's what the code expects.

This will also add climatological temperature/precip traces, if you have that information in text files. That part of the could could also just be commented out if you don't have or want the climo information.
