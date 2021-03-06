#!/usr/bin/env python
# coding: utf-8

# In[20]:


import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from matplotlib.dates import DateFormatter
from matplotlib.offsetbox import AnchoredText


# In[22]:


## find the most recent GEFS run based on what's in the LDM
list_of_dirs = glob.glob('/ldm-data/model_grib/ens/*') # * means all if need specific format then *.csv
latest_dir = max(list_of_dirs, key=os.path.getctime)
yyyymmdd = latest_dir.split("/")[-1]

## now get the latest init time
list_of_files = glob.glob('/ldm-data/model_grib/ens/'+yyyymmdd+'/*') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
init = latest_file.split("/")[-1].split("_")[-1].split(".")[0]
#init="2020100712"
init_pd = pd.to_datetime(init,format="%Y%m%d%H", utc=True)

print("processing init: "+init)


## define GEFS members
mems = ["c00","p01","p02","p03","p04","p05","p06","p07","p08","p09","p10","p11","p12",
         "p13","p14","p15","p16","p17","p18","p19","p20","p21","p22","p23","p24","p25",
         "p26","p27","p28","p29","p30"]
#mems = ["p02","p03"]

for ee in range(0,len(mems)):
    print("working on member "+mems[ee])

    try: 
        os.remove('../gefs_rt/grib_idx/'+mems[ee]+'_temp.idx')
    except OSError:
        pass
    
    ## open the dataset; subset down to just the area over Colorado
    data = xr.open_dataset("/ldm-data/model_grib/ens/"+yyyymmdd+"/gefs_ge"+mems[ee]+"_"+init+".grib2", engine='cfgrib',
                       backend_kwargs={'indexpath': 'grib_idx/'+mems[ee]+'_temp.idx',
                                       'filter_by_keys': {'typeOfLevel': 'heightAboveGround','level':2 
                                       }}).sel(latitude=slice(42,36),longitude=slice(250,260))
    if ee==0:
        data_all = data
    else:
        data_all = xr.concat([data_all,data], dim='number')


# In[24]:


## set some stuff up for our stations we want to plot
lats = [40.580, 40.17,39.77, 37.15, 39.12, 38.07, 38.28, 40.30]
lons = [-105.103, -103.22,-104.67, -107.75, -108.53, -102.68,-104.52, -106.50]
stn_abbs = ['fcl', 'ako', 'den', 'dro', 'gjt','laa','pub', 'sbs']
stn_names = ['Fort Collins', 'Akron', 'Denver', 'Durango', 'Grand Junction', 'Lamar', 'Pueblo', 'Steamboat Springs']

for i in range(0,len(lats)):
    
    print('working on station '+stn_names[i])

    ## select data at our point, convert to inches
    point = data_all.sel(longitude=(lons[i]+360),latitude=lats[i], method='nearest')
    point.t2m.values = 1.8*(point.t2m.values-273.15)+32.

    ## also bring in the climo data for this point
    climo = pd.read_table(stn_abbs[i]+"_temp_climo.txt", sep=" ")
    climo['datetime'] = pd.to_datetime(climo.dates.values)
    climo = climo.set_index('datetime')

    ## calculate the cumulative precip over the period matching our forecast
    climo_this = climo.loc[str(point.valid_time[0].values):str(point.valid_time[-1].values)]

    fig, ax = plt.subplots(figsize=(14, 8))

    ## value at this point
    point.t2m.plot.line(hue='number', x='valid_time', ax=ax, lw=1.75, 
                                markersize=4,marker='o')
    ## ensemble mean
    point.t2m.mean(dim='number').plot.line(x='valid_time',ax=ax, color='black',lw=3.5, 
                                                   marker='o')

    ## climo
    climo_this.hightemp.plot.line(x='datetime',ax=ax,color='silver',lw=3)
    climo_this.lowtemp.plot.line(x='datetime',ax=ax,color='silver',lw=3)
    

    plt.suptitle("NCEP GEFS 2-m temperature at "+stn_names[i],fontweight='bold',y=0.935)
    plt.title("init: "+init_pd.strftime("%A %Y-%m-%d %H%M")+" UTC")

    legend = plt.legend(mems + ['mean','climo'], fontsize=7, title='member')
    plt.setp(legend.get_title(),fontsize=7.5)

    plt.xlabel("time (UTC)/date")
    plt.ylabel("temperature (Fahrenheit)")

    ax.xaxis.set_major_formatter(DateFormatter("%HZ/%d\n%a"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=0)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment('center')

## save it
    Path("/mnt/engrweb/weather/real_time/archive/sfc_gefs_temp_plume_"+stn_abbs[i]+"/"+init).mkdir(parents=True, exist_ok=True)
    plt.savefig("/mnt/engrweb/weather/real_time/archive/sfc_gefs_temp_plume_"+stn_abbs[i]+"/"+init+"/sfc_gefs_temp_plume_"+stn_abbs[i]+".png",
               bbox_inches='tight',dpi=110, facecolor='white',transparent=False)

    #plt.show()
    
    plt.close('all')



# In[ ]:




