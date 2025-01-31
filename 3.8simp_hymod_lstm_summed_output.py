#load libraries
import numpy as np
import pandas as pd
import os

#read basin list
basin_list = pd.read_csv("data/ma29basins.csv", dtype={'basin_id':str})['basin_id'].values

#Historical
for id in basin_list:
    for coverage in range(105):
        for comb in range(15):
            file_path = f'output/regional_lstm_simp_hymod/merged/historical/lstm_input{id}_coverage{coverage}_comb{comb}.csv'
            if os.path.exists(file_path):
                lstm_error = pd.read_csv(file_path)
                hymod_simflow = pd.read_csv(f'output/hymod/hymod{id}_coverage{coverage}_comb{comb}.csv').drop(columns=['Unnamed: 0'])
                #convert date to iso format
                hymod_simflow['date'] = hymod_simflow['date'].apply(lambda x: f"{x.split('-')[0].zfill(4)}-{x.split('-')[1].zfill(2)}-{x.split('-')[2].zfill(2)}")
                #merge by date
                temp_df = pd.merge(lstm_error, hymod_simflow, on='date', how='inner')
                temp_df['hymod_lstm_streamflow']=temp_df['streamflow']+temp_df['streamflow_error']

                #only extract date and hymod_lstm_streamflow
                temp_df = temp_df.loc[:,['date', 'hymod_lstm_streamflow']]
                
                #round to 2 decimal places
                temp_df['hymod_lstm_streamflow'] = temp_df['hymod_lstm_streamflow'].apply(lambda x: round(x,2))
                #save as a csv file
                temp_df.to_csv(f'output/regional_lstm_simp_hymod/final_output/historical/hymod_lstm{id}_coverage{coverage}_comb{comb}.csv', index=False)


#Future
for id in basin_list:
    for coverage in range(105):
        for comb in range(15):
            file_path = f'output/regional_lstm_simp_hymod/merged/future/lstm_input{id}_coverage{coverage}_comb{comb}.csv'
            if os.path.exists(file_path):
                lstm_error = pd.read_csv(file_path)
                hymod_simflow = pd.read_csv(f'output/future/hymod/hymod{id}_coverage{coverage}_comb{comb}.csv')
                #convert date to iso format
                hymod_simflow['date'] = hymod_simflow['date'].apply(lambda x: f"{x.split('-')[0].zfill(4)}-{x.split('-')[1].zfill(2)}-{x.split('-')[2].zfill(2)}")
                
                #merge by date
                temp_df = pd.merge(lstm_error, hymod_simflow, on='date', how='inner')
                temp_df['hymod_lstm_streamflow']=temp_df['streamflow']+temp_df['streamflow_error']

                #only extract date and hymod_lstm_streamflow
                temp_df = temp_df.loc[:,['date', 'hymod_lstm_streamflow']]

                #round to 2 decimal places
                temp_df['hymod_lstm_streamflow'] = temp_df['hymod_lstm_streamflow'].apply(lambda x: round(x,2))

                #save as a csv file
                temp_df.to_csv(f'output/regional_lstm_simp_hymod/final_output/future/hymod_lstm{id}_coverage{coverage}_comb{comb}.csv', index=False)
                