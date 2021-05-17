from functions_change import *
from tqdm import tqdm 
from feasible_check import *

# 更改目標式後，每次排工作需要考慮是否已經超過 due date，因此有新的寫法
# 
def EDD_alt_main(m, n, h, machine_infos, job_dic, method_id, message_na):

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
    
    if message_na:
        print("以第" + str(method_id) + " 種 EDD rule 產生排程：")
    
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
        for no,[load,due,weight] in tqdm(sort_job_dic.items()):  # 利用 EDD + SPT 排完所有工作
            min_machine = select_machine(machine_workload)  # 選目前完成時間最短的機台
            job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))
            pro_rate = machine_infos[min_machine][0]
            decrease_rate = machine_infos[min_machine][1]
            maintain_time = machine_infos[min_machine][2]
            # initial_yield_rate = machine_infos[min_machine][3]
            L_yield_rate = machine_infos[min_machine][4]/100*pro_rate
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
    
    elif method_id == 3 or method_id == 4:
        if method_id == 4: # 初始化機台最後一次維修時間
            previous_main = {}
            for m in machine_workload.keys():
                previous_main[m] = 0

        jobs = list(job_dic.keys())
        while jobs:  # 還有 job 尚未排到  
            # 排工作(due-t/weight > qty)
            min_machine = select_machine(machine_workload)  # 選目前完成時間最短的機台
            no = select_job(job_dic, jobs, machine_workload[min_machine])
            if message_na:
                print("選擇機台 " + str(min_machine)+" 插入工作 " + str(no))
            jobs.remove(no)
            load = job_dic[no][0]
            due = job_dic[no][1]
            weight = job_dic[no][2]
            pro_rate = machine_infos[min_machine][0]
            decrease_rate = machine_infos[min_machine][1]
            maintain_time = machine_infos[min_machine][2]
            # initial_yield_rate = machine_infos[min_machine][3]
            L_yield_rate = machine_infos[min_machine][4]/100*pro_rate
            
            # 先記錄當下如果維修後的新排程解
            if method_id == 4:
                # 方法四：考慮維修，排工作
                job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))
                
                # 維修後，排入工作
                temp_workload = machine_workload[min_machine]  # 在上一個工作的完成時段後修
                temp_workload += maintain_time  # 加上維修時間
                temp_init_yr = 100  # 修到 100 %
                temp_cu_loss = cu_loss[min_machine]
                temp_load = load
                while temp_load > 0 and temp_workload < due:  # 未完成訂單且未到 due day
                    rec_rate = (temp_init_yr/100)*pro_rate
                    temp_load -= rec_rate
                    if temp_init_yr > L_yield_rate:
                        temp_init_yr -= decrease_rate
                        if temp_init_yr < L_yield_rate:  # 不能低於良率 lower bound
                            temp_init_yr = L_yield_rate
                    temp_workload += 1
                if temp_load > 0:  # 未滿足交期
                    temp_cu_loss += temp_load*weight  # 只有太晚做完才要算 cost

                # 不考慮維修，排入工作
                temp_workload_without = machine_workload[min_machine]
                temp_init_yr_without = init_yr[min_machine]
                temp_loss_without = cu_loss[min_machine]
                temp_load_without = load
                while temp_load_without > 0 and temp_workload_without < due:  # 未完成訂單且未到 due day
                    rec_rate = (temp_init_yr_without/100)*pro_rate
                    temp_load_without -= rec_rate
                    if temp_init_yr_without > L_yield_rate:
                        temp_init_yr_without -= decrease_rate
                        if temp_init_yr_without < L_yield_rate:  # 不能低於良率 lower bound
                            temp_init_yr_without = L_yield_rate
                    temp_workload_without += 1
                if temp_load_without > 0:  # 未滿足交期
                    temp_loss_without += temp_load_without*weight  # 只有太晚做完才要算 cost

                if temp_loss_without > temp_cu_loss:  # 表示此時維修會比不修效率更好
                    if message_na:
                        print("插入 job 同時安排維修會比較好! 因此會往前找出最佳維修時機。")
                    best_loss = temp_cu_loss
                    best_loss_list = []
                    for index, (j, t, _) in enumerate(job_schedule[min_machine]):
                        if t >= previous_main[min_machine]:  # 只需要考慮上次維修到現在最後一個 job 間何時插入維修較好
                            if index == 0:
                                temp_loss_list, temp_cu_loss, temp_schedule = alt_insert_maintenance(min_machine, t, machine_infos, job_schedule[min_machine][index:], 
                                                                0, job_dic)
                            else:
                                temp_loss_list, temp_cu_loss, temp_schedule = alt_insert_maintenance(min_machine, t, machine_infos, job_schedule[min_machine][index:],
                                                                loss[min_machine][index-1][1], job_dic)
                        if temp_cu_loss <= best_loss:  # 往前其它維修會更好
                            best_loss = temp_cu_loss
                            best_loss_list = temp_loss_list
                            best_schedule = temp_schedule
                            best_index = index
                            best_time = t

                    # 紀錄維修排程、最後維修時間及 index
                    previous_main[min_machine] = best_time
                    job_schedule[min_machine][best_index:] = best_schedule
                    cu_loss[min_machine] = best_loss
                    loss[min_machine][best_index:] = best_loss_list
                    # 3 要素
                    temp_machine_workload = job_schedule[min_machine][-1][1]
                    temp_init_yr = job_schedule[min_machine][-1][2]
                    temp_load = load
                    # 因為插入維修後不會紀錄最終的良率和 workload，所以重算
                    while temp_load > 0 and temp_machine_workload < due:  # 未完成訂單且未到 due day
                        rec_rate = (temp_init_yr/100)*pro_rate
                        temp_load -= rec_rate
                        if temp_init_yr > L_yield_rate:
                            temp_init_yr -= decrease_rate
                            if temp_init_yr < L_yield_rate:  # 不能低於良率 lower bound
                                temp_init_yr = L_yield_rate
                        temp_machine_workload += 1
                    
                    # 紀錄最終 3 要素
                    machine_workload[min_machine] = temp_machine_workload
                    init_yr[min_machine] = temp_init_yr
                    
                else:  # 不修更好
                    if message_na:
                        print("在安排 job 時，不考慮維修會更好。")
                    # 3 要素
                    machine_workload[min_machine] = temp_workload_without
                    init_yr[min_machine] = temp_init_yr_without
                    cu_loss[min_machine] = temp_loss_without
                    loss[min_machine].append((no,cu_loss[min_machine]))
                    
            elif method_id == 3:
                # 方法三：沒有考慮維修，排入工作
                job_schedule[min_machine].append((no,machine_workload[min_machine],init_yr[min_machine]))
                while load > 0 and machine_workload[min_machine] < due:  # 未完成訂單且未到 due day
                    rec_rate = (init_yr[min_machine]/100)*pro_rate
                    load -= rec_rate
                    if init_yr[min_machine] > L_yield_rate:
                        init_yr[min_machine] -= decrease_rate
                        if init_yr[min_machine] < L_yield_rate:  # 不能低於良率 lower bound
                            init_yr[min_machine] = L_yield_rate
                    machine_workload[min_machine] += 1
                if load > 0:  # 未滿足交期
                    cu_loss[min_machine] += int(load*weight)  # 只有太晚做完才要算 cost

                loss[min_machine].append((no,cu_loss[min_machine]))
        
    if message_na:    
        print("維修前的 EDD 排程 job_schedule：\n", job_schedule)
        print('維修前的 EDD 排程 production loss =', loss)
        print('維修前的 EDD 排程 total production loss =',sum(cu_loss.values()))
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    
    # 初始解 GREEDY 找維修
    # print(alt_decide_maintenance(machine_infos, job_schedule, cu_loss, loss, h, job_dic))
    new_cu_loss, new_loss, new_job_schedule \
        = alt_decide_maintenance(machine_infos, job_schedule, cu_loss, loss, h, job_dic)

    if message_na:
        print('維修後的 EDD 排程 job_schedule：\n',new_job_schedule)
        print('維修後的 EDD 排程總 production loss =',new_loss)
        print('維修後的 EDD 排程總 production loss =',sum(new_cu_loss.values()))
    
    edd_obj = sum(new_cu_loss.values())
    message_na = 1
    # check edd
    # print("check edd"+str(method_id)+":\n")
    total_flag = feasible_check(new_job_schedule, machine_infos, job_dic, edd_obj, h, message_na)
                        
    return job_schedule, loss, cu_loss, edd_obj, total_flag