import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# id = '01109060'
used_basin_list = ['01108000', '01109060', '01177000', '01104500']
colors = sns.color_palette("tab10")[1:]  # Get the same palette for LOWESS lines
for id in used_basin_list:
    # Load the data
    flood = pd.read_csv(f'output/tyr_flood_{id}.csv')
    change_flood = pd.read_csv(f'output/change_tyr_flood_{id}.csv')

    ###---01 plot for t-yr flood---###
    ##--Historical flood--##
    flood_historical = flood[flood['model'].isin(['HBV True', 'HBV Recalib', 'Hymod', "LSTM"])]
    flood_historical = flood_historical.reset_index(drop=True)
    #first find true change in tyr floods
    df_temp_true = flood_historical[(flood_historical['model'] == 'HBV True') & (flood_historical['precip_rmse'] == 0)]
    true_5yr = float(df_temp_true.loc[0,'5yr_flood'])
    true_10yr = float(df_temp_true.loc[0,'10yr_flood'])
    true_20yr = float(df_temp_true.loc[0,'20yr_flood'])
    #remove hbv true from the dataframe
    flood_historical = flood_historical[~(flood_historical['model'] == 'HBV True')]

    fig, axs = plt.subplots(3,1,figsize=(7, 8), sharex=True)
    axs[0].axhline(y=true_5yr, linestyle='--',  alpha=1, label='Truth', linewidth=2)
    sns.scatterplot(data=flood_historical, x='precip_rmse', y='5yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[0])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(flood_historical['model'].unique()):
        subset = flood_historical[flood_historical['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['5yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[0].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5, color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[0].set_xlabel('Precipitation RMSE (mm/day)')
    axs[0].set_ylabel('5-year flood (mm/day)')
    axs[0].grid(True, linestyle ='--', alpha = 0.5)
    axs[0].get_legend().remove()
    axs[0].set_title('Flood return period with historical precip')

    axs[1].axhline(y=true_10yr, linestyle='--',  alpha=1, label='Truth', linewidth=2)
    sns.scatterplot(data=flood_historical, x='precip_rmse', y='10yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[1])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(flood_historical['model'].unique()):
        subset = flood_historical[flood_historical['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['10yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[1].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[1].set_xlabel('Precipitation RMSE (mm/day)')
    axs[1].set_ylabel('10-year flood (mm/day)')
    axs[1].grid(True, linestyle ='--', alpha = 0.5)
    axs[1].get_legend().remove()

    axs[2].axhline(y=true_20yr, linestyle='--',  alpha=1, label='Truth', linewidth=2)
    sns.scatterplot(data=flood_historical, x='precip_rmse', y='20yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[2])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(flood_historical['model'].unique()):
        subset = flood_historical[flood_historical['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['20yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[2].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[2].set_xlabel('Precipitation RMSE (mm/day)')
    axs[2].set_ylabel('20-year flood (mm/day)')
    axs[2].grid(True, linestyle ='--', alpha = 0.5)
    axs[2].legend(title='', loc='best')
    #save the plot
    plt.tight_layout()
    plt.savefig(f'output/figures/{id}/7tyr_flood_historical.png', dpi=300)
    #clear the plot
    plt.clf()


    ##--Future flood--##
    flood_future = flood[flood['model'].isin([ 'HBV True Future', 'HBV Recalib Future', 'Hymod Future', "LSTM Future"])]
    #first find true change in tyr floods
    df_temp_true = flood_future[(flood_future['model'] == 'HBV True Future') & (flood_future['precip_rmse'] == 0)].reset_index(drop=True)
    true_5yr = float(df_temp_true.loc[0,'5yr_flood'])
    true_10yr = float(df_temp_true.loc[0,'10yr_flood'])
    true_20yr = float(df_temp_true.loc[0,'20yr_flood'])
    #remove hbv true from the dataframe
    flood_future = flood_future[~(flood_future['model'] == 'HBV True Future')]

    fig, axs = plt.subplots(3,1, figsize=(7,8), sharex=True)
    axs[0].axhline(y=true_5yr, linestyle='--',  alpha=1, label='Truth', linewidth=2)
    sns.scatterplot(data=flood_future, x='precip_rmse', y='5yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax =axs[0])
    for i,variable in enumerate(flood_future['model'].unique()):
        subset = flood_future[flood_future['model'] == variable]
        lowess =sm.nonparametric.lowess(subset['5yr_flood'], subset['precip_rmse'], frac=0.5)
        axs[0].plot(lowess[:,0], lowess[:,1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[0].set_xlabel('Precipitation RMSE (mm/day)')
    axs[0].set_ylabel('5-year flood (mm/day)')
    axs[0].grid(True, linestyle ='--', alpha = 0.5)
    axs[0].get_legend().remove()
    axs[0].set_title('Flood return period with future precip')

    axs[1].axhline(y=true_10yr, linestyle='--',  alpha=1, label='Truth', linewidth=2)
    sns.scatterplot(data=flood_future, x='precip_rmse', y='10yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[1])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(flood_future['model'].unique()):
        subset = flood_future[flood_future['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['10yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[1].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[1].set_xlabel('Precipitation RMSE (mm/day)')
    axs[1].set_ylabel('10-year flood (mm/day)')
    axs[1].grid(True, linestyle ='--', alpha = 0.5)
    axs[1].get_legend().remove()

    axs[2].axhline(y=true_20yr, linestyle='--',  alpha=1, label='Truth', linewidth=2)
    sns.scatterplot(data=flood_future, x='precip_rmse', y='20yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[2])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(flood_future['model'].unique()):
        subset = flood_future[flood_future['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['20yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[2].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[2].set_xlabel('Precipitation RMSE (mm/day)')
    axs[2].set_ylabel('20-year flood (mm/day)')
    axs[2].grid(True, linestyle ='--', alpha = 0.5)
    axs[2].legend(title='', loc='best')
    #save the plot
    plt.tight_layout()
    plt.savefig(f'output/figures/{id}/8tyr_flood_future.png', dpi=300)
    #clear the plot
    plt.clf()


    ###---02 plot for change in t-yr flood---###
    #true change in flood
    #first find true change in tyr floods
    df_temp_true = change_flood[(change_flood['model'] == 'HBV True') & (change_flood['precip_rmse'] == 0)]
    true_5yr = float(df_temp_true.loc[0,'change_5yr_flood'])
    true_10yr = float(df_temp_true.loc[0,'change_10yr_flood'])
    true_20yr = float(df_temp_true.loc[0,'change_20yr_flood'])
    
    #filter out hbv true from change dataframe
    change_flood = change_flood[~(change_flood['model'] == 'HBV True')] #don't need to show result of truth across precip error!
    fig, axs = plt.subplots(3,1,figsize=(7, 8), sharex=True)
    axs[0].axhline(y=true_5yr, linestyle='--',  alpha=1, label='True Change', linewidth=2)
    sns.scatterplot(data=change_flood, x='precip_rmse', y='change_5yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[0])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(change_flood['model'].unique()):
        subset = change_flood[change_flood['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['change_5yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[0].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[0].set_xlabel('Precipitation RMSE (mm/day)')
    axs[0].set_ylabel('∆5-year flood (mm/day)')
    axs[0].grid(True, linestyle ='--', alpha = 0.5)
    axs[0].get_legend().remove()
    axs[0].set_title('Change in flood return period')

    axs[1].axhline(y=true_10yr, linestyle='--',  alpha=1, label='True Change', linewidth=2)
    sns.scatterplot(data=change_flood, x='precip_rmse', y='change_10yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[1])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(change_flood['model'].unique()):
        subset = change_flood[change_flood['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['change_10yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[1].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[1].set_xlabel('Precipitation RMSE (mm/day)')
    axs[1].set_ylabel('∆10-year flood (mm/day)')
    axs[1].grid(True, linestyle ='--', alpha = 0.5)
    axs[1].get_legend().remove()

    axs[2].axhline(y=true_20yr, linestyle='--', alpha=1, label='True Change', linewidth=2)
    sns.scatterplot(data=change_flood, x='precip_rmse', y='change_20yr_flood', hue='model', alpha=0.6,palette=sns.color_palette("tab10")[1:], ax=axs[2])
    # Compute and plot LOWESS lines
    for i,variable in enumerate(change_flood['model'].unique()):
        subset = change_flood[change_flood['model'] == variable]
        lowess = sm.nonparametric.lowess(subset['change_20yr_flood'], subset['precip_rmse'], frac=0.5)  # Adjust frac as needed
        axs[2].plot(lowess[:, 0], lowess[:, 1], label=None, linewidth=1.5,color=colors[i % len(colors)])  # Use colors[i] for each model
    axs[2].set_xlabel('Precipitation RMSE (mm/day)')
    axs[2].set_ylabel('∆20-year flood (mm/day)')
    axs[2].grid(True, linestyle ='--', alpha = 0.5)
    axs[2].legend(title='', loc='best')
    #save the plot
    plt.tight_layout()
    plt.savefig(f'output/figures/{id}/9change_tyr_flood.png', dpi=300)
    #clear the plot
    plt.clf()