
import csv
import pandas as pd
import numpy as np
import re


######=================================================########
######               Segment A.1                       ########
######=================================================########

SimDays = 365
HorizonDays = 7  ##planning horizon 


data_name = 'NGMM_data'


######=================================================########
######               Segment A.2                       ########
######=================================================########

#read parameters for QP supply regions
df_QP_NA = pd.read_csv('QP_BASE_NA.csv',header=0)
qps = list(df_QP_NA['producer'])
for q in qps:
    new_q = q + '_qps'
    i = qps.index(q)
    qps[i] = new_q
df_QP_NA['producer'] = qps

#read pipeline data
df_line_params = pd.read_csv('PipeCapacities_Dec22.csv',header=0,index_col=0)
i_nodes = list(df_line_params.index)
c_nodes = list(df_line_params.columns)
nodes = i_nodes + c_nodes
all_nodes = [i for n, i in enumerate(nodes) if i not in nodes[:n]]
 
lines = []
caps = []
tos = []
froms = []

for i in all_nodes:
    for j in all_nodes:
        if i != j:
            line = i+'_to_'+j
            if df_line_params.loc[i,j]>0:
                froms.append(i)
                tos.append(j)
                lines.append(line)
                caps.append(df_line_params.loc[i,j])
                
for l in lines:
    new_l = l.replace('-','_')
    i = lines.index(l)
    lines[i] = new_l

df_pipelines = pd.DataFrame(caps,index = lines,columns = ['capacity']) 



# create line to node matrix

A = np.zeros((len(lines),len(all_nodes)))

df_A = pd.DataFrame(A)
df_A.columns = all_nodes
df_A['line'] = lines
df_A.set_index('line',inplace=True)

for i in range(0,len(lines)):
    f = froms[i]
    t = tos[i]
    df_A.loc[lines[i],f] = -1
    df_A.loc[lines[i],t] = 1

df_A.to_csv('line_to_node_map.csv')

df_line_to_node_map = pd.read_csv('line_to_node_map.csv',header=0)


# create QPS to node matrix

A = np.zeros((len(df_QP_NA),len(all_nodes)))

df_A = pd.DataFrame(A)
df_A.columns = all_nodes
df_A['name'] = list(df_QP_NA['producer'])
df_A.set_index('name',inplace=True)

for i in range(0,len(df_QP_NA)):
    node = df_QP_NA.loc[i,'node']
    g = df_QP_NA.loc[i,'producer']
    df_A.loc[g,node] = 1

df_A.to_csv('qps_to_node_map.csv')

df_node_to_producer_map = pd.read_csv('qps_to_node_map.csv',header=0)



##daily ts of demand at each node

# fake demand data for now
d = np.ones((365,len(all_nodes)))*2
df_demand = pd.DataFrame(d)
df_demand.columns = all_nodes


#node-to-node flow tariffs
nodal_flow_tariffs = pd.read_csv('PipelineTariff.csv',header=0,index_col = None)

froms = list(nodal_flow_tariffs['from'])
tos = list(nodal_flow_tariffs['to'])

for f in froms:
    new_f = f.replace('-','_')
    i = froms.index(f)
    froms[i] = new_f

for t in tos:
    new_t = t.replace('-','_')
    i = tos.index(t)
    tos[i] = new_t

L = []
for i in range(0,len(nodal_flow_tariffs)):
    L.append(froms[i] + '_to_' + tos[i])

nodal_flow_tariffs.index=L
nodal_flow_tariffs = nodal_flow_tariffs.drop(columns=['to','from'])




#node-to-node flow tariffs capacities
nodal_flow_tariffs_CAP = pd.read_csv('PipeTariffCurveQty.csv',header=0)

froms = list(nodal_flow_tariffs_CAP['from'])
tos = list(nodal_flow_tariffs_CAP['to'])

for f in froms:
    new_f = f.replace('-','_')
    i = froms.index(f)
    froms[i] = new_f

for t in tos:
    new_t = t.replace('-','_')
    i = tos.index(t)
    tos[i] = new_t
    
L = []
for i in range(0,len(nodal_flow_tariffs_CAP)):
    L.append(froms[i] + '_to_' + tos[i])

nodal_flow_tariffs_CAP.index=L
nodal_flow_tariffs_CAP = nodal_flow_tariffs_CAP.drop(columns=['to','from'])



######=================================================########
######               Write data file                   ########
######=================================================########

######====== write data.dat file ======########
with open(''+str(data_name)+'.dat', 'w') as f:

  
####### producer sets by type  

    # Non-associated
    f.write('set NA :=\n')
    
    # pull relevant generators
    for prod in range(0,len(df_QP_NA)):
        unit_name = df_QP_NA.loc[prod,'producer']
        f.write(unit_name + ' ')
    f.write(';\n\n')        

    print('Producer sets')


######Set nodes, sources and sinks

    # nodes
    f.write('set nodes :=\n')
    for z in all_nodes:
        name = z.replace('-','_')
        f.write(name + ' ')
    f.write(';\n\n')
    
    print('nodes')
    
    # lines
    f.write('set lines :=\n')
    for z in lines:
        f.write(z + ' ')
    f.write(';\n\n')
    
    print('lines')
    
    

####### simulation period and horizon
    f.write('param SimDays := %d;' % SimDays)
    f.write('\n')
    f.write('param HorizonDays := %d;' % HorizonDays)
    f.write('\n\n')


######=================================================########
######              Producers                     ########
######=================================================########
    
####### create parameter matrix for producers
    f.write('param:' + '\t')
    for c in df_QP_NA.columns:
        if c != 'producer':
            f.write(c + '\t')
    f.write(':=\n\n')
    for i in range(0,len(df_QP_NA)):    
        for c in df_QP_NA.columns:
            if c == 'producer':
                unit_name = df_QP_NA.loc[i,'producer']
                unit_name = unit_name.replace(' ','_')
                unit_name = unit_name.replace('&','_')
                unit_name = unit_name.replace('.','')
                f.write(unit_name + '\t')  
            else:
                f.write(str((df_QP_NA.loc[i,c])) + '\t')               
        f.write('\n')
    f.write(';\n\n')     
    
    print('QPS params')

######=================================================########
######               Pipelines                       ########
######=================================================########

####### create parameter matrix for pipeline paths (source and sink connections)
    f.write('param:' + '\t' + 'FlowLim :=' + '\n')
    for z in lines:
        f.write(z + '\t' + str(df_pipelines.loc[z,'capacity']) + '\n')
    f.write(';\n\n')

    print('pipelines')
    
    #Pipeline tariffs
    f.write('param:' + '\t' +'FTariff_1' + '\t' + 'FTariff_2' + '\t' + 'FTariff_3' + '\t' + 'FTariff_4' + '\t' + 'FTariff_5:=' + '\n')
    for z in lines:
        if z in list(nodal_flow_tariffs.index):
            f.write(z + '\t' + str(nodal_flow_tariffs.loc[z,'step1']) + '\t')
            f.write(str(nodal_flow_tariffs.loc[z,'step2']) + '\t')
            f.write(str(nodal_flow_tariffs.loc[z,'step3']) + '\t')
            f.write(str(nodal_flow_tariffs.loc[z,'step4']) + '\t')
            f.write(str(nodal_flow_tariffs.loc[z,'step5']) + '\n')
        else:
            f.write(z + '\t' + str(0) + '\t')
            f.write(str(0) + '\t')
            f.write(str(0) + '\t')
            f.write(str(0) + '\t')
            f.write(str(0) + '\n')
    
    f.write(';\n\n')
    

    #Pipeline tariffs capacities
    f.write('param:' + '\t' +'FTariff_1_CAP' + '\t' + 'FTariff_2_CAP' + '\t' + 'FTariff_3_CAP' + '\t' + 'FTariff_4_CAP' + '\t' + 'FTariff_5_CAP:=' + '\n')
    for z in lines:
        if z in list(nodal_flow_tariffs_CAP.index):
            f.write(z + '\t' + str(nodal_flow_tariffs_CAP.loc[z,'step1']) + '\t')
            f.write(str(nodal_flow_tariffs_CAP.loc[z,'step2']) + '\t')
            f.write(str(nodal_flow_tariffs_CAP.loc[z,'step3']) + '\t')
            f.write(str(nodal_flow_tariffs_CAP.loc[z,'step4']) + '\t')
            f.write(str(nodal_flow_tariffs_CAP.loc[z,'step5']) + '\n')
        else:
            f.write(z + '\t' + str(0) + '\t')
            f.write(str(0) + '\t')
            f.write(str(0) + '\t')
            f.write(str(0) + '\t')
            f.write(str(0) + '\n')
    
    f.write(';\n\n')
    
    
####### Daily timeseries
    
    # demand (daily)
    f.write('param:' + '\t' + 'SimDemand:=' + '\n')      
    for z in all_nodes:
        for h in range(0,len(df_demand)):
            new = z.replace('-','_')
            f.write(new + '\t' + str(h+1) + '\t' + str(df_demand.loc[h,z]) + '\n')
    f.write(';\n\n')
    
    print('demand')
        

###### Maps
    
    f.write('param QPS_to_node:')
    f.write('\n')
    f.write('\t' + '\t')

    for j in df_node_to_producer_map.columns:
        if j!= 'name':
            j_new = j.replace('-','_')
            f.write(j_new + '\t')
    f.write(':=' + '\n')
    for i in range(0,len(df_node_to_producer_map)):   
        for j in df_node_to_producer_map.columns:
            f.write(str(df_node_to_producer_map.loc[i,j]) + '\t')
        f.write('\n')
    f.write(';\n\n')
    
    print('Producers to node map')


    f.write('param line_to_node:')
    f.write('\n')
    f.write('\t' + '\t')

    for j in df_line_to_node_map.columns:
        if j!= 'line':
            j_new = j.replace('-','_')
            f.write(j_new + '\t')
    f.write(':=' + '\n')
    for i in range(0,len(df_line_to_node_map)):   
        for j in df_line_to_node_map.columns:
            f.write(str(df_line_to_node_map.loc[i,j]) + '\t')
        f.write('\n')
    f.write(';\n\n')
    
    print('Line to node map')   
print ('Complete:',data_name)
