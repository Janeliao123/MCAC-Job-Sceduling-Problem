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
def das_algorithm(file_num = 0, m_list = [], n_list = [], folder_name = "testdata", result_name = "result", tabu_size = [100], loop=100, methods = [3]):
    for m in m_list:
        for n in n_list:
            for method_id in methods:
                tabu_dic = {}
                edd_df = pd.DataFrame(columns=['name', 'runtime', 'gap', 'objectives'])
                prefix = "m"+str(m)+"n"+str(n)+"_" # problem 編號
                file_list = [str(i+1) for i in range(file_num)]
                for t in tabu_size:
                        # 建立 dataframe
                        tabu_dic[t] = pd.DataFrame(columns=['name', 'runtime', 'gap', 'objectives'])
                for index in file_list:
                    path = folder_name + "/" + "m" + str(m) + "n" + str(n) + "/" + prefix + index + ".txt"
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
                        job_dic = {}  # job_dic[機台編號] = [訂購量, 交期, 權重]
                        job_no = 1
                        for l in lines:
                            temp = [int(x) for x in l.strip().split(' ')]
                            job_dic[job_no] = temp  
                            job_no += 1

                        # EDD
                        org_time = time.time()
                        job_schedule, loss, cu_loss, edd_obj = \
                            EDD_alt_main(m, n, h, machine_infos, job_dic, method_id)
                        edd_df = edd_df.append({'name':prefix + str(index), 'runtime':float(time.time() - org_time), 'gap':'-', 'objectives': edd_obj} , ignore_index=True)
                        # Tabu
                        for t in tabu_size:
                            base_maint_loss = edd_obj
                            cross_order = True
                            cross_machine = True
                            org_time = time.time()
                            tabu_obj = Tabu_alt(h, t, loop, cross_order, cross_machine, base_maint_loss, job_schedule, loss, cu_loss, job_dic, machine_infos)
                            tabu_dic[t]= tabu_dic[t].append({'name':prefix + str(index), 'runtime':float(time.time() - org_time), 'gap':'-', 'objectives': tabu_obj} , ignore_index=True)
                # 寫入 20 次測資結果
                with pd.ExcelWriter(result_name + "/m" + str(m) + "n" + str(n) + "_edd" + str(method_id) + ".xlsx", engine="openpyxl", mode='w') as writer:  
                    edd_df = edd_df.append({'name':'average', 'runtime':edd_df.runtime.mean(), 'gap':'-', 'objectives': edd_df.objectives.mean()}, ignore_index=True)
                    edd_df.to_excel(writer)
                with pd.ExcelWriter(result_name + "/m" + str(m) + "n" + str(n) + "_tabu" + str(method_id) + ".xlsx", engine="openpyxl", mode='w') as writer:  
                    for k in tabu_dic.keys():
                        tabu_dic[k] = tabu_dic[k].append({'name':'average', 'runtime':tabu_dic[k].runtime.mean(), 'gap':'-', 'objectives': tabu_dic[k].objectives.mean()}, ignore_index=True)
                        tabu_dic[k].to_excel(writer, sheet_name = 'tabu_size = '+str(k))

# %%
