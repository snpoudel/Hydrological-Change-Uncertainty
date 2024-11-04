#load library
import numpy as np
import pandas as pd
import os

###---step 01---###
#  write objective functions for model evaluation ###
#write a function to calculate NSE
def nse(q_obs, q_sim):
    numerator = np.sum((q_obs - q_sim)**2)
    denominator = np.sum((q_obs - (np.mean(q_obs)))**2)
    nse_value = 1 - (numerator/denominator)
    return nse_value

#write a function to calculate RMSE
def rmse(q_obs, q_sim):
    rmse_value = np.sqrt(np.mean((q_obs - q_sim)**2))
    return rmse_value

#write a function to calculate Percentage BIAS
def pbias(q_obs, q_sim):
    pbias_value = (np.sum(q_obs - q_sim) / np.sum(q_obs)) * 100
    return pbias_value

#write a function to calculate KGE
def kge(q_obs, q_sim):
    r = np.corrcoef(q_obs, q_sim)[0,1]
    alpha = np.std(q_sim) / np.std(q_obs)
    beta = np.mean(q_sim) / np.mean(q_obs)
    kge_value = 1 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)
    return kge_value

#write a function to calculate percentage high flow bias
def high_flow_bias(q_obs, q_sim):
    q_obs = np.array(q_obs)
    q_sim = np.array(q_sim)
    q_obs_995_value = np.percentile(q_obs, 99.9)
    indices_q995 = np.where(q_obs > q_obs_995_value)
    q_obs_995 = q_obs[indices_q995]
    q_sim_995 = q_sim[indices_q995]
    hfb = (np.sum(q_obs_995 - q_sim_995) / np.sum(q_obs_995)) * 100
    return hfb


###---step 02---###
basin_list = pd.read_csv("data/regional_lstm/MA_basins_gauges_2000-2020_filtered.csv", dtype={'basin_id':str})
used_basin_list = basin_list['basin_id']

df_total = pd.DataFrame() #create an empty dataframe to store the results
for id in used_basin_list:
    # id = '01109060'
    grid_coverage = np.arange(12)
    grid_coverage = np.append(grid_coverage, [99])

    #Loop through each basin
    for grid in grid_coverage: #1
        #read true streamflow
        true_hbv_flow = pd.read_csv(f'output/hbv_true_streamflow/hbv_true_output_{id}.csv')
        true_hbv_flow = true_hbv_flow[364:] #remove the first 364 days
        true_hbv_flow = true_hbv_flow.reset_index(drop=True)
        #read true precipitation
        true_precip = pd.read_csv(f'data/true_precip/true_precip{id}.csv')

        for combination in range(10): #2
            #Read real streamflow from interpolated precipitation
            file_path = f'output/hbv_idw_recalib_streamflow/hbv_idw_recalib_streamflow{id}_coverage{grid}_comb{combination}.csv'
            if os.path.exists(file_path):
                #read real hbv flow
                # if os.path.exists(f'output/hbv_idw_streamflow/hbv_idw_streamflow{id}_coverage{grid}_comb{combination}.csv'):             
                real_hbv_flow = pd.read_csv(f'output/hbv_idw_streamflow/hbv_idw_streamflow{id}_coverage{grid}_comb{combination}.csv')
                real_hbv_flow = real_hbv_flow[364:] #remove the first 364 days
                real_hbv_flow = real_hbv_flow.reset_index(drop=True)
                #read recalibrated hbv flow
                recal_hbv_flow = pd.read_csv(f'output/hbv_idw_recalib_streamflow/hbv_idw_recalib_streamflow{id}_coverage{grid}_comb{combination}.csv')
                recal_hbv_flow = recal_hbv_flow[364:] #remove the first 364 days
                recal_hbv_flow = recal_hbv_flow.reset_index(drop=True)
                #rea real hymod flow
                real_hymod_flow = pd.read_csv(f'output/hymod_idw_streamflow/hymod_interpol_streamflow{id}_coverage{grid}_comb{combination}.csv')
                real_hymod_flow = real_hymod_flow[364:] #remove the first 364 days
                real_hymod_flow = real_hymod_flow.reset_index(drop=True)
                #read real lstm flow
                if os.path.exists(f'output/regional_lstm/historical/lstm_input{id}_coverage{grid}_comb{combination}.csv'):
                    real_lstm_flow = pd.read_csv(f'output/regional_lstm/historical/lstm_input{id}_coverage{grid}_comb{combination}.csv')
                    real_lstm_hymod_flow = pd.read_csv(f'output/regional_lstm_hymod/final_output/historical/hymod_lstm{id}_coverage{grid}_comb{combination}.csv')
            
                #read real precipitation
                real_precip = pd.read_csv(f'data/idw_precip/idw_precip{id}_coverage{grid}_comb{combination}.csv')

                #now calculate nse, rmse, pbias, kge, hfb for real hbv and hymod streamflow against true hbv streamflow
                #calculate results only for validation period
                val_pd = 5120 # ~ validation period starts from 2000th day
                #for hbv model
                nse_hbv = nse(true_hbv_flow['streamflow'][val_pd:], real_hbv_flow['streamflow'][val_pd:])
                rmse_hbv = rmse(true_hbv_flow['streamflow'][val_pd:], real_hbv_flow['streamflow'][val_pd:])
                pbias_hbv = pbias(true_hbv_flow['streamflow'][val_pd:], real_hbv_flow['streamflow'][val_pd:])
                kge_hbv = kge(true_hbv_flow['streamflow'][val_pd:], real_hbv_flow['streamflow'][val_pd:])
                hfb_hbv = high_flow_bias(true_hbv_flow['streamflow'][val_pd:], real_hbv_flow['streamflow'][val_pd:])
                #for recalibrated hbv model
                nse_recal_hbv = nse(true_hbv_flow['streamflow'][val_pd:], recal_hbv_flow['streamflow'][val_pd:])
                rmse_recal_hbv = rmse(true_hbv_flow['streamflow'][val_pd:], recal_hbv_flow['streamflow'][val_pd:])
                pbias_recal_hbv = pbias(true_hbv_flow['streamflow'][val_pd:], recal_hbv_flow['streamflow'][val_pd:])
                kge_recal_hbv = kge(true_hbv_flow['streamflow'][val_pd:], recal_hbv_flow['streamflow'][val_pd:])
                hfb_recal_hbv = high_flow_bias(true_hbv_flow['streamflow'][val_pd:], recal_hbv_flow['streamflow'][val_pd:])
                #for hymod model
                nse_hymod = nse(true_hbv_flow['streamflow'][val_pd:], real_hymod_flow['streamflow'][val_pd:])
                rmse_hymod = rmse(true_hbv_flow['streamflow'][val_pd:], real_hymod_flow['streamflow'][val_pd:])
                pbias_hymod = pbias(true_hbv_flow['streamflow'][val_pd:], real_hymod_flow['streamflow'][val_pd:])
                kge_hymod = kge(true_hbv_flow['streamflow'][val_pd:], real_hymod_flow['streamflow'][val_pd:])
                hfb_hymod = high_flow_bias(true_hbv_flow['streamflow'][val_pd:], real_hymod_flow['streamflow'][val_pd:])
                #for lstm model
                if os.path.exists(f'output/regional_lstm/historical/lstm_input{id}_coverage{grid}_comb{combination}.csv'):
                    nse_lstm = nse(true_hbv_flow['streamflow'][val_pd:], real_lstm_flow['streamflow'][val_pd:])
                    rmse_lstm = rmse(true_hbv_flow['streamflow'][val_pd:], real_lstm_flow['streamflow'][val_pd:])
                    pbias_lstm = pbias(true_hbv_flow['streamflow'][val_pd:], real_lstm_flow['streamflow'][val_pd:])
                    kge_lstm = kge(true_hbv_flow['streamflow'][val_pd:], real_lstm_flow['streamflow'][val_pd:])
                    hfb_lstm = high_flow_bias(true_hbv_flow['streamflow'][val_pd:], real_lstm_flow['streamflow'][val_pd:])
                else:
                    nse_lstm, rmse_lstm, pbias_lstm, kge_lstm, hfb_lstm = np.NAN, np.NAN, np.NAN, np.NAN, np.NAN

                #for lstm-hymod model
                if os.path.exists(f'output/regional_lstm_hymod/final_output/historical/hymod_lstm{id}_coverage{grid}_comb{combination}.csv'):
                    nse_lstm_hymod = nse(true_hbv_flow['streamflow'][val_pd:], real_lstm_hymod_flow['hymod_lstm_streamflow'][val_pd:])
                    rmse_lstm_hymod = rmse(true_hbv_flow['streamflow'][val_pd:], real_lstm_hymod_flow['hymod_lstm_streamflow'][val_pd:])
                    pbias_lstm_hymod = pbias(true_hbv_flow['streamflow'][val_pd:], real_lstm_hymod_flow['hymod_lstm_streamflow'][val_pd:])
                    kge_lstm_hymod = kge(true_hbv_flow['streamflow'][val_pd:], real_lstm_hymod_flow['hymod_lstm_streamflow'][val_pd:])
                    hfb_lstm_hymod = high_flow_bias(true_hbv_flow['streamflow'][val_pd:], real_lstm_hymod_flow['hymod_lstm_streamflow'][val_pd:])
                else:
                    nse_lstm_hymod, rmse_lstm_hymod, pbias_lstm_hymod, kge_lstm_hymod, hfb_lstm_hymod = np.NAN, np.NAN, np.NAN, np.NAN, np.NAN

                #for precipitation
                nse_precip = nse(true_precip['PRECIP'], real_precip['PRECIP'])
                rmse_precip = rmse(true_precip['PRECIP'], real_precip['PRECIP'])
                if np.array_equal(true_precip['PRECIP'], real_precip['PRECIP']):
                    rmse_precip = 0
                pbias_precip = pbias(true_precip['PRECIP'], real_precip['PRECIP'])
                kge_precip = kge(true_precip['PRECIP'], real_precip['PRECIP'])

                #save the results in a dataframe
                df_result = pd.DataFrame({'station_id':[id], 'grid':[grid], 'combination':[combination],
                                            'NSE(HBV)':[nse_hbv], 'RMSE(HBV)':[rmse_hbv], 'BIAS(HBV)':[pbias_hbv], 'KGE(HBV)':[kge_hbv], 'HFB(HBV)':[hfb_hbv],
                                            'NSE(RECAL_HBV)':[nse_recal_hbv], 'RMSE(RECAL_HBV)':[rmse_recal_hbv], 'BIAS(RECAL_HBV)':[pbias_recal_hbv], 'KGE(RECAL_HBV)':[kge_recal_hbv], 'HFB(RECAL_HBV)':[hfb_recal_hbv],
                                            'NSE(HYMOD)':[nse_hymod], 'RMSE(HYMOD)':[rmse_hymod], 'BIAS(HYMOD)':[pbias_hymod], 'KGE(HYMOD)':[kge_hymod], 'HFB(HYMOD)':[hfb_hymod],
                                            'NSE(LSTM)':[nse_lstm], 'RMSE(LSTM)':[rmse_lstm], 'BIAS(LSTM)':[pbias_lstm], 'KGE(LSTM)':[kge_lstm], 'HFB(LSTM)':[hfb_lstm],
                                            'NSE(HYMOD-LSTM)':[nse_lstm_hymod], 'RMSE(HYMOD-LSTM)':[rmse_lstm_hymod], 'BIAS(HYMOD-LSTM)':[pbias_lstm_hymod], 'KGE(HYMOD-LSTM)':[kge_lstm_hymod], 'HFB(HYMOD-LSTM)':[hfb_lstm_hymod],
                                            'NSE(PRECIP)':[nse_precip], 'RMSE(PRECIP)':[rmse_precip], 'BIAS(PRECIP)':[pbias_precip], 'KGE(PRECIP)':[kge_precip]})
                
                df_total = pd.concat([df_total, df_result], axis=0)
        #End of loop 23
        
df_total.to_csv(f'output/allbasins_diagnostics_validperiod.csv', index=False)    
#End of loop 1
