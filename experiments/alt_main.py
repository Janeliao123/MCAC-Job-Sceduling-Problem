# In[0]:
from tqdm import tqdm 
import time
import random
import numpy as np
import copy
from EDD_alt_main import *
from Tabu_alt_obj import *
import pandas as pd
from feasible_check import *
from maintenace_rule import *
from pathlib import Path

#In[1]
# edd_result = []
# tabu_result = []
# path = "testdata/m2n15/m2n15_2.txt"
# methods = [1,2,3]
# for method_id in methods:
#     with open(path,"r") as f:
#         m_n_h = [int(x) for x in f.readline().strip().split(' ')]
#         m = m_n_h[0]  # 機台數
#         n = m_n_h[1]  # 訂單數
#         h = m_n_h[2]  # 最多修幾台
#         machine_infos = {}
#         for i in range(m):  # 機台編號由 1 開始
#             machine_info = [int(x) for x in f.readline().strip().split(' ')]
#             machine_infos[i+1] = machine_info  # [生產速率, 下降速率, 維修時間, 初始良率, 良率下限]
#         lines = f.readlines()
#         job_dic = {}  # job_dic[機台編號] = [訂購量,交期]
#         job_no = 1
#         for l in lines:
#             temp = [int(x) for x in l.strip().split(' ')]
#             job_dic[job_no] = temp  
#             job_no += 1

#         # EDD
#         org_time = time.time()
#         job_schedule, loss, cu_loss, edd_obj = \
#             EDD_alt_main(m, n, h, machine_infos, job_dic, method_id)
#         edd_result.append([edd_obj, str(time.time() - org_time)])

#         # Tabu
#         base_maint_loss = edd_obj
#         tabu_size = 100
#         loop = 100
#         cross_order = True
#         cross_machine = True
#         org_time = time.time()
#         tabu_obj = Tabu_alt(h, tabu_size, loop, cross_order, cross_machine, base_maint_loss, job_schedule, loss, cu_loss, job_dic, machine_infos)
#         # print("schedule\n",best_maint_job_schedule)
#         # print("loss\n", best_maint_loss)
#         # tabu_result.append([tabu_obj, str(time.time() - org_time)])
#         print(method_id,"done!")
# In[]

# print("是否通過檢查：",feasible_check(best_maint_job_schedule, machine_infos, job_dic, tabu_obj, h))


# In[2]
def das_algorithm(file_num=0, factors_list={}, type=[], folder_name="testdata", result_name="result", tabu_size=[100], loop=100, methods=[3], maintenance_rule=0, yield_threshold=[90]):
    
    flag_list = {}
    path_name = folder_name + "/maintenance_rule"
    Path(path_name).mkdir(parents=True, exist_ok=True)
    
    if maintenance_rule:
        edd_avg_df = pd.DataFrame(columns=['factor', 'type', 'method', 'threshold', 'runtime', 'objectives'])
    else:
        edd_avg_df = pd.DataFrame(columns=['factor', 'type', 'method', 'runtime', 'objectives'])
    
    tabu_avg_df = {}
    for t in tabu_size:
        if maintenance_rule:
            tabu_avg_df[t] = pd.DataFrame(columns=['factor', 'type', 'method', 'threshold', 'runtime', 'objectives'])
        else:
            tabu_avg_df[t] = pd.DataFrame(columns=['factor', 'type', 'method', 'runtime', 'objectives'])
    
    for factor in factors_list.values():
        for t in type:
            for method_id in methods:
                for y in yield_threshold:
                    
                    # prefix = "m"+str(m)+"n"+str(n)+"_"  # problem 編號
                    prefix = factor + '_' + t  # problem 編號
                    flag_list[factor,t,method_id] = (0,'none')
                    file_list = [str(i+1) for i in range(file_num)]
                    
                    if maintenance_rule:
                        edd_df = pd.DataFrame(columns=['factor', 'type', 'method', 'threshold', 'index', 'runtime', 'gap', 'objectives'])
                    else:
                        edd_df = pd.DataFrame(columns=['factor', 'type', 'method', 'index', 'runtime', 'gap', 'objectives'])
                    
                    tabu_dic = {}
                    for t in tabu_size:
                        # 建立 dataframe
                        if maintenance_rule:
                            tabu_dic[t] = pd.DataFrame(columns=['factor', 'type', 'method', 'threshold', 'index', 'runtime', 'gap', 'objectives'])
                        else:
                            tabu_dic[t] = pd.DataFrame(columns=['factor', 'type', 'method', 'index', 'runtime', 'gap', 'objectives'])

                    for index in file_list:
                        path = folder_name + "/" + prefix + "/" + prefix + "_" + index + ".txt"
                        # 讀入 input
                        with open(path,"r") as f:
                            m_n_h = [int(x) for x in f.readline().strip().split(' ')]
                            m = m_n_h[0]  # 機台數
                            n = m_n_h[1]  # 訂單數
                            h = m_n_h[2]  # 最多修幾台
                            machine_infos = {}
                            for i in range(m):  # 機台編號由 1 開始
                                machine_info = [int(x) for x in f.readline().strip().split(' ')]
                                machine_infos[i+1] = machine_info  # [生產速率, 下降速率, 維修時間, 初始良率, 良率下限]
                            lines = f.readlines()
                            job_dic = {}  # job_dic[job 編號] = [訂購量, 交期, 權重]
                            job_no = 1
                            for l in lines:
                                temp = [int(x) for x in l.strip().split(' ')]
                                job_dic[job_no] = temp  
                                job_no += 1

                            # EDD
                            org_time = time.time()
                            message_na = 0  # 1 : 印出 massage
                            if maintenance_rule:
                                job_schedule, loss, cu_loss, edd_obj, total_flag_edd = \
                                    rule_main(m, n, h, machine_infos, job_dic, y, method_id, message_na)
                                edd_df = edd_df.append({'factor': factor, 'type': t, 'method': str(method_id), 'threshold': str(y), 'index': str(index), 'runtime':float(time.time() - org_time), 'gap':'-', 'objectives': edd_obj} , ignore_index=True)
                            else:
                                job_schedule, loss, cu_loss, edd_obj, total_flag_edd = \
                                    EDD_alt_main(m, n, h, machine_infos, job_dic, method_id, message_na)
                                edd_df = edd_df.append({'factor': factor, 'type': t, 'method': str(method_id), 'index': str(index), 'runtime':float(time.time() - org_time), 'gap':'-', 'objectives': edd_obj} , ignore_index=True)
                            
                            # Tabu
                            for t in tabu_size:
                                base_maint_loss = edd_obj
                                cross_level = True
                                cross_machine = True
                                org_time = time.time()
                                message_na = 1
                                tabu_obj, total_flag_tabu = Tabu_alt(h, t, loop, cross_level, cross_machine, base_maint_loss, job_schedule, loss, cu_loss, job_dic, machine_infos, message_na)
                                if maintenance_rule:
                                    tabu_dic[t] = tabu_dic[t].append({'factor': factor, 'type': t, 'method': str(method_id), 'threshold': str(y), 'index': str(index), 'runtime':float(time.time() - org_time), 'gap':'-', 'objectives': tabu_obj} , ignore_index=True)
                                else:
                                    tabu_dic[t] = tabu_dic[t].append({'factor': factor, 'type': t, 'method': str(method_id), 'index': str(index), 'runtime':float(time.time() - org_time), 'gap':'-', 'objectives': tabu_obj} , ignore_index=True)
                            
                            # feasible checker
                            if total_flag_edd == 1:
                                flag_list[factor,t,method_id] = (1,'edd')
                            elif total_flag_tabu == 1:
                                flag_list[factor,t,method_id] = (1,'tabu')

                    # 寫入 20 次測資結果
                    if maintenance_rule:
                        with pd.ExcelWriter(result_name + "/maintenance_rule/" + prefix + "/method_" + str(method_id) + "_threshold" + str(y) + ".xlsx", engine="openpyxl", mode='w') as writer:  
                            edd_df = edd_df.append({'factor': factor, 'type': t, 'method': str(method_id), 'threshold': str(y), 'index': 'average', 'runtime':edd_df.runtime.mean(), 'gap':'-', 'objectives': edd_df.objectives.mean()}, ignore_index=True)
                            edd_df.to_excel(writer)
                            edd_avg_df = edd_avg_df.append({'factor': factor, 'type': t, 'method': str(method_id), 'threshold': str(y), 'runtime':edd_df.runtime.mean(), 'objectives': edd_df.objectives.mean()}, ignore_index=True)
                        with pd.ExcelWriter(result_name + "/maintenance_rule/" + prefix + "/with_tabu_method_" + str(method_id) + "_threshold" + str(y) + ".xlsx", engine="openpyxl", mode='w') as writer:  
                            for k in tabu_dic.keys():
                                tabu_dic[k] = tabu_dic[k].append({'factor': factor, 'type': t, 'method': str(method_id), 'threshold': str(y), 'index': 'average', 'runtime':tabu_dic[k].runtime.mean(), 'gap':'-', 'objectives': tabu_dic[k].objectives.mean()}, ignore_index=True)
                                tabu_dic[k].to_excel(writer, sheet_name = 'tabu_size = ' + str(k))
                                tabu_avg_df[k] = tabu_avg_df[k].append({'factor': factor, 'type': t, 'method': str(method_id), 'threshold': str(y), 'runtime':tabu_dic[k].runtime.mean(), 'objectives': tabu_dic[k].objectives.mean()}, ignore_index=True)
                                
                    else:
                        with pd.ExcelWriter(result_name + "/" + prefix + "/edd_method_" + str(method_id) + ".xlsx", engine="openpyxl", mode='w') as writer:  
                            edd_df = edd_df.append({'factor': factor, 'type': t, 'method': str(method_id), 'index': 'average', 'runtime':edd_df.runtime.mean(), 'gap':'-', 'objectives': edd_df.objectives.mean()}, ignore_index=True)
                            edd_df.to_excel(writer)
                            edd_avg_df = edd_avg_df.append({'factor': factor, 'type': t, 'method': str(method_id), 'runtime':edd_df.runtime.mean(), 'objectives': edd_df.objectives.mean()}, ignore_index=True)
                        with pd.ExcelWriter(result_name + "/" + prefix + "/edd_with_tabu_method_" + str(method_id) + ".xlsx", engine="openpyxl", mode='w') as writer:  
                            for k in tabu_dic.keys():
                                tabu_dic[k] = tabu_dic[k].append({'factor': factor, 'type': t, 'method': str(method_id), 'index': 'average', 'runtime':tabu_dic[k].runtime.mean(), 'gap':'-', 'objectives': tabu_dic[k].objectives.mean()}, ignore_index=True)
                                tabu_dic[k].to_excel(writer, sheet_name = 'tabu_size = ' + str(k))
                                tabu_avg_df[k] = tabu_avg_df[k].append({'factor': factor, 'type': t, 'method': str(method_id), 'runtime':tabu_dic[k].runtime.mean(), 'objectives': tabu_dic[k].objectives.mean()}, ignore_index=True)
    if maintenance_rule:
        with pd.ExcelWriter(result_name + "/maintenance_rule/edd_avg.xlsx", engine="openpyxl", mode='w') as writer:
            edd_avg_df.to_excel(writer)
        for t in tabu_size:
            with pd.ExcelWriter(result_name + "/maintenance_rule/tabu_" + str(k) + "_avg.xlsx", engine="openpyxl", mode='w') as writer:
                tabu_avg_df[t].to_excel(writer)
    else:
        with pd.ExcelWriter(result_name + "/edd_avg.xlsx", engine="openpyxl", mode='w') as writer:
            edd_avg_df.to_excel(writer)
        for t in tabu_size:
            with pd.ExcelWriter(result_name + "/tabu_" + str(k) + "_avg.xlsx", engine="openpyxl", mode='w') as writer:
                tabu_avg_df[t].to_excel(writer)
    with open(result_name + "/feasible_checker.txt", 'w') as f:  
        for (factor,t,id),(v,method) in flag_list.items():
            if v == 1:
                f.write("在 fator " + str(factor) + "type" + str(t) + "的 method " + str(id) + "時，有不符合 feasible checker 的演算法 " + method)

# %%
