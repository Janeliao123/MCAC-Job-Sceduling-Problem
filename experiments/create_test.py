# In[]
import random
from pathlib import Path

# 一個情境會有多少測資
file_num = 20

# ==== Factors(6) ====
# numbers of machine 
m_list = [5, 3, 1]
# due dates
due_date_list = [(0.7,0.9), (0.9,1.1), (1.1,1.3)]
# weights
max_weight_list = [(1,10), (1,5), (1,1)]
# maintenance_time
main_time_list = [5, 3, 1]
# resource limit
resource_limit = ['m', 3, 1]
# decreasing rate
decreasing_rate = [(1.5,2.5), (0.5,1.5), (0,1)]

# 將這些 factors 寫為 dictionary
# scenario['machine']['H'] = [H,M,M,M,M,M]
# scenario['machine']['L'] = [L,M,M,M,M,M]
# 同理，一共有 6種 Factors
combinations = [m_list,due_date_list,max_weight_list,main_time_list,resource_limit,decreasing_rate]
factors_list = {0:'machine',1:'due_date',2:'weight',3:'main_time',4:'resource_limit',5:'decreasing_rate'}
scenarios = {}
for index, main in enumerate(combinations):
    scenarios[factors_list[index]] = {}
    scenarios[factors_list[index]]['H'] = {}
    scenarios[factors_list[index]]['L'] = {}
    for index_2, others in enumerate(combinations):
        if others == main:  # 是要進行區隔的 factor
            scenarios[factors_list[index]]['H'][factors_list[index_2]] = others[0]
            scenarios[factors_list[index]]['L'][factors_list[index_2]] = others[2]
        else:
            scenarios[factors_list[index]]['H'][factors_list[index_2]] = others[1]
            scenarios[factors_list[index]]['L'][factors_list[index_2]] = others[1]

print(scenarios)

for scenario, value in scenarios.items():
    # print(scenario)
    # print(value)
        
    # ==== Parameters(5) ====
    # numbers of jobs
    n = 25
    # production rate (lots/hr)
    production_rate = 40
    # lower_bound
    lower_bound = 50
    # initial_rate
    initial_rate = 90
    # job_quantity
    job_quantity = (20, 200)

    for type, factors in value.items():

        # 定義路徑及檔名
        prefix = scenario + '_' + type # problem 編號
        folder_name = "testdata_0512/" + prefix
        Path(folder_name).mkdir(parents=True, exist_ok=True)
        file_list = [str(i) for i in range(1,file_num+1)]
    
        for f in file_list:

            file = open(folder_name + "/" + prefix + "_" + f + ".txt", "w+")
            
            # ==== Factors(6) ==== 
            m = factors['machine']
            # due day 參數 (估計平均完工總時長)
            eta = ((job_quantity[0] + job_quantity[1]) * n) / ((production_rate + lower_bound)*m)
            # 訂單 j 的 due day
            D_j = [round(random.uniform(factors['due_date'][0] * eta, factors['due_date'][1] * eta)) for i in range(n)]
            # Timelength
            T = max(D_j)
            # Weight of jobs
            w_j = [round(random.uniform(factors['weight'][0], factors['weight'][1])) for i in range(n)]
            # 機台 i 的維修時間長
            F_i = [factors['main_time'] for i in range(m)]
            # 一次最多能維修幾台（resource_limit）
            if factors['resource_limit'] == 'm':
                H = m
            else:
                H = factors['resource_limit']
            # 機台 i 每期的減損率
            B_i = [round(random.uniform(factors['decreasing_rate'][0], factors['decreasing_rate'][1])) for i in range(m)]  
            
            # ==== Parameters(5) ==== 
            Q_j = [round(random.uniform(job_quantity[0], job_quantity[1])) for i in range(n)]   # 訂單 j 的需求量
            A_ij = [production_rate for i in range(m)]   # 機台 i 100% 時的產量(常數)
            r_i0 = [initial_rate for i in range(m)] # *100   # 機台 i 在第 0 期的生產率
            L_i = [lower_bound for i in range(m)] # *100      # 機台 i 的最低生產率（要變）

            
            # 將資料寫入檔案
            file.write(str(m) + " " + str(n) + " " + str(H) + " " + str(T) + "\n")

            for i in range(m):
                file.write(str(A_ij[i]) + " " + str(B_i[i]) + " " + str(F_i[i]) + " " + str(r_i0[i]) + " " + str(L_i[i]) + "\n")

            for i in range(n-1):
                file.write(str(Q_j[i]) + " " + str(D_j[i]) + " " + str(w_j[i]) + "\n")

            file.write(str(Q_j[n-1]) + " " + str(D_j[n-1]) + " " + str(w_j[n-1]))

            file.close()
# %%

# In[]
import random
from pathlib import Path

# 一個情境會有多少測資
file_num = 20

# ==== Factors(6) ====
# numbers of machine 
m_list = [5, 3, 1]
# due dates
due_date_list = [(0.7,0.9), (0.9,1.1), (1.1,1.3)]
# weights
max_weight_list = [(1,10), (1,5), (1,1)]
# maintenance_time
main_time_list = [5, 3, 1]
# resource limit
resource_limit = ['m', 3, 1]
# decreasing rate
decreasing_rate = [(1.5,2.5), (0.5,1.5), (0,1)]

# ==== Parameters(5) ====
# numbers of jobs
n = 25
# production rate (lots/hr)
production_rate = 40
# lower_bound
lower_bound = 50
# initial_rate
initial_rate = 90
# job_quantity
job_quantity = (20, 200)

# 定義路徑及檔名
prefix = 'benchmark'  # problem 編號
folder_name = "testdata_0512/" + prefix
Path(folder_name).mkdir(parents=True, exist_ok=True)
file_list = [str(i) for i in range(1,file_num+1)]

for f in file_list:

    file = open(folder_name + "/" + prefix + "_" + f + ".txt", "w+")
    
    # ==== Factors(6) ==== 
    m = m_list[1]
    # due day 參數 (估計平均完工總時長)
    eta = ((job_quantity[0] + job_quantity[1]) * n) / ((production_rate + lower_bound)*m)
    # 訂單 j 的 due day
    D_j = [round(random.uniform(due_date_list[1][0] * eta, due_date_list[1][1] * eta)) for i in range(n)]
    # Timelength
    T = max(D_j)
    # Weight of jobs
    w_j = [round(random.uniform(max_weight_list[1][0], max_weight_list[1][1])) for i in range(n)]
    # 機台 i 的維修時間長
    F_i = [main_time_list[1] for i in range(m)]
    # 一次最多能維修幾台（resource_limit）
    H = resource_limit[1]
    # 機台 i 每期的減損率
    B_i = [round(random.uniform(decreasing_rate[1][0], decreasing_rate[1][1])) for i in range(m)]  
    
    # ==== Parameters(5) ==== 
    Q_j = [round(random.uniform(job_quantity[0], job_quantity[1])) for i in range(n)]   # 訂單 j 的需求量
    A_ij = [production_rate for i in range(m)]   # 機台 i 100% 時的產量(常數)
    r_i0 = [initial_rate for i in range(m)] # *100   # 機台 i 在第 0 期的生產率
    L_i = [lower_bound for i in range(m)] # *100      # 機台 i 的最低生產率（要變）

    
    # 將資料寫入檔案
    file.write(str(m) + " " + str(n) + " " + str(H) + " " + str(T) + "\n")

    for i in range(m):
        file.write(str(A_ij[i]) + " " + str(B_i[i]) + " " + str(F_i[i]) + " " + str(r_i0[i]) + " " + str(L_i[i]) + "\n")

    for i in range(n-1):
        file.write(str(Q_j[i]) + " " + str(D_j[i]) + " " + str(w_j[i]) + "\n")

    file.write(str(Q_j[n-1]) + " " + str(D_j[n-1]) + " " + str(w_j[n-1]))

    file.close()
# %%
