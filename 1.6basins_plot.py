#import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx

#read MA stations that has precipitation data starting from 2010 upto 2020
station_MA = pd.read_csv('data/MA_stations_2000-2020.csv')
#read filtered basins
df_basins = pd.read_csv('data/MA_basins_gauges_2000-2020_filtered.csv',dtype={'basin_id':str})

#read basin drainage area
drainage_area = pd.read_csv('data/station_with_elev_and_area.csv',dtype={'STAID':str})
#empty dataframe to store the number of stations in each basin
df_num_stations = pd.DataFrame()

#plot single basins
#read a basin shapefile
used_basin_list = ['01108000', '01109060', '01177000', '01104500']

for basin_id in used_basin_list:
    basin_drainage_area = drainage_area[drainage_area['STAID']==basin_id]
    basin_drainage_area = basin_drainage_area['DRAIN_SQKM'].values[0]

    basin_shapefile = gpd.read_file(f'data/prms_drainage_area_shapes/model_{basin_id}_nhru.shp')
    #create another shapefile name basin_shapefile_buffer with 10km buffer
    basin_shapefile_buffer = basin_shapefile.copy()
    basin_shapefile_buffer['geometry'] = basin_shapefile_buffer.buffer(10000) #buffer 10km

    #convert the basin shapefile to the same coordinate system as the stations
    basin_shapefile = basin_shapefile.to_crs(epsg=4326)
    basin_shapefile_buffer = basin_shapefile_buffer.to_crs(epsg=4326)
    #filter stations that lies within the basin_shapefile
    #convert the stations to geodataframe
    stn_MA = gpd.GeoDataFrame(station_MA,geometry=gpd.points_from_xy(station_MA['lon'],station_MA['lat']))
    #make a list of stations that overlap with the basin
    stn_MA = stn_MA[stn_MA.within(basin_shapefile_buffer.unary_union)]
    stn_MA = stn_MA.reset_index(drop=True)

    ###plot the stations and the basin
    fig, ax = plt.subplots(figsize=(6,6))
    basin_shapefile.plot(ax=ax, edgecolor='none', facecolor = 'purple', alpha =0.3)
    stn_MA.plot(ax=ax,color='brown', markersize=50, marker='d', linewidth=3,
                 label=f'Gauging Station (n={len(stn_MA)})\nDrainage Area: {basin_drainage_area} SQKM')

    ctx.add_basemap(ax, crs=basin_shapefile.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend(loc = 'best')
    plt.title(f'Basin ID:{basin_id}')
    plt.tight_layout()
    plt.show()
    #save figure
    fig.savefig(f'output/figures/{basin_id}/0basin_{basin_id}.png', dpi=300)


#save shapefile for each basin with gauging stations
#read a basin shapefile

for basin_id in df_basins['basin_id']:
    basin_shapefile = gpd.read_file(f'data/prms_drainage_area_shapes/model_{basin_id}_nhru.shp')
    #create another shapefile name basin_shapefile_buffer with 10km buffer
    basin_shapefile_buffer = basin_shapefile.copy()
    basin_shapefile_buffer['geometry'] = basin_shapefile_buffer.buffer(10000) #buffer 10km

    #convert the basin shapefile to the same coordinate system as the stations
    basin_shapefile = basin_shapefile.to_crs(epsg=4326)
    basin_shapefile_buffer = basin_shapefile_buffer.to_crs(epsg=4326)
    #dissolve the internal boundaries of the basin
    basin_shapefile = basin_shapefile.dissolve()
    
    #filter stations that lies within the basin_shapefile
    #convert the stations to geodataframe
    stn_MA = gpd.GeoDataFrame(station_MA,geometry=gpd.points_from_xy(station_MA['lon'],station_MA['lat']))
    #make a list of stations that overlap with the basin
    stn_MA = stn_MA[stn_MA.within(basin_shapefile_buffer.unary_union)]
    stn_MA = stn_MA.reset_index(drop=True)
    #save the shapefile of stations
    stn_MA.to_file(f'data/basin_shapefile_with_gauges/basin_{basin_id}_stations.shp')
    #save the shapefile of basin
    basin_shapefile.to_file(f'data/basin_shapefile_with_gauges/basin_{basin_id}.shp')



