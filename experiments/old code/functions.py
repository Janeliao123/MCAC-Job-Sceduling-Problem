import random
import numpy as np
import copy

def select_machine(machine_workload):
    min_machine = sorted(machine_workload.items(), key=lambda item: item[1])[0][0]  # 選目前完成時間最短的機台
    return min_machine

def select_job(job_dic, jobs, t):
    job_value = {}
    for j in jobs:
        job_value[j] = (job_dic[j][1]-t)/job_dic[j][2]
    sort_job_dic = dict(sorted(job_value.items(), key=lambda item: item[1]))
    return list(sort_job_dic.keys())[0]

def job_time(workload, initial_yield_rate, decrease_rate, lower_bound, pro_rate):  # 計算訂單要花多少時間
    time = 0
    after_rate = initial_yield_rate
    while workload > 0:  # 直到滿足訂單數
        rec_rate = (after_rate/100)*pro_rate
        workload -= rec_rate
        if after_rate > lower_bound:
            after_rate -= decrease_rate
            if after_rate < lower_bound:  # 不能低於良率 lower bound
                after_rate = lower_bound
        time += 1
    return time, after_rate

def find_job_level(job_schedule):  # 找出同一層的工作
    pos_jobs = {}
    max_pos = max([len(x) for x in job_schedule.values()])
    position = range(0,max_pos)
    for p in position:
        pos_jobs[p] = []
        for j in job_schedule:
            if len(job_schedule[j]) > p:
                 pos_jobs[p].append(job_schedule[j][p][0])
    return pos_jobs, max_pos

def reschedule(time, init_yr, new_job, pro_rate, schedule, tardiness, decrease_rate, L_yield_rate, job_dic):  # 將工作重新排列後
    new_tard = tardiness
    new_tardiness_list = []
    new_schedule = []
    # 算新插入的交換工作
    new_schedule.append((new_job, time, init_yr))
    cost_time, after_yield = job_time(job_dic[new_job][0], init_yr, decrease_rate, L_yield_rate, pro_rate)
    time += cost_time
    init_yr = after_yield
    due = job_dic[new_job][1]
    new_tard += max(time-due,0)
    new_tardiness_list.append((new_job,new_tard))
    # 後面依序重新計算
    for job_n,t,_ in schedule:
        due = job_dic[job_n][1]
        new_schedule.append((job_n, time, init_yr))
        cost_time, after_yield = job_time(job_dic[job_n][0], init_yr, decrease_rate, L_yield_rate, pro_rate)
        time += cost_time
        init_yr = after_yield
        new_tard += max(time-due,0)  # 只有太晚做完才要算 cost
        new_tardiness_list.append((job_n,new_tard))
    return new_tardiness_list, new_tard, new_schedule

def simple_schedule(job_schedule):
    simple_sche = {}
    for m in job_schedule.keys():
        simple_sche[m] = []
        for job_n,_,_ in job_schedule[m]:
            simple_sche[m].append(job_n)
    return simple_sche

def new_simple(job1, job2, simple_sche):
    new_sche = copy.deepcopy(simple_sche)
    for m in simple_sche.keys():
        for i in range(len(simple_sche[m])):
            if simple_sche[m][i] == job1:
                new_sche[m][i] = job2
            elif simple_sche[m][i] == job2:
                new_sche[m][i] = job1 
    return new_sche

def alt_decide_maintenance(machine_infos, job_schedule, cu_loss, loss, h, job_dic):  # 最小化欠貨量
    print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    new_cu_loss = copy.deepcopy(cu_loss)
    new_loss = copy.deepcopy(loss)
    new_job_schedule = copy.deepcopy(job_schedule)
    machine_maintenance_cnt = {}  # 記錄在不同時間上有哪些機台在維修
    maintenance_schedule = {}  #紀錄修過的紀錄 (機台,時間)
    for i in job_schedule.keys():
        maintenance_schedule[i] = []
    flag = 1
    while flag == 1:  # 上次維修有可能更好，所以繼續找
        flag = 0  # 假設該輪沒有找到更好的，就會是 0
        best_improve_loss = 0 
        for machine_no in job_schedule.keys():  # 每台機台都跑過
            m_improve_loss = 0
            m_loss = new_cu_loss[machine_no]  # 初始設定最小 loss 為原先機台 (machine_no) 的 loss
            pro_rate = machine_infos[machine_no][0]
            decrease_rate = machine_infos[machine_no][1]
            maintain_time = machine_infos[machine_no][2]
            # initial_yield_rate = machine_infos[machine_no][3]
            L_yield_rate = machine_infos[machine_no][4]/100*pro_rate
            for index, (job_no, time, yr) in enumerate(new_job_schedule[machine_no]):  # 每台機台的每個地方插入維修，求最好的
                if yr != 100:  # 沒修過才要考慮插入維修
                    if index == 0:
                        temp_loss_list, temp_loss, temp_schedule = alt_insert_maintenance(time, maintain_time, pro_rate, new_job_schedule[machine_no][index:], 
                                                                0, decrease_rate, L_yield_rate, job_dic)
                    else:
                        temp_loss_list, temp_loss, temp_schedule = alt_insert_maintenance(time, maintain_time, pro_rate, new_job_schedule[machine_no][index:], 
                                                                new_loss[machine_no][index-1][1], decrease_rate, L_yield_rate, job_dic)

                    if temp_loss < m_loss:  # 維修會原先方案更好，則記錄該筆維修
                        flag = 1
                        m_index = index
                        m_improve_loss = new_cu_loss[machine_no] - temp_loss
                        m_loss = temp_loss
                        m_loss_list = temp_loss_list
                        m_schedule = temp_schedule
                        m_time = time  # 維修時間

            if m_improve_loss > best_improve_loss:  # 選出所有機台維修中，最好的一個維修時段
                best_index = m_index
                best_loss = m_loss
                best_loss_list = m_loss_list
                best_schedule = m_schedule
                best_time = m_time
                best_improve_loss = m_improve_loss
                best_m = machine_no
        if flag == 1:  # 維修會更好
            # print('還在找...')
            # print('當下維修時間表',machine_maintenance_cnt)
            # print('至今排程',new_job_schedule)
            # print('至今維修排程',maintenance_schedule)
            if best_time not in machine_maintenance_cnt:
                machine_maintenance_cnt[best_time] = []
            if len(machine_maintenance_cnt[best_time]) <= h:  # 該時段還有資源維修，則更新 new_job_schedule
                # print('還可以修...')
                machine_maintenance_cnt[best_time].append(best_m)
                new_cu_loss[best_m] = best_loss
                new_loss[best_m][best_index:]= best_loss_list
                new_job_schedule[best_m][best_index:] = best_schedule
                maintenance_schedule[best_m].append(best_time)
                # print("維修排程：", maintenance_schedule)
                # print("更新的機台 ", best_m,'，loss = ', new_cu_loss[best_m],'維修時間 = ', best_time,"，進步 = ", best_improve_loss)
                # print('新的 loss 表:\n',new_loss)
    return maintenance_schedule, new_cu_loss, new_loss, new_job_schedule

def alt_insert_maintenance(time, maintain_t, pro_rate, schedule, loss, decrease_rate, L_yield_rate, job_dic):  # 在某個時間點插入維修重新規劃後的結果
    time += maintain_t  # 加上維修時間
    init_yr = 100  # 修到 100 %
    new_loss = loss
    new_schedule = []
    new_loss_list = []
    for job_n,_,yr in schedule:  # 剩下還沒有排到的工作
        load = job_dic[job_n][0]
        due = job_dic[job_n][1]
        weight = job_dic[job_n][2]
        if yr == 100: # 如果有維修過，會出現良率 = 100
            time += maintain_t
            init_yr = 100
        new_schedule.append((job_n, time, init_yr))
        while load > 0 and time < due:  # 未完成訂單且未到 due day
            rec_rate = (init_yr/100)*pro_rate
            load -= rec_rate
            if init_yr > L_yield_rate:
                init_yr -= decrease_rate
                if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                    init_yr = L_yield_rate
            time += 1
        if load > 0:  # 未滿足交期
            new_loss += load*weight  # 只有太晚做完才要算 cost
        new_loss_list.append((job_n,new_loss))  # (job, 結束後在該機台上至今累積的 loss)
    return new_loss_list, new_loss, new_schedule

def reschedule_alt(time, init_yr, new_job, maintain_time, pro_rate, schedule, loss, decrease_rate, L_yield_rate, job_dic):  # 將工作重新排列後
    
    new_loss = loss
    new_loss_list = []
    new_schedule = []
    load = job_dic[new_job][0]
    due = job_dic[new_job][1]
    weight = job_dic[new_job][2]
    new_schedule.append((new_job, time, init_yr))
    # 算新插入的交換工作
    # if time < due:
    #     new_schedule.append((new_job, time, init_yr))
    while load > 0 and time < due:  # 未完成訂單且未到 due day
        rec_rate = (init_yr/100)*pro_rate
        load -= rec_rate
        if init_yr > L_yield_rate:
            init_yr -= decrease_rate
            if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                init_yr = L_yield_rate
        time += 1
    if load > 0:  # 未滿足交期
        new_loss += load*weight  # 只有太晚做完才要算 cost
    new_loss_list.append((new_job,new_loss))
    # 後面依序重新計算
    for job_n,_,yr in schedule:
        load = job_dic[job_n][0]
        due = job_dic[job_n][1]
        weight = job_dic[job_n][2]
        
        if yr == 100:
            time += maintain_time
            init_yr = 100
        new_schedule.append((job_n, time, init_yr))
        temp_load = load
        while temp_load > 0 and time < due:  # 未完成訂單且未到 due day
            rec_rate = (init_yr/100)*pro_rate
            temp_load -= rec_rate
            if init_yr > L_yield_rate:
                init_yr -= decrease_rate
                if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                    init_yr = L_yield_rate
            time += 1
        if temp_load > 0:  # 未滿足交期
            new_loss += temp_load*weight  # 只有太晚做完才要算 cost
        new_loss_list.append((job_n,new_loss))
    return new_loss_list, new_loss, new_schedule

