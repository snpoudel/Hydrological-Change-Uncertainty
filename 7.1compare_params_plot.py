import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

basin_list = pd.read_csv('data/MA_basins_gauges_2000-2020_filtered.csv', dtype={'basin_id':str})
used_basin_list = ['01108000', '01109060', '01177000', '01104500']
basin_list = basin_list[basin_list['basin_id'].isin(used_basin_list)]
for id in basin_list['basin_id']:
    #read in hbv true parameters
    true_param = pd.read_csv('data/true_hbv_calibrated_parameters.csv', dtype={'station_id':str})
    true_param = true_param[true_param['station_id']==id]
    true_param['tag'] = 'HBV True'

    total_grid = basin_list[basin_list['basin_id'] == id]['num_stations'].values[0]
    grid = total_grid - 1
    #read hbv recalibrated parameters
    hbv_params = pd.DataFrame()
    for comb in np.arange(10):
        if os.path.exists(f'output/parameters/hbv_recalib/params{id}_grid{grid}_comb{comb}.csv'):
            file = pd.read_csv(f'output/parameters/hbv_recalib/params{id}_grid{grid}_comb{comb}.csv')
            hbv_params=pd.concat([hbv_params, file], ignore_index=True)
    hbv_params['tag'] = f'HBV Recalib with 90% gauge'
    vars=['fc','beta','pwp','l','ks','ki','kb','kperc','coeff_pet','ddf',
                                'scf','ts','tm','tti','whc','crf','maxbas']
    #merge
    df = pd.concat([hbv_params, true_param], ignore_index=True)

    # Set up the figure and axes
    fig, axs = plt.subplots(nrows=4, ncols=5, figsize=(7, 5))
    axs = axs.flatten()

    # Create a box plot for each variable
    for i, var in enumerate(vars):
        sns.swarmplot(data=df, y=var, ax=axs[i], hue='tag')
        axs[i].set_title(f'{var}')
        axs[i].set_xlabel('')
        axs[i].set_ylabel('')
        axs[i].get_legend().remove()


    # Turn off any unused subplots
    for j in range(len(vars), len(axs)):
        fig.delaxes(axs[j])

    # Adjust layout
    plt.tight_layout()
    plt.show()

    #save plot
    fig.savefig(f'output/figures/{id}/param_comparision.png', dpi=300)