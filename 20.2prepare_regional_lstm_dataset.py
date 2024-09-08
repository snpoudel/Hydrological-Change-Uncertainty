import numpy as np
import pandas as pd
import os

#read all basin lists
basin_list = pd.read_csv('data/MA_basins_gauges_2000-2020_filtered.csv', sep='\t', dtype={'basin_id':str})


#--HISTORICAL--#
for id in basin_list['basin_id']:
    #read interpolate precip for this basin
    for precip_bucket in ['0-2', '2-4', '4-6', '6-8', '8-10']:
        for coverage in range(15):
            for comb in range(15):
                file_path = f'data/regional_lstm/idw_precip_buckets/pb{precip_bucket}/idw_precip{id}_coverage{coverage}_comb{comb}.csv'
                if os.path.exists(file_path):
                    #read interpolate precip
                    idw_precip =pd.read_csv(file_path)

                    #extract static features from previous input datasets
                    previous_file = pd.read_csv(f'data/regional_lstm/lstm_input/lstm_input_{id}.csv').iloc[[0]]
                    previous_file = previous_file.iloc[:,8:] #extract only static features
                    previous_file = round(previous_file, 2)
                    previous_file = pd.concat([previous_file]*len(idw_precip))
                    previous_file = previous_file.reset_index(drop=True)
                    
                    #read true discharge for this basin
                    true_flow = pd.read_csv(f'output/hbv_true_streamflow/hbv_true_output_{id}.csv')

                    #merge data,temp,flow from true file to previous file
                    previous_file['idw_precip'] = idw_precip['PRECIP']
                    previous_file['era5temp'] = true_flow['era5temp']
                    previous_file['date'] = true_flow['date']
                    previous_file['qobs'] = true_flow['streamflow']
                    previous_file = previous_file.reset_index(drop=True)

                    #save the final lstm input file
                    previous_file.to_csv(f'data/regional_lstm/processed_lstm_input/pb{precip_bucket}/lstm_input{id}_coverage{coverage}_comb{comb}.csv', index=False)



#--FUTURE--#
for id in basin_list['basin_id']:
    #read interpolate precip for this basin
    for precip_bucket in ['0-2', '2-4', '4-6', '6-8', '8-10']:
        for coverage in range(15):
            for comb in range(15):
                file_path = f'data/regional_lstm/future_idw_precip_buckets/pb{precip_bucket}/idw_precip{id}_coverage{coverage}_comb{comb}.csv'
                if os.path.exists(file_path):
                    #read interpolate precip
                    idw_precip =pd.read_csv(file_path)

                    #extract static features from previous input datasets
                    previous_file = pd.read_csv(f'data/regional_lstm/lstm_input/lstm_input_{id}.csv').iloc[[0]]
                    previous_file = previous_file.iloc[:,8:] #extract only static features
                    previous_file = round(previous_file, 2)
                    previous_file = pd.concat([previous_file]*len(idw_precip))
                    previous_file = previous_file.reset_index(drop=True)
                    
                    #read true discharge for this basin
                    true_flow = pd.read_csv(f'output/hbv_true_streamflow/hbv_true_output_{id}.csv')

                    #merge data,temp,flow from true file to previous file
                    previous_file['idw_precip'] = idw_precip['PRECIP']
                    previous_file['era5temp'] = true_flow['era5temp']
                    previous_file['date'] = true_flow['date']
                    previous_file['qobs'] = true_flow['streamflow']
                    previous_file = previous_file.reset_index(drop=True)

                    #save the final lstm input file
                    previous_file.to_csv(f'data/regional_lstm/future_processed_lstm_input/pb{precip_bucket}/lstm_input{id}_coverage{coverage}_comb{comb}.csv', index=False)