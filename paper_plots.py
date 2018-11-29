# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 20:56:47 2018

@author: jdbul
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
#%%

data = pd.read_csv("Data/self_serve_results.csv")

print(data)

data.info()

data['Percent_who_use']= data['Percent_who_use']/100


#%%


fig, ax1 = plt.subplots()

color = 'purple'
ax1.set_xlabel('Percent of Self-Serve Utilization')
ax1.set_ylabel('Average Queue Waiting Time (hours)', color=color)
ln1 = ax1.plot(data['Percent_who_use'], data['Avg_Wait'], color=color, marker = '+', label='Average Wait for an Operator')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'green'
ax2.set_ylabel('Average Queue Length (Number of Callers)', color=color)  # we already handled the x-label with ax1
ln2 = ax2.plot(data['Percent_who_use'], data['Avg_Queue'], color=color, marker = '.', ls='--', label='Average Queue Length')
ax2.tick_params(axis='y', labelcolor=color)
plt.title("Operator Waiting Queue Statistics as a \n Function of Self-Service Adoption Rates")

ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))

fig.tight_layout()
lns = ln1+ln2
labs = [l.get_label() for l in lns]
plt.legend(lns, labs, loc=0)

ax1.legend(loc='upper right')
plt.show()

#%%

fig, ax = plt.subplots()

ax.set_xlabel('Percent of Self-Serve Utilization')
ax.set_ylabel('Average Operator Utilization')

plt.plot(data['Percent_who_use'], data['Agent_Util'], marker='x')
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))
plt.title('Operator Utilization in Response to \n Self-Service Adoption Rates')
plt.tight_layout()


#%%
"""
Num operator plots
"""

datafile= "Data/num_operator_results.csv"

df = pd.read_csv(datafile)

df.info()

#%%

fig, ax1 = plt.subplots()

barWidth = 0.25
r1 = [x + .125 for x in np.arange(4)]
r2 = [x + .375 for x in np.arange(4)]

color = 'red'
ax1.set_xlabel('Number of Operators')
ax1.set_ylabel('Average Number of Daily Hang-Ups', color=color)
ln1 = ax1.bar(r1, df['Number of Hang_Ups'], width = 0.25, color=color,hatch = '/', label='Average Calls Abandoned')
#ln2 = ax1.bar(r2, df['Agent_Util'], color="green", width = 0.25, label='Average Operator Utilization')

ax1.tick_params(axis='y', labelcolor=color)
plt.xticks([r + barWidth for r in range(4)], ['One Less', 'Base', 'Plus 1', 'Plus 2'])


ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'blue'
ax2.set_ylabel('Operator Utilization Percentage')  # we already handled the x-label with ax1
ax2.tick_params(axis='y')
plt.title("Average Daily Number of Caller Hang-Ups and Average \n Operator Utilization")
ln2 = ax2.bar(r2, df['Agent_Util'] , width = 0.25, label='Average Operator Utilization')

ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))

fig.tight_layout()

plt.legend([ln1, ln2], ['Average Calls Abandoned', 'Average Operator Utilization'])
#ax1.legend(loc='upper right')
#ax2.legend(loc='upper right')
plt.show()

