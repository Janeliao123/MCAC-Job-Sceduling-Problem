from functions import *
from tqdm import tqdm 
import itertools

# Tabu 
def Tabu_alt(h, tabu_size, loop, cross_order, cross_machine, base_maint_loss, job_schedule, loss, cu_loss, job_dic, machine_infos):

    tabu_list = []
    best_job_schedule = copy.deepcopy(job_schedule)
    best_cu_loss = copy.deepcopy(cu_loss)
    best_loss = copy.deepcopy(loss)

    print("正在用改版找出所有 neighbbor 的 Tabu search 找出更好的排程，一共執行 %d 次迴圈 ：" % loop)
    swap_job_schedule = copy.deepcopy(job_schedule)
    swap_cu_loss = copy.deepcopy(cu_loss)
    swap_loss = copy.deepcopy(loss)
    target_list = []
    schedule_list = []
    for i in range(loop):  # 一共需要重複找 neighbor loop 次
        # 將工作分層(order)
        job_level, max_level = find_job_level(swap_job_schedule)
        neighbor_pair = [] # 記錄所有鄰近交換的 job
        for l in range(0,max_level-1):
            neighbor_pair.extend(list(itertools.combinations(job_level[l], 2)))  # 每個 order 內的工作彼此交換
            if cross_order == True:  # 要跨 order
                temp = []
                for j in range(len(job_level[l])):
                    recent_job = job_level[l][j]       
                    if cross_machine == True:  # 會跟所有下一個 order 的 job 交換
                        for job in job_level[l+1]:
                            temp.append((recent_job, job))
                        if len(job_level)-1 >= l+2:
                            for job in job_level[l+2]:  # 會跟所有下下個 order 的 job 交換
                                temp.append((recent_job, job))
                        if len(job_level)-1 >= l+3:
                            for job in job_level[l+3]:  # 會跟所有下下下個 order 的 job 交換
                                temp.append((recent_job, job))
                        if len(job_level)-1 >= l+4:
                            for job in job_level[l+4]:  # 會跟所有下下下個 order 的 job 交換
                                temp.append((recent_job, job))
                        if len(job_level)-1 >= l+5:
                            for job in job_level[l+5]:  # 會跟所有下下下個 order 的 job 交換
                                temp.append((recent_job, job))
                    else:
                        for k,v in swap_job_schedule.items():
                            for x in range(len(v)):
                                if x != (len(v)-1) and v[x][0] == recent_job:
                                    job = v[x+1][0]  # 和後面 order 交換
                                    temp.append((recent_job, job))
                neighbor_pair.extend(temp)                        
        flag = 0 # 表示第一次找 neighbor，還沒有初始基準
        # print("鄰居 list = ",neighbor_pair)
        simple_sche = simple_schedule(swap_job_schedule) 
        # print("新的 neighbor 基準 = ", simple_sche)
        for (job_1,job_2) in neighbor_pair:  # 更新所有的 neightboring pair
            new_simple_shce =  new_simple(job_1, job_2, simple_sche)
            if new_simple_shce not in tabu_list:
            # if (job_1,job_2) or (job_2,job_1) not in tabu_list: # 沒有換過，才要換換看
                # 先建立一個紀錄交換排程用的資料
                temp_job_schedule = copy.deepcopy(swap_job_schedule)
                temp_cu_loss = copy.deepcopy(swap_cu_loss)
                temp_loss = copy.deepcopy(swap_loss)
                for i in range(len(job_schedule)):  # 找出要交換的工作機台時間位址並重新規劃
                    machine = i+1
                    index = 0
                    pro_rate = machine_infos[machine][0]
                    decrease_rate = machine_infos[machine][1]
                    maintain_time = machine_infos[machine][2]
                    # initial_yield_rate = machine_infos[machine][3]
                    L_yield_rate = machine_infos[machine][4]
                    for job_n, t, init_yr in swap_job_schedule[machine]:
                        if job_n == job_1:
                            machine_1 = machine 
                            index_1 = index 
                            if index_1 == 0:
                                before_loss = 0
                            else:
                                before_loss = swap_loss[machine][index-1][1]
                            new_loss_list_1, new_loss_1, new_schedule_1 = \
                                reschedule_alt(t, init_yr, job_2, pro_rate, swap_job_schedule[machine][index+1:],
                                before_loss, decrease_rate, L_yield_rate, job_dic)

                        elif job_n == job_2:
                            machine_2 = machine 
                            index_2 = index 
                            if index_2 == 0:
                                before_loss = 0
                            else:
                                before_loss = swap_loss[machine][index-1][1]
                            new_loss_list_2, new_loss_2, new_schedule_2 = \
                                reschedule_alt(t, init_yr, job_1, pro_rate, swap_job_schedule[machine][index+1:],
                                before_loss, decrease_rate, L_yield_rate, job_dic)
                        index += 1
                # 將交換排程紀錄下來
                temp_loss[machine_1][index_1:] = new_loss_list_1 
                temp_loss[machine_2][index_2:] = new_loss_list_2
                temp_cu_loss[machine_1] = new_loss_1
                temp_cu_loss[machine_2] = new_loss_2
                temp_job_schedule[machine_1][index_1:] = new_schedule_1 
                temp_job_schedule[machine_2][index_2:] = new_schedule_2

                if machine_1 == machine_2:  # 同機台的工作要重新算
                    check_job_schedule = []
                    check_loss_list = []
                    check_loss = 0
                    time = 0
                    pro_rate = machine_infos[machine_1][0]
                    decrease_rate = machine_infos[machine_1][1]
                    initial_yield_rate = machine_infos[machine_1][3]
                    L_yield_rate = machine_infos[machine_1][4]
                    init_yr = initial_yield_rate
                    for job_n,_,_ in temp_job_schedule[machine_1]:
                        load = job_dic[job_n][0]
                        due = job_dic[job_n][1]
                        weight = job_dic[job_n][2]
                        check_job_schedule.append((job_n, time, init_yr))
                        while load > 0 and time < due:  # 未完成訂單且未到 due day
                            rec_rate = (init_yr/100)*pro_rate
                            load -= rec_rate
                            if init_yr > L_yield_rate:
                                init_yr -= decrease_rate
                                if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                                    init_yr = L_yield_rate
                            time += 1
                        if load > 0:  # 未滿足交期
                            check_loss += load*weight  # 只有太晚做完才要算 cost
                        check_loss_list.append((job_n,check_loss))
                    temp_loss[machine_1] = check_loss_list 
                    temp_cu_loss[machine_1] = check_loss
                    temp_job_schedule[machine_1] = check_job_schedule

                # 插入維修
                temp_maint_sche, temp_new_cu_loss, temp_new_loss, temp_new_job_schedule = \
                    alt_decide_maintenance(machine_infos, temp_job_schedule, temp_cu_loss, temp_loss, h, job_dic)
                # 記錄最好的 neighborhood schedule
                if flag == 0 :  # 表示第一個 neighborhood
                    flag = 1
                    best_temp_job_schedule = copy.deepcopy(temp_job_schedule)
                    best_temp_cu_loss = copy.deepcopy(temp_cu_loss)
                    best_temp_loss = copy.deepcopy(temp_loss)
                    best_temp_maint_loss = sum(temp_new_cu_loss.values())
                    best_pair = (job_1, job_2)
                elif sum(temp_new_cu_loss.values()) < best_temp_maint_loss:
                    # 更新排程資訊
                    # print("交換後會更好的 job = ",(job_1,job_2))
                    # print("MAIN_schedule = ",temp_new_job_schedule)
                    # print("schedule = ",temp_job_schedule)
                    best_temp_maint_loss = sum(temp_new_cu_loss.values())
                    best_temp_loss = temp_loss
                    best_temp_cu_loss = temp_cu_loss
                    best_temp_job_schedule = temp_job_schedule
        # 更新最好的 neighborhood
        target_list.append(sum(best_temp_cu_loss.values()))
        schedule_list.append(best_temp_job_schedule)
        swap_loss = best_temp_loss
        swap_job_schedule = best_temp_job_schedule
        swap_cu_loss = best_temp_cu_loss
        # 沒看過，更新 tabu list 資訊
        # tabu_list.append((best_pair[0],best_pair[1]))
        tabu_list.append(simple_schedule(best_temp_job_schedule))
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0) 
        if  best_temp_maint_loss < base_maint_loss:  # 表示新的交換有進步，則更新排程
            print("improve! loss = ", best_temp_maint_loss)
            # 更新排程資訊
            base_maint_loss = best_temp_maint_loss
            best_loss = best_temp_loss
            best_job_schedule = best_temp_job_schedule
            best_cu_loss = best_temp_cu_loss
            

    # 把最好的排程找維修決策
    best_maint_sche, best_maint_cu_loss, best_maint_loss, best_maint_job_schedule = \
        alt_decide_maintenance(machine_infos, best_job_schedule, best_cu_loss, best_loss, h, job_dic)
    print('產生排程：\n',best_maint_job_schedule)
    print('產生維修時程：\n',best_maint_sche)
    print('Tabu 後的總 loss\n',sum(best_maint_cu_loss.values()))
    tabu_obj = sum(best_maint_cu_loss.values())

    return tabu_obj
