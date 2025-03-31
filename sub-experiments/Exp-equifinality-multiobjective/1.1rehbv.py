#load libraries
import numpy as np
import pandas as pd
import os
from geneticalgorithm import geneticalgorithm as ga
from hbv_model import hbv
from mpi4py import MPI
import warnings
warnings.filterwarnings("ignore")

#Set up communicator to parallelize job in cluster using MPI
comm = MPI.COMM_WORLD #Get the default communicator object
rank = comm.Get_rank() #Get the rank of the current process
size = comm.Get_size() #Get the total number of processes

#change current working directory
os.chdir('/home/fs01/sp2596/MA-Precip-Uncertainty-GaugeData')
########### Calibrate hbv model ###########
#Write a function that calibrates hymod model
def calibNSE(station_id, grid, combination):
    #read input csv file
    #read interpolated precipitation
    df = pd.read_csv(f'data/noisy_precip/noisy_precip{station_id}_coverage{grid}_comb{combination}.csv')
    ###LET'S CALIBRATE MODEL FOR first 25 years ###
    calib_time = 9125 #25 years is 9125 days
    p = df["PRECIP"][0:calib_time] #precipitation
    date = df["DATE"][0:calib_time] #date

    #read temperature, latitude, and observed flow (true hbv flow)
    df_true = pd.read_csv(f'output/hbv_true/hbv_true{station_id}.csv')
    temp = df_true["era5temp"][0:calib_time] #temperature
    latitude = df_true["latitude"][0:calib_time] #latitude
    routing = 1 # 0: no routing, 1 allows running
    q_obs = df_true["streamflow"][0:calib_time]  #validation data / observed flow

    ##genetic algorithm for hbv model calibration
    #reference: https://github.com/rmsolgi/geneticalgorithm
    #write a function you want to minimize

    def cal_nse(obs, sim):
        denominator = np.sum((obs - (np.mean(obs)))**2)
        numerator = np.sum((obs - sim)**2)
        nse_value = 1 - (numerator/denominator)
        return nse_value

    #function to calculate nse by seperating into less than 25th percentile, greater than 75th percentile, and total flow
    def nse(pars):
        q_sim = hbv(pars, p, temp, date, latitude, routing)
        #use first 2 years as spinup
        q_sim = q_sim[730:]
        q_obs_inner = q_obs[730:]
        #calculate nse for total flow
        nse_total = cal_nse(q_obs_inner, q_sim)
        #calculate nse for low flow
        q_obs_low = q_obs_inner[q_obs_inner < np.percentile(q_obs_inner, 25)]
        q_sim_low = q_sim[q_obs_inner < np.percentile(q_obs_inner, 25)]
        nse_low = cal_nse(q_obs_low, q_sim_low)
        #calculate nse for high flow
        q_obs_high = q_obs_inner[q_obs_inner > np.percentile(q_obs_inner, 75)]
        q_sim_high = q_sim[q_obs_inner > np.percentile(q_obs_inner, 75)]
        nse_high = cal_nse(q_obs_high, q_sim_high)
        #return the sum of nse values
        return -(nse_total + nse_low + nse_high) #minimize this (use negative sign if you need to maximize)

    varbound = np.array([[1,1000], #fc
                        [1,7], #beta
                        [0.01,0.99], #pwp
                        [1,999], #l
                        [0.01,0.99], #ks
                        [0.01,0.99], #ki
                        [0.0001, 0.99], #kb
                        [0.001, 0.99], #kperc
                        [0.5,2], #coeff_pet
                        [0.01,10], #ddf
                        [0.5,1.5], #scf
                        [-1,4], #ts
                        [-1,4], #tm
                        [-1,4], #tti
                        [0, 0.2], #whc
                        [0.1,1], #crf
                        [1,10]]) #maxbas

    algorithm_param = {
        'max_num_iteration': 100,              #100 Generations, higher is better, but requires more computational time
        'max_iteration_without_improv': None,   # Stopping criterion for lack of improvement
        'population_size': 2000,                 #200 Number of parameter-sets in a single iteration/generation(to start with population 10 times the number of parameters should be fine!)
        'parents_portion': 0.3,                 # Portion of new generation population filled by previous population
        'elit_ratio': 0.01,                     # Portion of the best individuals preserved unchanged
        'crossover_probability': 0.3,           # Chance of existing solution passing its characteristics to new trial solution
        'crossover_type': 'uniform',            # Create offspring by combining the parameters of selected parents
        'mutation_probability': 0.01            # Introduce random changes to the offspring’s parameters (0.1 is 10%)
    }

    model = ga(function = nse,
            dimension = 17, #number of parameters to be calibrated
            variable_type= 'real',
            variable_boundaries = varbound,
            algorithm_parameters = algorithm_param)

    model.run()
    #end of genetic algorithm

    #output of the genetic algorithm/best parameters
    best_parameters = model.output_dict
    param_value = best_parameters["variable"]
    nse_value = best_parameters["function"]
    nse_value = -nse_value #nse function gives -ve values, which is now reversed here to get true nse
    #convert into a dataframe
    df_param = pd.DataFrame(param_value).transpose()
    df_param = df_param.rename(columns={0:"fc", 1:"beta", 2:"pwp", 3:"l", 4:"ks", 5:"ki",
                             6:"kb", 7:"kperc",  8:"coeff_pet", 9:"ddf", 10:"scf", 11:"ts",
                             12:"tm", 13:"tti", 14:"whc", 15:"crf", 16:"maxbas"})
    df_param["station_id"] = str(station_id)
    df_param["nse"] = nse_value
    #save as a csv file
    return df_param #returns calibrated parameters and nse value
##End of function


#basin id
#id = '01108000'
lat_basin = pd.read_csv('data/basinID_withLatLon.csv', dtype={'STAID':str})

basin_list = pd.read_csv('data/ma29basins.csv', dtype={'basin_id':str})
basin_list['used_stations'] = basin_list['num_stations'] - 1 #use total -1 stations
basin_list['station_array'] = basin_list['used_stations'].apply(lambda x:np.array(np.append(np.arange(1,x+1), [99])))
basin_list = basin_list.explode('station_array').reset_index(drop=True)

id = basin_list['basin_id'][rank]
grid = basin_list['station_array'][rank] 

for combination in np.arange(12):
    file_path = f'data/noisy_precip/noisy_precip{id}_coverage{grid}_comb{combination}.csv'
    if os.path.exists(file_path):
        #---HISTORICAL OBSERVATION---#
        precip_in = pd.read_csv(f'data/noisy_precip/noisy_precip{id}_coverage{grid}_comb{combination}.csv')
        #Read temperature era5
        temp_in = pd.read_csv(f'data/temperature/temp{id}.csv')
        #Read latitude
        lat_in_df = lat_basin[lat_basin['STAID'] == id]
        lat_in = lat_in_df['LAT_CENT'].iloc[0]

        # #Read calibrated hbv parameters
        # params_in = calibNSE(id, grid, combination)

        # #save parameters as a csv file
        # params_in.to_csv(f'/home/fs01/sp2596/MA-Precip-Uncertainty-Exp-equifinality2/output/parameters/hbv_recalib/params{id}_grid{grid}_comb{combination}.csv')
        params_in = pd.read_csv(f'/home/fs01/sp2596/MA-Precip-Uncertainty-Exp-equifinality2/output/parameters/hbv_recalib/params{id}_grid{grid}_comb{combination}.csv')
        params_in = params_in.drop(columns=['Unnamed: 0'])

        params_in = params_in.iloc[0,:-2] #remove basin ID column
        params_in = np.array(params_in)

        # #run hbv model
        # q_sim = hbv(params_in, precip_in['PRECIP'], temp_in['tavg'], precip_in['DATE'], lat_in, routing=1)
        # q_sim = np.round(q_sim, 3)

        # #keep result in a dataframe
        # output_df = pd.DataFrame({ 'date':precip_in['DATE'], 'streamflow':q_sim })
        # #save output dataframe
        # output_df.to_csv(f'/home/fs01/sp2596/MA-Precip-Uncertainty-Exp-equifinality2/output/rehbv/rehbv{id}_coverage{grid}_comb{combination}.csv')



        #---FUTURE OBSERVATION---#
        precip_in = pd.read_csv(f'data/future/future_noisy_precip/future_noisy_precip{id}_coverage{grid}_comb{combination}.csv')
        #Read temperature era5
        temp_in = pd.read_csv(f'data/future/future_temperature/future_temp{id}.csv')
        #Read latitude
        lat_in_df = lat_basin[lat_basin['STAID'] == id]
        lat_in = lat_in_df['LAT_CENT'].iloc[0]

        #Calibrated parameters are same as historical

        #run hbv model
        q_sim = hbv(params_in, precip_in['PRECIP'], temp_in['tavg'], precip_in['DATE'], lat_in, routing=1)
        q_sim = np.round(q_sim, 3)

        #keep result in a dataframe
        output_df = pd.DataFrame({ 'date':precip_in['DATE'], 'streamflow':q_sim })
        #save output dataframe
        output_df.to_csv(f'/home/fs01/sp2596/MA-Precip-Uncertainty-Exp-equifinality2/output/future/rehbv/rehbv{id}_coverage{grid}_comb{combination}.csv')