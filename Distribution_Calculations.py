# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 16:48:53 2018

@author: jdbul
"""

"""



RUN THIS FILE AFTER TURN CALL_DATA_ANALYSIS.PY FIRST!  THE OBJECTS ARE NEEDED!




"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

#%%
"""
Get percentages for topics of departments
"""

topics.info()
# rename
topics.rename(columns={'KB_Article' : 'Dept'}, inplace=True)

# get total counts by dept using existing count col
department_dist_df = topics.groupby(['Dept'], as_index=False)['Count'].count()

# Get percentage of total for each dept

department_dist_df['Percentage'] = department_dist_df.Count.apply(lambda x: x/np.sum(department_dist_df['Count']))

# Sort and append average duration by dept

temp_dur = topics.groupby(['Dept'], as_index=False)['Seconds'].mean()
department_dist_df = pd.merge(department_dist_df, temp_dur, how='inner', on='Dept')

temp_std = topics.groupby(['Dept'], as_index=True)['Seconds'].std()

department_dist_df = pd.merge(department_dist_df, pd.DataFrame(temp_std), left_on='Dept', right_index=True, how='inner')
department_dist_df.set_index('Dept', inplace=True)
department_dist_df.drop(columns = ['Count'], inplace=True)
department_dist_df.rename(columns = {'Seconds_x' : 'MeanSeconds', 'Seconds_y':'StdDev'}, inplace=True)

#department_dist_df.to_csv('Data/Duration_distributions.csv')
#%%
"""
get std deviation and append

This can be done more simply above, this was to confirm wonky results
"""
sd_dict = {}
key_list = department_dist_df.Dept.unique()

for i in key_list:
    sd_dict[i] = []

for i in range(len(topics)):
    sd_dict[topics.Dept[i]].append(topics.Seconds[i])
    
dep_sd = {}

for i in key_list:
    dep_sd[i] = np.mean(sd_dict[i])


# this dataframe now has the data what percent of topics have what durations, we need to condense

#%%
"""
Get call arrival distribution based on data
Use daily data to extrapolate arrival rate, abadonment time avg(for customer patience) by day of the week
This can then be combined with topic duration data
"""

arrival_df = daily_data[['CallsPresented', 'Day_of_Week']]

day_dict = dict(zip([2,3,4,5,6],['Monday','Tuesday','Wednesday','Thursday','Friday']))

# drop an anomaly of low volume day, this was the first day of operation
arrival_df = arrival_df.drop(arrival_df.index[0])

#add column with categorical days
day_list = []
for i in range(len(arrival_df)):
    t = day_dict[arrival_df.Day_of_Week[i]]
    day_list.append(t)

arrival_df['Weekday'] = day_list
arrival_df.sort_values(['Day_of_Week'], ascending=True, inplace=True)
arrival_df.rename(columns = {'CallsPresented':'Daily Call Arrivals'}, inplace=True)
#%%
"""
box plot
"""
plt.figure()
sns.set_style('whitegrid')
_ = sns.boxplot(x='Weekday', y='Daily Call Arrivals', data=arrival_df)
_.set_title('Call Volume Distribution by Day of Week, 2013-2015')
sns.despine(left=True)


#%%
"""
Abandonment rate
"""

abandon_df = daily_data[['CallsPresented', 'Max_Abandon_Per_Day', 'Day_of_Week']]

#drop that pesky row here
abandon_df = abandon_df.drop(abandon_df.index[0])

#add column with categorical days using daydict from above
day_list = []
for i in range(len(abandon_df)):
    t = day_dict[abandon_df.Day_of_Week[i]]
    day_list.append(t)

abandon_df['Weekday'] = day_list
abandon_df.sort_values(['Day_of_Week'], ascending=True, inplace=True)
abandon_df.rename(columns = {'CallsPresented':'Daily Call Arrivals'}, inplace=True)
abandon_df['Percent of Calls Abandoned'] = (abandon_df['Max_Abandon_Per_Day']/abandon_df['Daily Call Arrivals'])*100

#%%
"""
boxplot
"""
plt.figure()
sns.set_style('whitegrid')
p = sns.boxplot(y='Percent of Calls Abandoned', x='Weekday', data=abandon_df)
p.set_title('Percent of Daily Calls Abandonment by Day of Week, 2013-2015')
sns.despine(left=True)
vals = p.get_yticks()
p.set_yticklabels(['{:.0%}'.format(x/100) for x in vals])

#%%
"""
Get means by day for arrivals and abandons and compare with newer data to see 
if levels are similar.
"""

summary_df = abandon_df

summary_df['Calls Answered'] = summary_df['Daily Call Arrivals'] - summary_df['Max_Abandon_Per_Day']

means_by_day = summary_df.groupby('Weekday', as_index=False).mean()
means_by_day.sort_values(['Day_of_Week'], ascending=True, inplace=True)

#%%
"""
Bring in new data (article data, parse by date to get day of week)
"""


new_daily = article_data
new_daily['Date'] = article_data['Created On']
new_daily['Date'] = pd.to_datetime(new_daily['Date'], format='%m/%d/%Y %H:%M')
new_daily['Date2'] = new_daily['Date'].apply(lambda x: datetime.datetime.date(x))
new_daily['Day_of_Week'] = new_daily['Date'].apply(lambda x: datetime.datetime.weekday(x)+2)
new_daily['CountNew'] = 1

#%%
"""
Group new data by mean calls handled by day of week
"""

new_daily_count = new_daily.groupby(['Date2'], as_index=False)['CountNew'].count()
new_daily_day = new_daily.groupby(['Date2'], as_index=False)['Day_of_Week'].mean()

new_daily = new_daily_day.merge(new_daily_count, how='inner', on='Date2')

day_list = []
for i in range(len(new_daily)):
    t = day_dict[new_daily.Day_of_Week[i]]
    day_list.append(t)

new_daily['Weekday'] = day_list

new_daily_summary = new_daily.groupby(['Weekday'], as_index=False).mean()

new_daily_summary.sort_values(['Day_of_Week'], ascending=True, inplace=True)
new_daily_summary = new_daily_summary.drop(columns = ['Day_of_Week'])

#%%
"""
Compare these calls handled to old calls handled, to see if scaling up is necessary
Assuming abandoned percentages hold true
"""

means_by_day.info()
new_daily_summary.info()

call_amount_combined = means_by_day.merge(new_daily_summary, how='inner', on='Weekday')

call_amount_combined['Ratio_OldoverNew'] = call_amount_combined['Calls Answered']/call_amount_combined['CountNew']

call_amount_combined['Arrivals'] = call_amount_combined['CountNew']/(1-(call_amount_combined['Percent of Calls Abandoned']/100))


#this is daily totals for simulation
calls_by_day_for_simulation = call_amount_combined[['Weekday', 'Arrivals', 'Percent of Calls Abandoned']]
#calls_by_day_for_simulation.to_csv("Data/calls_by_day_for_simulation.csv")
#%%
"""
Try to get an hourly breakdown of calls by weekday.  This will be looked at as
a percentage so that it can scale correctly
"""


daily_hour = article_data
daily_hour['Date'] = article_data['Created On']
daily_hour['Date'] = pd.to_datetime(daily_hour['Date'], format='%m/%d/%Y %H:%M')
daily_hour['Count'] = 1
daily_hour['Hour of the Day'] = daily_hour['Date'].dt.hour
daily_hour['Date2'] = daily_hour['Date'].apply(lambda x: datetime.datetime.date(x))
daily_hour = daily_hour.groupby(['Date2', 'Hour of the Day'], as_index=False)['Count'].count()
daily_hour['Day_of_Week'] = daily_hour['Date2'].apply(lambda x: datetime.datetime.weekday(x)+2)


day_list = []
for i in range(len(daily_hour)):
    t = day_dict[daily_hour.Day_of_Week[i]]
    day_list.append(t)

daily_hour['Weekday'] = day_list

daily_hourly_summary_calls = daily_hour.groupby(['Weekday', "Hour of the Day"], as_index=False)['Day_of_Week','Count'].mean()
daily_hourly_summary_calls.sort_values(['Day_of_Week', 'Hour of the Day'], ascending=True, inplace=True)

#%%
"""
Combine hourly calls handled to total est. calls to get percentage for total hourly arrivals
"""

totals_by_day_hourly = daily_hourly_summary_calls.groupby('Weekday', as_index=True)['Count'].sum()

daily_hourly_summary_calls['Proportion'] = 0
for i in range(len(daily_hourly_summary_calls)):
    daily_hourly_summary_calls['Proportion'].iloc[i] = daily_hourly_summary_calls['Count'].iloc[i] / totals_by_day_hourly.loc[daily_hourly_summary_calls.Weekday.iloc[i]]

final_hourly_dist = daily_hourly_summary_calls
#%%
    
total_dict = {}

for i in range(len(calls_by_day_for_simulation)):
    total_dict[calls_by_day_for_simulation['Weekday'][i]] = calls_by_day_for_simulation['Arrivals'][i]

final_hourly_dist['Arrivals'] = np.nan
for i in range(len(final_hourly_dist)):
    final_hourly_dist['Arrivals'].iloc[i] = final_hourly_dist['Proportion'].loc[i] * total_dict[final_hourly_dist['Weekday'].iloc[i]]

hourly_arrival_dist_for_simulation = final_hourly_dist.drop(columns=['Day_of_Week', 'Count', 'Proportion'])

hourly_arrival_dist_for_simulation.set_index(['Weekday', 'Hour of the Day'], inplace=True)

#hourly_arrival_dist_for_simulation.to_csv('Data/hourly_arrival_dist_for_simulation.csv')





#%%
