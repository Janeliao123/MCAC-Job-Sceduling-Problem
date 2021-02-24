# In[0]:
from tqdm import tqdm 
import time
import random
import numpy as np
import copy
from EDD_alt import *
from Tabu_alt_obj import *

#In[1]
edd_result = []
tabu_result = []
path = "m5n50_1.txt"
with open(path,"r") as f:
    m_n_h = [int(x) for x in f.readline().strip().split(' ')]
    m = m_n_h[0]  # 機台數
    n = m_n_h[1]  # 訂單數
    h = m_n_h[2]  # 最多修幾台
    pro_rate = {}  # 生產速率
    decrease_rate = {}  # 機台下降良率
    maintain_time = {}  # 機台維修時間
    initial_yield_rate = {}  # 初始良率
    L_yield_rate = {}  # 最低良率
    for i in range(m):  # 機台編號由 1 開始
        machine_info = [int(x) for x in f.readline().strip().split(' ')]
        pro_rate[i+1] = machine_info[0]
        decrease_rate[i+1] = machine_info[1]
        maintain_time[i+1] = machine_info[2]
        initial_yield_rate[i+1] = machine_info[3]
        L_yield_rate[i+1] = machine_info[4]
    lines = f.readlines()
    job_dic = {}  # job_dic[機台編號] = [訂購量,交期]
    job_no = 1
    for l in lines:
        temp = [int(x) for x in l.strip().split(' ')]
        job_dic[job_no] = temp  
        job_no += 1

    # EDD
    org_time = time.time()
    job_schedule, loss, cu_loss, maint_sche, new_cu_loss, new_loss, new_job_schedule, edd_obj = \
        EDD_alt(m, n, h, pro_rate, decrease_rate, maintain_time, initial_yield_rate, L_yield_rate, job_dic)
    edd_result.append([edd_obj, str(time.time() - org_time)])
    
    # Tabu
    base_maint_loss = sum(new_cu_loss.values())
    tabu_size = 1000
    loop = 100
    cross_order = True
    cross_machine = True
    org_time = time.time()
    tabu_obj = Tabu_alt(h, tabu_size, loop, cross_order, cross_machine, maintain_time, base_maint_loss, job_schedule, pro_rate, loss, decrease_rate, L_yield_rate, cu_loss, maint_sche, job_dic)
    tabu_result.append([tabu_obj, str(time.time() - org_time)])
# In[2]
def das_algorithm(file_num = 0, m_list = [], n_list = [], folder_name = "testdata", result_name = "result"):
    edd_result = []
    tabu_result = []

    for m in m_list:
        final1 = open(result_name + "/m" + str(m) + "result_edd.txt", "w+")
        final2 = open(result_name + "/m" + str(m) + "result_tabu.txt", "w+")
          # 寫檔案
        final1.write('name runtime gap objectives \n')
        final2.write('name runtime gap objectives \n')
        
        for n in n_list:
            prefix = "m"+str(m)+"n"+str(n)+"_" # problem 編號
            file_list = [str(i+1) for i in range(file_num)]

            for index in file_list:
                path = folder_name + "/" + prefix + index + ".txt"
                # 讀入 input
                with open(path,"r") as f:
                    m_n_h = [int(x) for x in f.readline().strip().split(' ')]
                    m = m_n_h[0]  # 機台數
                    n = m_n_h[1]  # 訂單數
                    h = m_n_h[2]  # 最多修幾台
                    pro_rate = {}  # 生產速率
                    decrease_rate = {}  # 機台下降良率
                    maintain_time = {}  # 機台維修時間
                    initial_yield_rate = {}  # 初始良率
                    L_yield_rate = {}  # 最低良率
                    for i in range(m):  # 機台編號由 1 開始
                        machine_info = [int(x) for x in f.readline().strip().split(' ')]
                        pro_rate[i+1] = machine_info[0]
                        decrease_rate[i+1] = machine_info[1]
                        maintain_time[i+1] = machine_info[2]
                        initial_yield_rate[i+1] = machine_info[3]
                        L_yield_rate[i+1] = machine_info[4]
                    lines = f.readlines()
                    job_dic = {}  # job_dic[機台編號] = [訂購量,交期]
                    job_no = 1
                    for l in lines:
                        temp = [int(x) for x in l.strip().split(' ')]
                        job_dic[job_no] = temp  
                        job_no += 1

                    # EDD
                    org_time = time.time()
                    job_schedule, loss, cu_loss, maint_sche, new_cu_loss, new_loss, new_job_schedule, edd_obj = \
                        EDD_alt(m, n, h, pro_rate, decrease_rate, maintain_time, initial_yield_rate, L_yield_rate, job_dic)
                    edd_result.append([edd_obj, str(time.time() - org_time)])
                    
                    # Tabu
                    base_maint_loss = sum(new_cu_loss.values())
                    tabu_size = 1000
                    loop = 100
                    cross_order = True
                    cross_machine = True
                    org_time = time.time()
                    tabu_obj = Tabu_alt(h, tabu_size, loop, cross_order, cross_machine, maintain_time, base_maint_loss, job_schedule, pro_rate, loss, decrease_rate, L_yield_rate, cu_loss, maint_sche, job_dic)
                    tabu_result.append([tabu_obj, str(time.time() - org_time)])
                      
        name = prefix + index

        for i in range(len(edd_result)):
            final1.write(name + " " + str(edd_result[i][1]) + " " + "-" + " " + str(edd_result[i][0]) + "\n")
            final2.write(name + " " + str(tabu_random_result[i][1]) + " " + "-" + " " + str(tabu_random_result[i][0]) + "\n")
            
        final1.close()
        final2.close()

            
# %%
