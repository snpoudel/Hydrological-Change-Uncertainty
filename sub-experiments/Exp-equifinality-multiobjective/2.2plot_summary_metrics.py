#import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
#set colorblind friendly colors from seaborn
sns.set_palette('colorblind')

#read input
df = pd.read_csv('output/allbasins_diagnostics_validperiod.csv')
df_zeroprecip = df[df['RMSE(PRECIP)'] == 0] #filter precip zero
df_zeroprecip['precip_cat'] = '0'

df = df[df['RMSE(PRECIP)'] != 0] #filter everything except precip zero
#convert precipitation error into categorical group
df['precip_cat']  = pd.cut(df['RMSE(PRECIP)'], bins=[0,1,2,3,4,6,8],
                           labels=['0-1', '1-2', '2-3', '3-4', '4-6', '6-8'])

#merge back zero precips
df = pd.concat([df,df_zeroprecip], ignore_index=True)
df = df.dropna(axis='rows')


#boxplot for no error
df_bias_melt = pd.melt(df, id_vars=['precip_cat'], value_vars=[ 'BIAS(RECAL_HBV)',  'BIAS(FULL-HYMOD)','BIAS(HYMOD)'])
df_bias_melt['objective'] = 'BIAS'

df_hfb_melt = pd.melt(df, id_vars=['precip_cat'], value_vars= ['HFB(RECAL_HBV)', 'HFB(FULL-HYMOD)', 'HFB(HYMOD)'])
df_hfb_melt['objective'] = 'HFB'

df_rmse_melt = pd.melt(df, id_vars=['precip_cat'], value_vars=['RMSE(RECAL_HBV)', 'RMSE(FULL-HYMOD)', 'RMSE(HYMOD)'])
df_rmse_melt['objective'] = 'RMSE'

df_nse_melt = pd.melt(df, id_vars=['precip_cat'], value_vars=['NSE(RECAL_HBV)', 'NSE(FULL-HYMOD)', 'NSE(HYMOD)'])
df_nse_melt['objective'] = 'NSE'

df_kge_melt = pd.melt(df, id_vars=['precip_cat'], value_vars=['KGE(RECAL_HBV)', 'KGE(FULL-HYMOD)', 'KGE(HYMOD)'])
df_kge_melt['objective'] = 'KGE'
#combine all dataframes
df_all = pd.concat([df_bias_melt, df_hfb_melt, df_rmse_melt, df_nse_melt, df_kge_melt], axis=0)
df_all['model'] = df_all['variable'].apply(lambda x: x.split('(')[1].split(')')[0])

#set order of model categories
model_order = ['RECAL_HBV', 'FULL-HYMOD', 'HYMOD']
df_all['model'] = pd.Categorical(df_all['model'], categories=model_order, ordered=True)

#make plot for nse, kge, rmse
df_all_nkr = df_all[df_all['objective'].isin(['RMSE','KGE','NSE'])]
#Make boxplots using seaborn
precip_cat_order = ['0', '0-1', '1-2', '2-3', '3-4', '4-6', '6-8']
seaplot = sns.catplot(
            data=df_all_nkr, order = precip_cat_order,
            x='precip_cat', y='value', row='objective',
            hue='model', kind='box', showfliers = False, width =0.8,
            sharey=False,  legend_out=True,
            height = 2.5, aspect = 2.5, #aspect times height gives width of each facet
            ) 
seaplot.set_axis_labels('Precipitation Uncertainty (RMSE, mm/day)', "") #set x and y labels
seaplot.legend.set_title("Model") #set legend title
seaplot.set_titles("") #remove default titles
plt.suptitle('Summary performance during validation period for all basins')
for index, ax in enumerate(seaplot.axes.flat): #seaplot.axes.flat is a list of all axes in facetgrid/catplot
    ax.set_ylabel(['RMSE(mm/day)', 'NSE', 'KGE'][index])
    ax.grid(True, linestyle ='--', alpha = 0.5)
# plt.tight_layout()
plt.show()
#save the plot
# seaplot.savefig('output/figures/NSE_allbasin.png', dpi=300)
#also save as a pdf
# seaplot.savefig('output/figures/diagnosticsNSE_allbasin.pdf')
# seaplot.savefig('output/figures/NoLSTM_diagnosticsKGE_allbasin.png', dpi=300) #without lstm


#make plot for nse, kge, rmse
df_all_bias = df_all[df_all['objective'].isin(['BIAS','HFB'])]
#Make boxplots using seaborn
precip_cat_order = ['0', '0-1', '1-2', '2-3', '3-4', '4-6', '6-8']
seaplot = sns.catplot(
            data=df_all_bias, order = precip_cat_order,
            x='precip_cat', y='value', row='objective',
            hue='model', kind='box', showfliers = False, width =0.7,
            sharey=False,  legend_out=True,
            height = 3, aspect = 3, #aspect times height gives width of each facet
            ) 
seaplot.set_axis_labels('Precipitation Uncertainty (RMSE, mm/day)', "") #set x and y labels
seaplot.legend.set_title("Model") #set legend title
seaplot.set_titles("") #remove default titles
plt.suptitle('Summary performance during validation period for all basins')
for index, ax in enumerate(seaplot.axes.flat): #seaplot.axes.flat is a list of all axes in facetgrid/catplot
    ax.set_ylabel(['Bias(%)', '>99.9th Flow Bias(%)'][index])
    ax.grid(True, linestyle ='--', alpha = 0.5)
# plt.tight_layout()
plt.show()

#save the plot
# seaplot.savefig('output/figures/NoLSTM_diagnosticsBIAS_allbasin.png', dpi=300) #without lstm
# seaplot.savefig('output/figures/BIAS_allbasin.png', dpi=300)


#######################################################################################################################################################################################################
#only save result for nse plot
#make plot for nse, kge, rmse
df_all_nkr = df_all[df_all['objective'].isin(['NSE'])]
#Make boxplots using seaborn
precip_cat_order = ['0', '0-1', '1-2', '2-3', '3-4', '4-6', '6-8']
seaplot = sns.catplot(
            data=df_all_nkr, order = precip_cat_order,
            x='precip_cat', y='value', row='objective',
            hue='model', kind='box', showfliers = False, width =0.8,
            sharey=False,  legend_out=False,
            height = 4, aspect = 2, #aspect times height gives width of each facet
            ) 
seaplot.set_axis_labels('Precipitation Uncertainty (RMSE, mm/day)', "") #set x and y labels
seaplot.legend.set_title("Model") #set legend title
seaplot.set_titles("") #remove default titles
plt.ylabel('Nash-Sutcliffe Efficiency')
plt.grid(True, linestyle ='--', alpha = 0.5)
plt.ylim(0, None)
plt.tight_layout()
plt.show()
#save the plot
seaplot.savefig('output/figures/OnlyNSE_allbasin_LowHighAllflow.png', dpi=300)