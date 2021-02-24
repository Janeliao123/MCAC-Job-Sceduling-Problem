from functions import *
from tqdm import tqdm 
def EDD_alt(m, n, h, pro_rate, decrease_rate, maintain_time, initial_yield_rate, L_yield_rate, job_dic):

    # 排工作，不考慮維修 (initail solution)
    sort_job_dic = dict(sorted(job_dic.items(), key=lambda item: item[1][0]))
    sort_job_dic = dict(sorted(sort_job_dic.items(), key=lambda item: item[1][1]))

    machine_workload = {}  # 紀錄結束工作量
    job_schedule = {}  #記錄 (job,開始時間,初始良率)
    loss= {}  #記錄各機台累積的 (job,tardiness)
    cu_loss = {}  # 記錄各機台累積 tardiness
    init_yr = {}  # 複製紀錄初始良率
    
    # 產生 EDD 排程
    for i in range(m):
        machine_workload[i+1] = 0
        job_schedule[i+1] = []
        cu_loss[i+1] = 0
        loss[i+1] = []
        init_yr[i+1] = initial_yield_rate[i+1]
    print("正在用 EDD rule 產生排程：")
    for no,[load,due] in tqdm(sort_job_dic.items()):  # 利用 EDD + SPT 排完所有工作
        min_machine = select_machine(machine_workload)  # 選目前完成時間最短的機台
        job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))
        temp_load = load
        while temp_load > 0 and machine_workload[min_machine] < due:  # 未完成訂單且未到 due day
            rec_rate = (init_yr[min_machine]/100)*pro_rate[min_machine]
            temp_load -= rec_rate
            if init_yr[min_machine] > L_yield_rate[min_machine]:
                init_yr[min_machine] -= decrease_rate[min_machine]
                if init_yr[min_machine] < L_yield_rate[min_machine]:  # 不能低於良率 lower bound
                    init_yr[min_machine] = L_yield_rate[min_machine]
            machine_workload[min_machine] += 1
        if temp_load > 0:  # 未滿足交期
            cu_loss[min_machine] += temp_load  # 只有太晚做完才要算 cost
        loss[min_machine].append((no,cu_loss[min_machine]))
    print('維修前的 EDD 排程總 tardiness：\n',sum(cu_loss.values()))
    
    # 初始解 GREEDY 找維修
    maint_sche, new_cu_loss, new_loss, new_job_schedule = \
        alt_decide_maintenance(decrease_rate, job_schedule, cu_loss, loss, h, pro_rate, maintain_time, job_dic, L_yield_rate)
    
    print('產生維修時程：\n',maint_sche)
    print('維修後的 EDD 排程總 production loss = ',sum(new_cu_loss.values()))
    edd_obj = sum(new_cu_loss.values())
    
    return job_schedule, loss, cu_loss, maint_sche, new_cu_loss, new_loss, new_job_schedule, edd_obj