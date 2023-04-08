# -*- coding: utf-8 -*-

###Import Libraries
import pulp
import pandas as pd

###Loading profile of the Local Energy System
data = pd.read_excel("DHW_HTG_Pel_Psol_exp_update.xlsx")

###Creating Date dataframe
date = data["YYYY-MM-DD"]

###Creating Time of Day dataframe
time_of_day = data["HH:MM:SS"]

###Creating Electric Load dataframe
EL_load = 0.25*data["P_el[W]"]                              #convert from W to Wh
EL_load = EL_load.to_frame().to_dict('index')
inplace=True
###Creating Thermal Load dataframe
HL_load = 0.25*data["P_Htg[W]"]
HL_load = HL_load.to_frame().to_dict('index')

###Creating Warmwater Load dataframe
WWL_load = 0.25*data["P_WW[W]"]
WWL_load = WWL_load.to_frame().to_dict('index')


###Dimensioning of PV Installation
PV_per_sqm=data["P_sol[W]"]

pv_cap = 20000                #installed photovoltaic capacity in Watts
max_pv_per_sqm = PV_per_sqm.max()      #from Watts/sqm from the profile data
installation_area = pv_cap/max_pv_per_sqm

###Creating PV generation dataframe
PV_generation = 0.25 * PV_per_sqm * installation_area   #from W to Wh
PV_generation = PV_generation.to_frame().to_dict('index')


#------------Creating System Parameters---------------------------------------

#EFFICIENCIES
eff_storage=0.98    #efficiency of storage (2% loss every 1 hour)
eff_boiler=0.90     #Efficiency of boiler
eff_chp_el=0.35     #Efficiency of CHP for electrical generation
eff_chp_th=0.55     #Efficiency of CHP for thermal generation

#MAXIMUM OUTPUT
H_chp_max=94300     #Maximum heat output from the CHP in Watts
E_chp_max=60000     #Maximum electrical output from the CHP in Watts
H_boiler_max=200000 #Maximum heat output from Boiler in Watts

#MINIMUM OUTPUT
E_chp_min=30000     #Minimum electrical output from the CHP in Watts
H_chp_min=47100     #Minimum heat output from the CHP in Watts
H_boiler_min=20000  #Minimum heat output from Boiler in Watts

#MAXIMUM STORAGE
H_st_max=200000     #Maximum Heat Storage Capacity in Watts

#COSTS/KWH
E_cost=0.25/1000    #Electricty price in Euro/Wh
G_cost=0.0687/1000  #Gas price in Euro/Wh
fit=0.10/1000       #Feedin Tariff in Euro/Wh



#------------Declaring Problem Variables-------------------------------------

#Electricity consumed from the Grid
El_grid = pulp.LpVariable.dicts("Grid_Electricity", [k for k in data.index], lowBound=0, cat='Continuous')

#Part of PV generation being fed to the Grid
PV_feed = pulp.LpVariable.dicts("PV_feed-in", [ k for k in data.index], lowBound=0, cat='Continuous')

#Part of PV generation being self consumed by the system
PV_self = pulp.LpVariable.dicts("PV_self", [ k for k in data.index], lowBound=0, cat='Continuous')

#Gas consumed by the CHP
G_chp = pulp.LpVariable.dicts("Gas_Consumption_CHP", [ k for k in data.index], lowBound=0, upBound=171454, cat='Continuous')    #min and max system values

#Gas consumed by the auxiliary boiler
G_boiler = pulp.LpVariable.dicts("Gas_Consumption_auxiliary_boiler", [ k for k in data.index], lowBound= 0, upBound= 204082, cat='Continuous')  # min and max system values

#Electricity produced by chp for self-consumption
E_chp = pulp.LpVariable.dicts("Electricity_Production", [ k for k in data.index], lowBound= E_chp_min, upBound= E_chp_max, cat='Continuous')

#Electricity produced by chp for self-consumption
E_chp_self = pulp.LpVariable.dicts("Electricity_Production_self", [ k for k in data.index], lowBound= 0, upBound= E_chp_max, cat='Continuous')

#Electricity produced by chp for feed-in
E_chp_feed = pulp.LpVariable.dicts("Electricity_Production_feed", [ k for k in data.index], lowBound= 0, upBound= E_chp_max, cat='Continuous')

#Heat produced
H_chp = pulp.LpVariable.dicts("Heat_Production", [ k for k in data.index], lowBound= H_chp_min, upBound= H_chp_max, cat='Continuous')     

#Heat produced by Boiler
H_boiler = pulp.LpVariable.dicts("Heat_Boiler_Production", [ k for k in data.index], lowBound= H_boiler_min, upBound= H_boiler_max, cat='Continuous')   



#-------------creating the model-----------------------------------------
#State of charge of the thermal storage
SOC = pulp.LpVariable.dicts("State_of_Charge", [ k for k in data.index], lowBound=0, upBound= 200000, cat='Continuous')        

###Creating the  model to contain the problem data
model = pulp.LpProblem("Operation_Cost_Minimization_Problem", pulp.LpMinimize)



###Calculating the use of thermal storage

for k in data.index:
    #Electricity produced by the CHP
    model += E_chp_self[k] + E_chp_feed[k] == G_chp[k] * eff_chp_el

    #Heat Produced by the CHP
    model += H_chp[k] == G_chp[k] * eff_chp_th

    #Heat Produced by the boiler
    model += H_boiler[k] == G_boiler[k] * eff_boiler





#Adding Constraints to the model
for k in data.index:

    #Electricity supply-demand balance
    model += El_grid[k] + E_chp_self[k] + PV_self[k] == EL_load[k] + PV_feed[k] + E_chp_feed[k]
    #PV generation and distribution equation
    model += PV_self[k] + PV_feed[k] == PV_generation[k]
    #model += PV_self[k] <= EL_load[k]

    #Electricity produced by CHP is sum of feed-in and self-consumption
    model += E_chp[k] == E_chp_feed[k] + E_chp_self[k]

    #Gas consumed by chp is either 0 or greater than 85714         
    model += 0 == G_chp[k] or G_chp[k] >= 85714

    #Gas consumed by boiler is either 0 or greater than 22222
    model += 0 == G_boiler[k] or G_boiler[k] >= 22222



#-----------Calculating the use of thermal energy----------------------
#Heat supply-demand balance/Storage Dynamics

for k in data.index:
   if k==data.index[0]:
             SOC[0]==0
             model += SOC[k] == H_chp[k] - HL_load[k] + H_boiler[k] - WWL_load[k]    #["th_load_house[kW]"]- Added leftover boiler heat[brenden]
   else:

           if (H_st_max- SOC[k]) <= (eff_storage * H_st_max) and (H_chp[k] - HL_load[k] + H_boiler[k] - WWL_load[k]) <= (H_st_max - SOC[k-1]):   #If the maximum capacity was not reached we can store heat load
               model += SOC[k] == eff_storage * SOC[k-1] + H_chp[k] + H_boiler[k] - HL_load[k]  - WWL_load[k]     #["th_load_house[kW]"]
           else: # If the maximum capacity was reached, we need to use it to supply heat
               model += SOC[k+1] == SOC[k]- HL_load[k] - WWL_load[k]
    



#------------CALCULATING THE TOTAL COSTS OF THE MODEL------------------
#Adding objective function to the model

model += pulp.lpSum([(E_cost * El_grid[k]) - (fit * (PV_feed[k] + E_chp_feed[k]) + G_cost * (G_chp[k] + G_boiler[k])) for k in data.index])



#--------------Creating a file with the results-----------------------

#The problem data is written to an .lp file
model.writeLP('Operation_Cost_Minimization_Problem.lp')

###The problem is solved using PuLP's choice of Solver
model.solve()
pulp.LpStatus[model.status]


###Print objective function value (Total Minimized Costs for the whole year)
print("The Total Minimized Cost (Euros) for the entire year is: ")
print (pulp.value(model.objective))



#Creating Results
output = []
for k in data.index:
    var_output = {
        'Time': k,
        'Date': date[k],
        'Time of day': time_of_day[k],
        'El_grid': El_grid[k].varValue,
        'G_boiler': G_boiler[k].varValue,
        'G_chp': G_chp[k].varValue,
        'E_chp_self': E_chp_self[k].varValue,
        'E_chp_feed': E_chp_feed[k].varValue,
        'PV_generation': PV_generation[k],
        'PV_self': PV_self[k].varValue,
        'PV_feed': PV_feed[k].varValue,
        'SOC': SOC[k].varValue,

        'Minimised_cost': (E_cost * El_grid[k].varValue + G_cost * (G_chp[k].varValue + G_boiler[k].varValue) - fit * (PV_feed[k].varValue + E_chp_feed[k].varValue))

    }
    output.append(var_output)
output_df = pd.DataFrame.from_records(output).sort_values(['Time'])
output_df.set_index(['Time'], inplace=True)
output_df


### Writing Files out
file_name = "Operation_Cost_Minimization_Problem.csv"
output_df.to_csv(file_name, sep=',', encoding='utf-8')
