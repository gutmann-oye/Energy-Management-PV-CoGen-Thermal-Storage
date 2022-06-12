# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:00:22 2021

@author: uoyebanj
"""

import pandas as pd

#file_path = "D:/Users/uoyebanj/Desktop/Irradiation Data Process/irr_data/" #====> Insert path
file_path = "D:/Users/uoyebanj/Desktop/Irradiation Data Process/Data for AI/" #====> Insert path

#df = pd.read_excel(file_path+"irradiation_data_summer_fullcell.xlsx", header=None) #====> Insert file name
df = pd.read_excel(file_path+"irradiation_data_day6.xlsx", header=None) #====> Insert file name

df1 = df.loc[0:19] #====> Insert row data to extract ['0:19','20:39','40:59','60:79','80:99','99:118']
df1 = df1.T

column_names = []
for i in range(1,len(df1.columns)+1):
    column_names.append("cell_irr"+str(i))
    
df1.columns = column_names
df1["min_irr"] = df1.min(axis=1)
df2 = df1["min_irr"]

file_name = "string_irr_1"  #====> Insert OUTPUT file name
file_path_out = "D:/Users/uoyebanj/Desktop/Irradiation Data Process/strings_irr_data/"
path = file_path_out+file_name+".csv"
df2.to_csv(path, sep = ",", index=False, encoding='utf-8')
#df2.to_excel(path, sep = ",", index=False, encoding='utf-8')



#%%
import pandas as pd
#df = pd.read_csv(r"D:\Users\uoyebanj\Desktop\Data Logging\data log\mp_data_ganimod.csv")
df = pd.read_csv(r"D:\Users\uoyebanj\Desktop\Data Logging\power_voltage_ganimod.csv")
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'fantasy'})

season = "AI/Day6"  ##>>>Insert season ['winter', 'spring', 'summer', 'autumn']
df1 = pd.read_csv("C:/Users/PHODIO/Desktop/thesis/my_safe/Ganimod Simulations/Ganimod/"+season+"/power_voltage_day6.csv")
df2 = pd.read_csv("C:/Users/PHODIO/Desktop/thesis/my_safe/Ganimod Simulations/Ganimod/"+season+"/mp_data_day6.csv")
df3 = pd.read_csv("C:/Users/PHODIO/Desktop/thesis/my_safe/Ganimod Simulations/Ganimod/"+season+"/power_voltage_AI_day6.csv")
#df3 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Blade/"+season+"/power_voltage_blade.csv")
#df4 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Standard/"+season+"/power_voltage_standard.csv")

df2["P_mp1"] = df2[" I_mp1"] * df2[" V_mp1"]
df2["P_mp2"] = df2[" I_mp2"] * df2[" V_mp2"]
df2["P_mp3"] = df2[" I_mp3"] * df2[" V_mp3"]
df2["P_mp4"] = df2[" I_mp4"] * df2[" V_mp4"]
df2["P_mp5"] = df2[" I_mp5"] * df2[" V_mp5"]
df2["P_mp6"] = df2[" I_mp6"] * df2[" V_mp6"]
df2["P_mp"] = df2["P_mp1"]+df2["P_mp2"]+df2["P_mp3"]+df2["P_mp4"]+df2["P_mp5"]+df2["P_mp6"]

df = pd.DataFrame()
df['Time'] = df1["Time"]
df['Total PV input MPP'] = df2["P_mp"]
df['Total output power (GaNimod P&O Algorithm)'] = df1[" P_out"]
df['Total output power (GaNimod ANN Algorithm)'] = df3[" P_out"]

total = df['Total PV input MPP'].sum(axis = 0, skipna = True)
print(total)
tracked_po = df['Total output power (GaNimod P&O Algorithm)'].sum(axis = 0, skipna = True)
print(f'tracked_po: {tracked_po}')
accuracy_po = tracked_po/total
print(f'accuracy_po: {accuracy_po}')

tracked_ann = df['Total output power (GaNimod ANN Algorithm)'].sum(axis = 0, skipna = True)
print(f'tracked_ann: {tracked_ann}')
accuracy_ann = (tracked_ann/total)
print(f'accuracy_ann: {accuracy_ann}')

#df['Total output power (Blade design)'] = df3[" P_out"]
#df['Total output power (Standard design)'] = df4[" P_out"]
#%%
#For the Team
import pandas as pd
import numpy as np
season = "autumn"  ##>>>Insert season
df1 = pd.read_csv("C:/Users/PHODIO/Desktop/thesis/my_safe/Ganimod Simulations/Ganimod/"+season+"/power_voltage_ganimod.csv")
df2 = pd.read_csv("C:/Users/PHODIO/Desktop/thesis/my_safe/Ganimod Simulations/Ganimod/"+season+"/mp_data_ganimod.csv")
#df3 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Blade/"+season+"/power_voltage_blade.csv")
df4 = pd.read_csv("C:/Users/PHODIO/Desktop/thesis/my_safe/Ganimod Simulations/Standard/"+season+"/power_voltage_standard.csv")

df2["P_mp1"] = df2[" I_mp1"] * df2[" V_mp1"]
df2["P_mp2"] = df2[" I_mp2"] * df2[" V_mp2"]
df2["P_mp3"] = df2[" I_mp3"] * df2[" V_mp3"]
df2["P_mp4"] = df2[" I_mp4"] * df2[" V_mp4"]
df2["P_mp5"] = df2[" I_mp5"] * df2[" V_mp5"]
df2["P_mp6"] = df2[" I_mp6"] * df2[" V_mp6"]
df2["P_mp"] = df2["P_mp1"]+df2["P_mp2"]+df2["P_mp3"]+df2["P_mp4"]+df2["P_mp5"]+df2["P_mp6"]

df = pd.DataFrame()
df['Time'] = df1["Time"]
df['Total PV input MPP'] = df2["P_mp"]
df['Total output power (GaNimod)'] = df1[" P_out"]
df['Total output power (Standard design)'] = df4[" P_out"]


total = df['Total PV input MPP'].sum(axis = 0, skipna = True)
print(total)

#%%
#df.to_excel("D:/Users/uoyebanj/Desktop/Ganimod Simulations/PLOTS/power_yield_comparison.xlsx", index=False, encoding='utf-8')

x = np.arange(0, len(df), 60)
df.plot(x="Time",
        y = ['Total PV input MPP', 'Total output power (GaNimod)', 'Total output power (Standard design)'],
        figsize = (25,10),
        title = "Power Yield Comparison (in W)",
        grid = True,
        fontsize = 13,
        xticks = x
        ).set_xlabel('Time (in mins)', fontsize=20)
#%%
#Test
#For the Team
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
season = "summer"  ##>>>Insert season
df1 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Ganimod/"+season+"/power_voltage_ganimod.csv")
df2 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Ganimod/"+season+"/mp_data_ganimod.csv")
#df3 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Blade/"+season+"/power_voltage_blade.csv")
df4 = pd.read_csv("D:/Users/uoyebanj/Desktop/Ganimod Simulations/Standard/"+season+"/power_voltage_standard.csv")

df2["P_mp1"] = df2[" I_mp1"] * df2[" V_mp1"]
df2["P_mp2"] = df2[" I_mp2"] * df2[" V_mp2"]
df2["P_mp3"] = df2[" I_mp3"] * df2[" V_mp3"]
df2["P_mp4"] = df2[" I_mp4"] * df2[" V_mp4"]
df2["P_mp5"] = df2[" I_mp5"] * df2[" V_mp5"]
df2["P_mp6"] = df2[" I_mp6"] * df2[" V_mp6"]
df2["P_mp"] = df2["P_mp1"]+df2["P_mp2"]+df2["P_mp3"]+df2["P_mp4"]+df2["P_mp5"]+df2["P_mp6"]

df = pd.DataFrame()
df['Time'] = df1["Time"]
df['Total PV input MPP'] = df2["P_mp"]
df['Total output power (GaNimod)'] = df1[" P_out"]
df['Total output power (Standard design)'] = df4[" P_out"]
x = df['Time']
y1 = df['Total PV input MPP']
y2 = df['Total output power (GaNimod)']
y3 = df['Total output power (Standard design)']

fig = plt.figure(figsize = (25,10))
ax1 = fig.add_subplot(111)
ax1.plot(x, y1, color = "r", linestyle= "-",linewidth = 2, label= "Total PV input MPP")
ax1.set_xlabel('Time (in mins)', fontsize=15)
ax1.set_ylabel('Total PV input MPP', fontsize=15)
ax1.set_xticks(np.arange(0, len(df)+20, 60))
ax1.set_xlim(0,len(df)+20)
ax1.legend(loc="best", fontsize =13)
ax1.grid()

ax2 = ax1.twinx()
ax2.plot(x, y2, color = "g", linestyle= "-",linewidth = 2, label= "Total output power (GaNimod)")
ax2.set_ylabel('Total output power (GaNimod)', fontsize=15)
ax2.legend(loc="best", fontsize =13)
