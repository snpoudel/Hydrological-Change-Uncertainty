#import libraries
import numpy as np
import pandas as pd
import os
import lmoments3 as lm
from lmoments3 import distr
from scipy.stats import gumbel_r
from scipy.stats import genextreme
from scipy.stats import pearson3
import warnings
warnings.filterwarnings('ignore')

os.chdir('Z:/MA-Precip-Uncertainty-GaugeData/')

##--For Climate scenario 15--##

#function that returns flood specific return period
def return_flood(data, return_period, distribution, method):
    '''
    data: annual extreme values, eg., [10, 20, 30]
    return_period: 5-yr, eg., 5
    distribution: Gumbel = 'gum' Log-Pearson3 =  'lp' GEV = 'gev'
    method: L-moment = 'lm' or MLE = 'mle'
    '''
    data = data[data>0] #only keep non zero values
    #calculate non exceedance probability from return period
    exceedance_prob = 1/return_period
    nep = 1 - exceedance_prob #non-exceedance probability

    if distribution == 'gum': ##--Gumbel Distribution--##
        
        if method == 'lm': #fit using L-moment
            params = distr.gum.lmom_fit(data)
            model = distr.gum(**params)
            flood = model.ppf(nep)
            return flood
        if method == 'mle': #fit using MLE
            params = gumbel_r.fit(data) #MLE is default
            flood = gumbel_r.ppf(nep, loc=params[0], scale=params[1])
            return flood
        
    if distribution == 'gev': ##--Generalized Extreme Value distribution--##
        
        if method == 'lm':
            #fit with L-moment
            params = distr.gev.lmom_fit(data)
            model = distr.gev(**params)
            flood = model.ppf(nep)
            return flood
        if method == 'mle': #fit with MLE
            params = genextreme.fit(data)
            flood = genextreme.ppf(nep, c=params[0], loc=params[1], scale=params[2])
            return flood
        
    if distribution == 'lp': ##--Log-Normal distribution--##
        
        if method == 'lm':
            #fit with L-moment
            params = distr.pe3.lmom_fit(np.log(data))
            model = distr.pe3(**params)
            flood = np.exp(model.ppf(nep))
            return flood
        if method == 'mle':
            #fit with MLE
            params = pearson3.fit(np.log(data))
            flood = np.exp(pearson3.ppf(nep, skew=params[0], loc=params[1], scale=params[2]))
            return flood


#function to return change in design flood wrt true change in design flood 
def percent_change(value_future, value_historical, true_change): #value_future and value_historical are estimated from a model and true_change is from truth model
    estimated_change_model = ((value_future - value_historical)/value_historical)*100
    return np.round(estimated_change_model - true_change, 3)

#initialize the dataframe
df_change = pd.DataFrame() #merge final
df_change_dist = pd.DataFrame() #merge after each distribution

start_year = np.arange(50, 1000, 50)
end_year = np.arange(100, 1050, 50)
# start_year = [50]
# end_year = [100]
for syear, eyear in zip(start_year, end_year):
    #loop through each method and distribution
    for method in ['mle', 'lm']: #['mle', 'lm']:
        for distribution in ['gev', 'gum']:
            df_tyr_flood =pd.DataFrame(columns=['model', 'grid', 'comb',  '50yr_flood',  'precip_rmse'])
            df_change_flood = pd.DataFrame(columns=['station', 'model',  'change_50yr_flood', 'precip_rmse'])
            # basin_id = '01109060'
            basin_list = pd.read_csv("data/ma29basins.csv", dtype={'basin_id':str})
            used_basin_list = basin_list['basin_id']

            for basin_id in used_basin_list:
                #True precipitation
                true_precip = pd.read_csv(f'data/true_precip/true_precip{basin_id}.csv')
                future_true_precip = pd.read_csv(f'data/future/future_true_precip/future_true_precip{basin_id}.csv')

                #HBV truth model
                #read the streamflow data
                hbv_truth = pd.read_csv(f'output/hbv_true/hbv_true{basin_id}.csv')
                hbv_truth['year'] = hbv_truth['date'].apply(lambda x: int(x.split('-')[0]))
                data = hbv_truth.groupby('year')['streamflow'].max()
                
                #calculate the 20, 10 and 20 years flood
                flood_50 =  return_flood(data,50,distribution,method)
                true_tyr_flood =pd.DataFrame({'model':'HBV True', 'grid':'NA', 'comb':'NA',  '50yr_flood':flood_50,  'precip_rmse':0}, index=[0])
                df_tyr_flood = pd.concat([df_tyr_flood, true_tyr_flood], ignore_index=True)
                flood_50t  =  flood_50 #save true floods

                #read the future streamflow data
                hbv_true_future = pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/hbv_true/hbv_true{basin_id}.csv')
                hbv_true_future['year'] = hbv_true_future['date'].apply(lambda x: int(x.split('-')[0]))
                data = hbv_true_future.groupby('year')['streamflow'].max()
                #calculate the 5, 10, and 20 years flood
                flood_50 =  return_flood(data,50,distribution,method)
                true_tyr_flood_future =pd.DataFrame({'model':'HBV True Future', 'grid':'NA', 'comb':'NA',  '50yr_flood':flood_50,  'precip_rmse':0}, index=[0])
                df_tyr_flood = pd.concat([df_tyr_flood, true_tyr_flood_future], ignore_index=True)
                
                #true change in 5 10 20yr flood
                true_change_10yr = ((flood_50 - flood_50t)/flood_50t)*100

                #loop through each grid coverage and combination
                grid_list = np.arange(11)
                grid_list = np.append(grid_list, [99])
                for grid in grid_list:
                    for comb in range(11):
                        #--HISTORICAL DATA--#
                        #Interpolated precipitation
                        file_path = f'output/rehbv/rehbv{basin_id}_coverage{grid}_comb{comb}.csv'
                        if os.path.exists(file_path):
                            idw_precip = pd.read_csv(f'data/noisy_precip/noisy_precip{basin_id}_coverage{grid}_comb{comb}.csv')
                            precip_rmse = np.sqrt(np.mean((true_precip['PRECIP'] - idw_precip['PRECIP'])**2)) #calculate the rmse
                            precip_rmse = np.round(precip_rmse, 3)
                            if np.array_equal(true_precip['PRECIP'], idw_precip['PRECIP']):
                                rmse_precip = 0
                    

                            #HBV recalibrated model
                            #read the streamflow data
                            hbv_recalibrated = pd.read_csv(f'output/rehbv/rehbv{basin_id}_coverage{grid}_comb{comb}.csv')
                            hbv_recalibrated['year'] = hbv_recalibrated['date'].apply(lambda x: int(x.split('-')[0]))
                            #only keep 50 years of data
                            hbv_recalibrated = hbv_recalibrated[(hbv_recalibrated['year']>=syear) & (hbv_recalibrated['year']<eyear)].reset_index(drop=True)
                            data = hbv_recalibrated.groupby('year')['streamflow'].max()
                            #calculate the 5, 10, and 20 years flood
                            flood_50 =  return_flood(data,50,distribution,method)
                            temp_df_hbvr = pd.DataFrame({'model':'HBV Recalib', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_hbvr], ignore_index=True)

                            #Full-Hymod model
                            #read the streamflow data
                            hymod = pd.read_csv(f'output/hymod/hymod{basin_id}_coverage{grid}_comb{comb}.csv')
                            hymod['year'] = hymod['date'].apply(lambda x: int(x.split('-')[0]))
                            #only keep 50 years of data
                            hymod = hymod[(hymod['year']>=syear) & (hymod['year']<eyear)].reset_index(drop=True)
                            data = hymod.groupby('year')['streamflow'].max()
                            #calculate the 5, 10, and 20 years flood
                            flood_50 =  return_flood(data,50,distribution,method)
                            temp_df_fullhy = pd.DataFrame({'model':'Full-Hymod', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_fullhy], ignore_index=True)
                            
                            #Hymod model
                            #read the streamflow data
                            hymod = pd.read_csv(f'output/simp_hymod/simp_hymod{basin_id}_coverage{grid}_comb{comb}.csv')
                            hymod['year'] = hymod['date'].apply(lambda x: int(x.split('-')[0]))
                            #only keep 50 years of data
                            hymod = hymod[(hymod['year']>=syear) & (hymod['year']<eyear)].reset_index(drop=True)
                            data = hymod.groupby('year')['streamflow'].max()
                            #calculate the 5, 10, and 20 years flood
                            flood_50 =  return_flood(data,50,distribution,method)
                            temp_df_hy = pd.DataFrame({'model':'Hymod', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_hy], ignore_index=True)

                            #LSTM model
                            #read the streamflow data
                            if os.path.exists(f'output/regional_lstm/historical/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv'):
                                lstm = pd.read_csv(f'output/regional_lstm/historical/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv')
                                lstm['year'] = lstm['date'].apply(lambda x: int(x.split('-')[0]))
                                #only keep 50 years of data
                                lstm = lstm[(lstm['year']>=syear) & (lstm['year']<eyear)].reset_index(drop=True)
                                data = lstm.groupby('year')['streamflow'].max()
                                data = data[data>0]#only keep non zero values
                                #calculate the 5, 10, and 20 years flood
                                flood_50 =  return_flood(data,50,distribution,method)
                            else:
                                flood_50 = np.NAN

                            temp_df_lstm = pd.DataFrame({'model':'LSTM', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_lstm], ignore_index=True)

                            #FULL-HYMOD-LSTM model
                            #read the streamflow data
                            if os.path.exists(f'output/regional_lstm_hymod/final_output/historical/hymod_lstm{basin_id}_coverage{grid}_comb{comb}.csv'):
                                lstm = pd.read_csv(f'output/regional_lstm_hymod/final_output/historical/hymod_lstm{basin_id}_coverage{grid}_comb{comb}.csv')
                                lstm['year'] = lstm['date'].apply(lambda x: int(x.split('-')[0]))
                                #only keep 50 years of data
                                lstm = lstm[(lstm['year']>=syear) & (lstm['year']<eyear)].reset_index(drop=True)
                                data = lstm.groupby('year')['hymod_lstm_streamflow'].max()
                                data = data[data>0]#only keep non zero values
                                #calculate the 5, 10, and 20 years flood
                                flood_50 =  return_flood(data,50,distribution,method)
                            else:
                                flood_50 = np.NAN

                            temp_df_lstm_fullhymod = pd.DataFrame({'model':'FULL-HYMOD-LSTM', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_lstm_fullhymod], ignore_index=True)

                            #HYMOD-LSTM model
                            #read the streamflow data
                            if os.path.exists(f'output/regional_lstm_simp_hymod/final_output/historical/hymod_lstm{basin_id}_coverage{grid}_comb{comb}.csv'):
                                lstm = pd.read_csv(f'output/regional_lstm_simp_hymod/final_output/historical/hymod_lstm{basin_id}_coverage{grid}_comb{comb}.csv')
                                lstm['year'] = lstm['date'].apply(lambda x: int(x.split('-')[0]))
                                #only keep 50 years of data
                                lstm = lstm[(lstm['year']>=syear) & (lstm['year']<eyear)].reset_index(drop=True)
                                data = lstm.groupby('year')['simp_hymod_lstm_streamflow'].max()
                                data = data[data>0]#only keep non zero values
                                #calculate the 5, 10, and 20 years flood
                                flood_50 =  return_flood(data,50,distribution,method)
                            else:
                                flood_50 = np.NAN

                            temp_df_lstm_hymod = pd.DataFrame({'model':'HYMOD-LSTM', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_lstm_hymod], ignore_index=True)
##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
                            #--FUTURE DATA--#

                            #HBV recalibrated model future
                            #read the streamflow data
                            hbv_recalibrated_future =pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/rehbv/rehbv{basin_id}_coverage{grid}_comb{comb}.csv')
                            hbv_recalibrated_future['year'] = hbv_recalibrated_future['date'].apply(lambda x: int(x.split('-')[0]))
                            # only keep 50 years of data
                            hbv_recalibrated_future = hbv_recalibrated_future[(hbv_recalibrated_future['year']>=syear) & (hbv_recalibrated_future['year']<eyear)].reset_index(drop=True)
                            data = hbv_recalibrated_future.groupby('year')['streamflow'].max()
                            #calculate the 5, 10, and 20 years flood
                            flood_50 =  return_flood(data,50,distribution,method)
                            temp_df_hbvrf = pd.DataFrame({'model':'HBV Recalib Future', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_hbvrf], ignore_index=True)

                            #Full-Hymod model future
                            #read the streamflow data
                            hymod_future = pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/hymod/hymod{basin_id}_coverage{grid}_comb{comb}.csv')
                            hymod_future['year'] = hymod_future['date'].apply(lambda x: int(x.split('-')[0]))
                            # only keep 50 years of data
                            hymod_future = hymod_future[(hymod_future['year']>=syear) & (hymod_future['year']<eyear)].reset_index(drop=True)
                            data = hymod_future.groupby('year')['streamflow'].max()
                            #calculate the 5, 10, and 20 years flood
                            flood_50 =  return_flood(data,50,distribution,method)
                            temp_df_fullhyf = pd.DataFrame({'model':'Full-Hymod Future', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_fullhyf], ignore_index=True)

                            #Hymod model future
                            #read the streamflow data
                            hymod_future = pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/simp_hymod/simp_hymod{basin_id}_coverage{grid}_comb{comb}.csv')
                            hymod_future['year'] = hymod_future['date'].apply(lambda x: int(x.split('-')[0]))
                            # only keep 50 years of data
                            hymod_future = hymod_future[(hymod_future['year']>=syear) & (hymod_future['year']<eyear)].reset_index(drop=True)
                            data = hymod_future.groupby('year')['streamflow'].max()
                            #calculate the 5, 10, and 20 years flood
                            flood_50 =  return_flood(data,50,distribution,method)
                            temp_df_hyf = pd.DataFrame({'model':'Hymod Future', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_hyf], ignore_index=True)

                            #LSTM model future
                            #read the streamflow data
                            if os.path.exists(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/regional_lstm/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv'):
                                lstm_future = pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/regional_lstm/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv')
                                lstm_future['year'] = lstm_future['date'].apply(lambda x: int(x.split('-')[0]))
                                # only keep 50 years of data
                                lstm_future = lstm_future[(lstm_future['year']>=syear) & (lstm_future['year']<eyear)].reset_index(drop=True)
                                data = lstm_future.groupby('year')['streamflow'].max()
                                data = data[data>0]#only keep non zero values
                                #calculate the 5, 10, and 20 years flood
                                flood_50 =  return_flood(data,50,distribution,method)
                            else:
                                flood_50 = np.NaN
                            temp_df_lstmf = pd.DataFrame({'model':'LSTM Future', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_lstmf], ignore_index=True)

                            #Full-HYMOD-LSTM model future
                            #read the streamflow data
                            if os.path.exists(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/regional_lstm_hymod/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv'):
                                lstm_future = pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/regional_lstm_hymod/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv')
                                lstm_future['year'] = lstm_future['date'].apply(lambda x: int(x.split('-')[0]))
                                # only keep 50 years of data
                                lstm_future = lstm_future[(lstm_future['year']>=syear) & (lstm_future['year']<eyear)].reset_index(drop=True)
                                data = lstm_future.groupby('year')['hymod_lstm_streamflow'].max()
                                data = data[data>0]#only keep non zero values
                                #calculate the 5, 10, and 20 years flood
                                flood_50 =  return_flood(data,50,distribution,method)
                            else:
                                flood_50 = np.NaN
                            temp_df_lstm_fullhymodf = pd.DataFrame({'model':'HYMOD-LSTM Future', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_lstm_fullhymodf], ignore_index=True)

                            #HYMOD-LSTM model future
                            #read the streamflow data
                            if os.path.exists(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/regional_lstm_simp_hymod/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv'):
                                lstm_future = pd.read_csv(f'Z:/MA-Precip-Uncertainty-Exp-climscenarios/output/scenario15/regional_lstm_simp_hymod/lstm_input{basin_id}_coverage{grid}_comb{comb}.csv')
                                lstm_future['year'] = lstm_future['date'].apply(lambda x: int(x.split('-')[0]))
                                # only keep 50 years of data
                                lstm_future = lstm_future[(lstm_future['year']>=syear) & (lstm_future['year']<eyear)].reset_index(drop=True)
                                data = lstm_future.groupby('year')['simp_hymod_lstm_streamflow'].max()
                                data = data[data>0]#only keep non zero values
                                #calculate the 5, 10, and 20 years flood
                                flood_50 =  return_flood(data,50,distribution,method)
                            else:
                                flood_50 = np.NaN
                            temp_df_lstm_hymodf = pd.DataFrame({'model':'HYMOD-LSTM Future', 'grid':grid, 'comb':comb,  '50yr_flood':flood_50,  'precip_rmse':precip_rmse}, index=[0])
                            df_tyr_flood = pd.concat([df_tyr_flood, temp_df_lstm_hymodf], ignore_index=True)


                            change_hbv_recalib = pd.DataFrame({'station':basin_id,'model':'HBV Recalib',
                                            'change_50yr_flood':percent_change(temp_df_hbvrf['50yr_flood'] , temp_df_hbvr['50yr_flood'], true_change_10yr),'precip_rmse':precip_rmse}, index=[0])
                            
                            change_full_hymod = pd.DataFrame({'station':basin_id,'model':'Full-Hymod', 
                                            'change_50yr_flood':percent_change(temp_df_fullhyf['50yr_flood'] , temp_df_fullhy['50yr_flood'], true_change_10yr),'precip_rmse':precip_rmse}, index=[0])
                            
                            change_lstm = pd.DataFrame({'station':basin_id,'model':'LSTM', 
                                            'change_50yr_flood':percent_change(temp_df_lstmf['50yr_flood'] , temp_df_lstm['50yr_flood'], true_change_10yr), 'precip_rmse':precip_rmse}, index=[0])
                            
                            change_full_hymod_lstm = pd.DataFrame({'station':basin_id,'model':'FULL-HYMOD-LSTM', 
                                            'change_50yr_flood':percent_change(temp_df_lstm_fullhymodf['50yr_flood'] , temp_df_lstm_fullhymod['50yr_flood'], true_change_10yr), 'precip_rmse':precip_rmse}, index=[0])
                            
                            change_hymod_lstm = pd.DataFrame({'station':basin_id,'model':'HYMOD-LSTM', 
                                            'change_50yr_flood':percent_change(temp_df_lstm_hymodf['50yr_flood'] , temp_df_lstm_hymod['50yr_flood'], true_change_10yr), 'precip_rmse':precip_rmse}, index=[0])
                            
                            change_hymod = pd.DataFrame({'station':basin_id,'model':'Hymod', 
                                            'change_50yr_flood':percent_change(temp_df_hyf['50yr_flood'] , temp_df_hy['50yr_flood'], true_change_10yr), 'precip_rmse':precip_rmse}, index=[0])
                            
                            
                            df_change_flood = pd.concat([df_change_flood, change_hbv_recalib,  change_full_hymod, change_hymod, change_lstm, change_full_hymod_lstm, change_hymod_lstm], ignore_index=True)
                            #add method and distribution to the dataframe
                            df_change_flood['method'] = method
                            df_change_flood['distribution'] = distribution
            #merge the dataframes after each distribution
            df_change_dist = pd.concat([df_change_dist, df_change_flood], ignore_index=True)
        #merge the dataframes after each method and distribution
        df_change = pd.concat([df_change, df_change_dist], ignore_index=True)
#save the dataframes after all methods and distributions
df_change.to_csv(f'Z:/MA-Precip-Uncertainty-Exp-ExtremeFitting/output/only50yr_flood.csv', index=False)