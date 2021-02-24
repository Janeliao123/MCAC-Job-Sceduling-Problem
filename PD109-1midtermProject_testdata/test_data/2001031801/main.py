#In[0]
from tqdm import tqdm 
import random
import numpy as np
import copy
from EDD import *
from Tabu import *
from Tabu_origin import *
from functions import *

#In[1]
# 讀入 input
with open("m2n10\m2n10_2.txt","r") as f:
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
    job_schedule, tardiness, cu_tard, maint_sche, new_cu_tard, new_tardiness, new_job_schedule = \
        EDD(m, n, h, pro_rate, decrease_rate, maintain_time, initial_yield_rate, L_yield_rate, job_dic)
    print("EDD SCEDULE = ",job_schedule)
    base_maint_tard = sum(new_cu_tard.values())
    tabu_size = 500
    loop = 500
    cross_order = True
    # cross_order = False
    cross_machine = True
    # cross_machine = False
    origin_obj = Tabu_origin(h, tabu_size, loop, maintain_time, base_maint_tard, job_schedule, pro_rate, tardiness, decrease_rate, L_yield_rate, cu_tard, maint_sche, job_dic)
    # swap_maint_sche, swap_maint_cu_tard, swap_maint_tardiness, swap_maint_job_schedule = \
    tabu_obj, target, schedule_list, tabu_list = Tabu(h, tabu_size, loop, cross_order, cross_machine, maintain_time, base_maint_tard, job_schedule, pro_rate, tardiness, decrease_rate, L_yield_rate, cu_tard, maint_sche, job_dic)
    

#In[2]
new_sche = []

for sche in schedule_list:
    new_sche.append(simple_schedule(sche))

print(new_sche)
# print(target)
# print(tabu_list)

#In[3]
import matplotlib.pyplot as plt
plt.figure(figsize = (20,10))
#做圖
plt.plot(target, 'blue', label = 'tardiness')
plt.show()

# %%
