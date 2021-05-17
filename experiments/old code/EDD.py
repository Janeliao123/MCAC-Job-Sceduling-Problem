from functions import *
from tqdm import tqdm 
def EDD(m, n, h, pro_rate, decrease_rate, maintain_time, initial_yield_rate, L_yield_rate, job_dic):

    # 排工作，不考慮維修 (initail solution)
    sort_job_dic = dict(sorted(job_dic.items(), key=lambda item: item[1][0]))
    sort_job_dic = dict(sorted(sort_job_dic.items(), key=lambda item: item[1][1]))

    machine_workload = {}  # 紀錄結束工作量
    job_schedule = {}  #記錄 (job,開始時間,初始良率)
    tardiness= {}  #記錄各機台累積的 (job,tardiness)
    cu_tard = {}  # 記錄各機台累積 tardiness
    init_yr = {}  # 複製紀錄初始良率
    
    # 產生 EDD 排程
    for i in range(m):
        machine_workload[i+1] = 0
        job_schedule[i+1] = []
        cu_tard[i+1] = 0
        tardiness[i+1] = []
        init_yr[i+1] = initial_yield_rate[i+1]
    print("正在用 EDD rule 產生排程：")
    for no,[load,due] in tqdm(sort_job_dic.items()):  # 利用 EDD + SPT 排完所有工作
        min_machine = select_machine(machine_workload)  # 選目前完成時間最短的機台
        job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))  
        cost_time, after_yield = job_time(load, init_yr[min_machine], decrease_rate[min_machine], L_yield_rate[min_machine],pro_rate[min_machine])
        machine_workload[min_machine] += cost_time
        init_yr[min_machine] = after_yield
        cu_tard[min_machine] += max(machine_workload[min_machine]-due,0)  # 只有太晚做完才要算 cost
        tardiness[min_machine].append((no,cu_tard[min_machine]))
    print('維修前的 EDD 排程總 tardiness：\n',sum(cu_tard.values()))
    
    # 初始解 GREEDY 找維修
    maint_sche, new_cu_tard, new_tardiness, new_job_schedule = \
        decide_maintenance(decrease_rate, job_schedule, cu_tard, tardiness, h, pro_rate, maintain_time, job_dic, L_yield_rate)
    
    print('產生維修時程：\n',maint_sche)
    print('維修後的 EDD 排程總 tardiness：\n',sum(new_cu_tard.values()))
    edd_obj = sum(new_cu_tard.values())
    
    return job_schedule, tardiness, cu_tard, maint_sche, new_cu_tard, new_tardiness, new_job_schedule, edd_obj