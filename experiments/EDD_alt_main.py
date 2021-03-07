from functions import *
from tqdm import tqdm 

# 更改目標式後，每次排工作需要考慮是否已經超過 due date，因此有新的寫法
# 
def EDD_alt_main(m, n, h, machine_infos, job_dic, method_id):

    machine_workload = {}  # 紀錄結束工作量
    job_schedule = {}  #記錄 (job,開始時間,初始良率)
    loss= {}  #記錄各機台累積的 (job,tardiness)
    cu_loss = {}  # 記錄各機台累積 tardiness
    init_yr = {}  # 複製紀錄初始良率
    for i in range(m):
            machine_workload[i+1] = 0
            cu_loss[i+1] = 0
            init_yr[i+1] = machine_infos[i+1][3]
            job_schedule[i+1] = []
            loss[i+1] = []
    
    if method_id == 1 or method_id == 2:
        if method_id == 1:
            # 方法一：排工作(weight > due > qty)，不考慮維修 (initail solution)
            sort_job_dic = dict(sorted(job_dic.items(), key=lambda item: item[1][2]))
            sort_job_dic = dict(sorted(sort_job_dic.items(), key=lambda item: item[1][1]))
            sort_job_dic = dict(sorted(sort_job_dic.items(), key=lambda item: item[1][0]))
        if method_id == 2:
            # 方法二：排工作(due/weight > qty)，不考慮維修 (initail solution)
            sort_job_dic = dict(sorted(job_dic.items(), key=lambda item: item[1][1]/item[1][2]))
            sort_job_dic = dict(sorted(sort_job_dic.items(), key=lambda item: item[1][0]))

        # 產生 EDD 排程
        print("正在用 EDD rule 產生排程：")
        for no,[load,due,weight] in tqdm(sort_job_dic.items()):  # 利用 EDD + SPT 排完所有工作
            min_machine = select_machine(machine_workload)  # 選目前完成時間最短的機台
            job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))
            pro_rate = machine_infos[min_machine][0]
            decrease_rate = machine_infos[min_machine][1]
            maintain_time = machine_infos[min_machine][2]
            # initial_yield_rate = machine_infos[min_machine][3]
            L_yield_rate = machine_infos[min_machine][4]
            while load > 0 and machine_workload[min_machine] < due:  # 未完成訂單且未到 due day
                rec_rate = (init_yr[min_machine]/100)*pro_rate
                load -= rec_rate
                if init_yr[min_machine] > L_yield_rate:
                    init_yr[min_machine] -= decrease_rate
                    if init_yr[min_machine] < L_yield_rate:  # 不能低於良率 lower bound
                        init_yr[min_machine] = L_yield_rate
                machine_workload[min_machine] += 1
            if load > 0:  # 未滿足交期
                cu_loss[min_machine] += load*weight  # 只有太晚做完才要算 cost
            loss[min_machine].append((no,cu_loss[min_machine]))
        print('維修前的 EDD 排程總 tardiness：\n',sum(cu_loss.values()))
    elif method_id == 3 or method_id == 4:
        jobs = list(job_dic.keys())
        while jobs:  # 還有 job 尚未排到  
            # 方法三：排工作(due-t/weight > qty)，不考慮維修 (initail solution)
            min_machine = select_machine(machine_workload)  # 選目前完成時間最短的機台
            if method_id == 3:
                no = select_job(job_dic, jobs, machine_workload[min_machine])
                jobs.remove(no)
            load = job_dic[no][0]
            due = job_dic[no][1]
            weight = job_dic[no][2]
            job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))
            pro_rate = machine_infos[min_machine][0]
            decrease_rate = machine_infos[min_machine][1]
            maintain_time = machine_infos[min_machine][2]
            # initial_yield_rate = machine_infos[min_machine][3]
            L_yield_rate = machine_infos[min_machine][4]
            while load > 0 and machine_workload[min_machine] < due:  # 未完成訂單且未到 due day
                rec_rate = (init_yr[min_machine]/100)*pro_rate
                load -= rec_rate
                if init_yr[min_machine] > L_yield_rate:
                    init_yr[min_machine] -= decrease_rate
                    if init_yr[min_machine] < L_yield_rate:  # 不能低於良率 lower bound
                        init_yr[min_machine] = L_yield_rate
                machine_workload[min_machine] += 1
            if load > 0:  # 未滿足交期
                cu_loss[min_machine] += load*weight  # 只有太晚做完才要算 cost
            loss[min_machine].append((no,cu_loss[min_machine]))
        print('維修前的 EDD 排程總 tardiness：\n',sum(cu_loss.values()))
    
    # 初始解 GREEDY 找維修
    maint_sche, new_cu_loss, new_loss, new_job_schedule = \
        alt_decide_maintenance(machine_infos, job_schedule, cu_loss, loss, h, job_dic)
    
    print('產生排程：\n',new_job_schedule)
    print('產生維修時程：\n',maint_sche)
    print('維修後的 EDD 排程總 production loss = ',sum(new_cu_loss.values()))
    edd_obj = sum(new_cu_loss.values())
    
    return job_schedule, loss, cu_loss, edd_obj