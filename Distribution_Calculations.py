# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 16:48:53 2018

@author: jdbul
"""

import pandas as pd
import numpy as np

#%%
"""
Get percentages for distributions of departments
"""

topics.info()
# rename
topics.rename(columns={'KB_Article' : 'Dept'}, inplace=True)

# get total counts by dept using existing count col
department_dist_df = topics.groupby(['Dept'], as_index=False)['Count'].count()

# Get percentage of total for each dept

department_dist_df['Percentage'] = department_dist_df.Count.apply(lambda x: round(x/np.sum(department_dist_df['Count'])*100,2))

# Sort and append average duration by dept

temp_dur = topics.groupby(['Dept'], as_index=False)['Seconds'].mean()
department_dist_df = pd.merge(department_dist_df, temp_dur, how='inner', on='Dept')

# this dataframe now has the data what percent of topics have what durations, we need to condense

#%%
"""
Get call arrival distribution based on data
"""