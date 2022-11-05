# coding: utf-8
from pyomo.environ import *
from pyomo.environ import value
import numpy as np

model = AbstractModel()

######=================================================########
######               Segment B.1                       ########
######=================================================########

### Producers by fuel-type
model.NA = Set()

# network data
model.lines = Set() 
model.nodes = Set()

# qps parameters
model.Qstep1 = Param(model.NA,within=Any)
model.Qstep2 = Param(model.NA,within=Any)
model.Qstep3 = Param(model.NA,within=Any)
model.Qstep4 = Param(model.NA,within=Any)
model.Qstep5 = Param(model.NA,within=Any)
model.Qstep6 = Param(model.NA,within=Any)

model.Pstep1 = Param(model.NA,within=Any)
model.Pstep2 = Param(model.NA,within=Any)
model.Pstep3 = Param(model.NA,within=Any)
model.Pstep4 = Param(model.NA,within=Any)
model.Pstep5 = Param(model.NA,within=Any)
model.Pstep6 = Param(model.NA,within=Any)
model.node = Param(model.NA,within=Any)

#pipeline parameters
model.FlowLim = Param(model.lines)
model.QPS_to_node=Param(model.NA,model.nodes)
model.line_to_node=Param(model.lines,model.nodes)

model.FTariff_1=Param(model.lines)
model.FTariff_2=Param(model.lines)
model.FTariff_3=Param(model.lines)
model.FTariff_4=Param(model.lines)
model.FTariff_5=Param(model.lines)

model.FTariff_1_CAP=Param(model.lines)
model.FTariff_2_CAP=Param(model.lines)
model.FTariff_3_CAP=Param(model.lines)
model.FTariff_4_CAP=Param(model.lines)
model.FTariff_5_CAP=Param(model.lines)

# ######=================================================########
# ######               Segment B.5                       ########
# ######=================================================########

######===== Parameters/initial_conditions to run simulation ======####### 
## Full range of time series information
model.SimDays = Param(within=PositiveIntegers)
model.SD_periods = RangeSet(1,model.SimDays+1)

# Operating horizon information 
model.HorizonDays = Param(within=PositiveIntegers)
model.HD_periods = RangeSet(1,model.HorizonDays)

# ######=================================================########
# ######               Segment B.6                       ########
# ######=================================================########

#Demand over simulation period
model.SimDemand = Param(model.nodes*model.SD_periods, within=NonNegativeReals)

#Horizon demand
model.HorizonDemand = Param(model.nodes*model.HD_periods,within=NonNegativeReals,mutable=True)


######=======================Decision variables======================########
##Natural gas productoin
model.step1_prod = Var(model.NA,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step2_prod = Var(model.NA,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step3_prod = Var(model.NA,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step4_prod = Var(model.NA,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step5_prod = Var(model.NA,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step6_prod = Var(model.NA,model.HD_periods, within=NonNegativeReals,initialize=0)

# pipeline variables 
model.step1_flow = Var(model.lines,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step2_flow = Var(model.lines,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step3_flow = Var(model.lines,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step4_flow = Var(model.lines,model.HD_periods, within=NonNegativeReals,initialize=0)
model.step5_flow = Var(model.lines,model.HD_periods, within=NonNegativeReals,initialize=0)


######=================================================########
######               Segment B.8                       ########
######=================================================########

######================Objective function=============########

def SysCost(model):
    
    production = sum(model.step1_prod[j,i]*model.Pstep1[j] + model.step2_prod[j,i]*model.Pstep2[j] + model.step3_prod[j,i]*model.Pstep3[j] + model.step4_prod[j,i]*model.Pstep4[j] for i in model.HD_periods for j in model.NA)  
    pipelines = sum(model.step1_flow[l,i]*model.FTariff_1[l] + model.step2_flow[l,i]*model.FTariff_2[l] + model.step3_flow[l,i]*model.FTariff_3[l] + model.step4_flow[l,i]*model.FTariff_4[l] + model.step5_flow[l,i]*model.FTariff_5[l] for l in model.lines for i in model.HD_periods)

    return production + pipelines
    
model.SystemCost = Objective(rule=SysCost, sense=minimize)


######=================================================########
######               Segment B.9                      ########
######=================================================########


# Constraints for Max Capacity of QPS and pipelines
def MaxQP1(model,j,i):
    return model.step1_prod[j,i]  <= model.Qstep1[j] 
model.MaxCapQP1= Constraint(model.NA,model.HD_periods,rule=MaxQP1)

def MaxQP2(model,j,i):
    return model.step2_prod[j,i]  <= (model.Qstep2[j] - model.Qstep1[j])
model.MaxCapQP2= Constraint(model.NA,model.HD_periods,rule=MaxQP2)

def MaxQP3(model,j,i):
    return model.step3_prod[j,i]  <= (model.Qstep3[j] - model.Qstep2[j])
model.MaxCapQP3= Constraint(model.NA,model.HD_periods,rule=MaxQP3)

def MaxQP4(model,j,i):
    return model.step4_prod[j,i]  <= (model.Qstep4[j] - model.Qstep3[j])
model.MaxCapQP4= Constraint(model.NA,model.HD_periods,rule=MaxQP4)

def MaxQP5(model,j,i):
    return model.step5_prod[j,i]  <= (model.Qstep5[j] - model.Qstep4[j])
model.MaxCapQP5= Constraint(model.NA,model.HD_periods,rule=MaxQP5)

def MaxPIPE1(model,j,i):
    return model.step1_flow[j,i]  <= model.FTariff_1_CAP[j] 
model.MaxCapFlow1= Constraint(model.lines,model.HD_periods,rule=MaxPIPE1)

def MaxPIPE2(model,j,i):
    return model.step2_flow[j,i]  <= (model.FTariff_2_CAP[j] - model.FTariff_1_CAP[j])
model.MaxCapFlow2= Constraint(model.lines,model.HD_periods,rule=MaxPIPE2)

def MaxPIPE3(model,j,i):
    return model.step3_flow[j,i]  <= (model.FTariff_3_CAP[j] - model.FTariff_2_CAP[j])
model.MaxCapFlow3= Constraint(model.lines,model.HD_periods,rule=MaxPIPE3)

def MaxPIPE4(model,j,i):
    return model.step4_flow[j,i]  <= (model.FTariff_4_CAP[j] - model.FTariff_3_CAP[j])
model.MaxCapFlow4= Constraint(model.lines,model.HD_periods,rule=MaxPIPE4)


def Nodal_Balance(model,z,i):
    flow = sum((model.step1_flow[l,i] + model.step2_flow[l,i] + model.step3_flow[l,i] + model.step4_flow[l,i] + model.step5_flow[l,i])*model.line_to_node[l,z] for l in model.lines)   
    gen = sum(model.step1_prod[j,i]*model.QPS_to_node[j,z] + model.step2_prod[j,i]*model.QPS_to_node[j,z] + model.step3_prod[j,i]*model.QPS_to_node[j,z] + model.step4_prod[j,i]*model.QPS_to_node[j,z] + model.step5_prod[j,i]*model.QPS_to_node[j,z] + model.step6_prod[j,i]*model.QPS_to_node[j,z] for j in model.NA)    
    return gen + flow == model.HorizonDemand[z,i] 
model.Node_Constraint = Constraint(model.nodes,model.HD_periods,rule=Nodal_Balance)

def Flow_line(model,l,i):
    return  model.step1_flow[l,i] + model.step2_flow[l,i] + model.step3_flow[l,i] + model.step4_flow[l,i] + model.step5_flow[l,i] <= model.FlowLim[l]
model.Flow_Constraint = Constraint(model.lines,model.HD_periods,rule=Flow_line)

