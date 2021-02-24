import random
import numpy as np
import copy

def select_machine(machine_workload):
    min_machine = sorted(machine_workload.items(), key=lambda item: item[1])[0][0]  # 選目前完成時間最短的機台
    return min_machine

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

def insert_maintenance(time, maintain_t, pro_rate, schedule, tardiness, decrease_rate, L_yield_rate, job_dic):  # 在某個時間點插入維修重新規劃後的結果
    time += maintain_t  # 加上維修時間
    init_yr = 100  # 修到 100 %
    new_tard = tardiness
    new_schedule = []
    new_tardiness_list = []
    for job_n,t,_ in schedule:  # 剩下還沒有排到的工作
        due = job_dic[job_n][1]
        new_schedule.append((job_n, time, init_yr))
        cost_time, after_yield = job_time(job_dic[job_n][0], init_yr, decrease_rate, L_yield_rate, pro_rate)
        time += cost_time
        init_yr = after_yield
        new_tard += max(time-due,0)  # 只有太晚做完才要算 cost
        new_tardiness_list.append((job_n,new_tard))
    return new_tardiness_list, new_tard, new_schedule

def decide_maintenance(decrease_rate,job_schedule, cu_tard, tardiness, h, pro_rate, maintain_time, job_dic, L_yield_rate):  # GREEDY 選擇會更好的維修決策
    maintenance_schedule = []  #紀錄修過的紀錄 (機台,時間)
    new_cu_tard = copy.deepcopy(cu_tard)
    new_tardiness = copy.deepcopy(tardiness)
    new_job_schedule = copy.deepcopy(job_schedule)
    machine_maintenance_cnt = {}  # 記錄每台機器在不同時間上跑了多久
    for i in range(len(job_schedule)):
        machine_maintenance_cnt[i+1] = {}
    flag = 1
    while flag == 1:  # 每個時段最多可以修 h 台
        flag = 0  # 假設該輪沒有找到更好的，就會是 0
        best_improve_tard = 0 
        for machine in range(len(job_schedule)):  # 每台機台都跑過
            machine_no = machine + 1
            index = 0  # 紀錄跑到機台上的哪個 job
            m_improve_tard = 0
            m_tard = new_cu_tard[machine_no]  # 初始設定最小 tardiness 為原先機台 (machine_no) 的 tardiness
            for job_no,time,yr in new_job_schedule[machine_no]:  # 每台機台的每個地方插入維修，求最好的
                if index == 0:
                    temp_tardiness_list, temp_tard, temp_schedule = insert_maintenance(time, maintain_time[machine_no], pro_rate[machine_no], new_job_schedule[machine_no][index:], 
                                                            0, decrease_rate[machine_no], L_yield_rate[machine_no], job_dic)
                else:
                    temp_tardiness_list, temp_tard, temp_schedule = insert_maintenance(time, maintain_time[machine_no], pro_rate[machine_no], new_job_schedule[machine_no][index:], 
                                                            new_tardiness[machine_no][index-1][1], decrease_rate[machine_no], L_yield_rate[machine_no], job_dic)
                if temp_tard < m_tard:
                    flag = 1
                    m_index = index
                    m_improve_tard = m_tard - temp_tard
                    m_tard = temp_tard
                    m_tardiness_list = temp_tardiness_list
                    m_schedule = temp_schedule
                    m_info = (machine_no,time)  # (維修機台, 維修時間)
                index += 1
            if m_improve_tard > best_improve_tard:
                best_index = m_index
                best_tard = m_tard
                best_tardiness_list = m_tardiness_list
                best_schedule = m_schedule
                best_info = m_info
                best_improve_tard = m_improve_tard
        if flag == 1:  # 維修會更好
            if best_index not in machine_maintenance_cnt[best_info[0]]:
                machine_maintenance_cnt[best_info[0]][best_index] = 0
            else:
                machine_maintenance_cnt[best_info[0]][best_index] += 1
            if machine_maintenance_cnt[best_info[0]][best_index] <= h:
                new_cu_tard[best_info[0]] = best_tard
                new_tardiness[best_info[0]][best_index:]= best_tardiness_list
                new_job_schedule[best_info[0]][best_index:] = best_schedule
                maintenance_schedule.append(best_info)
            

    return maintenance_schedule, new_cu_tard, new_tardiness, new_job_schedule


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
    maintenance_schedule = []  #紀錄修過的紀錄 (機台,時間)
    new_cu_loss = copy.deepcopy(cu_loss)
    new_loss = copy.deepcopy(loss)
    new_job_schedule = copy.deepcopy(job_schedule)
    machine_maintenance_cnt = {}  # 記錄每台機器在不同時間上跑了多久
    for i in range(len(job_schedule)):
        machine_maintenance_cnt[i+1] = {}
    flag = 1
    while flag == 1:  # 上次維修有可能更好，所以繼續找
        flag = 0  # 假設該輪沒有找到更好的，就會是 0
        best_improve_loss = 0 
        for machine in range(len(job_schedule)):  # 每台機台都跑過
            machine_no = machine + 1
            index = 0  # 紀錄跑到機台上的哪個 job
            m_improve_loss = 0
            m_loss = new_cu_loss[machine_no]  # 初始設定最小 loss 為原先機台 (machine_no) 的 loss
            pro_rate = machine_infos[machine_no][0]
            decrease_rate = machine_infos[machine_no][1]
            maintain_time = machine_infos[machine_no][2]
            # initial_yield_rate = machine_infos[machine_no][3]
            L_yield_rate = machine_infos[machine_no][4]
            for job_no, time, yr in new_job_schedule[machine_no]:  # 每台機台的每個地方插入維修，求最好的
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
                    m_info = (machine_no, time)  # (維修機台, 維修時間)
                index += 1
            if m_improve_loss > best_improve_loss:  # 選出所有機台維修中，最好的一個維修時段
                best_index = m_index
                best_loss = m_loss
                best_loss_list = m_loss_list
                best_schedule = m_schedule
                best_info = m_info
                best_improve_loss = m_improve_loss
        if flag == 1:  # 維修會更好
            if best_info[1] not in machine_maintenance_cnt[best_info[0]]:
                machine_maintenance_cnt[best_info[0]][best_info[1]] = 0
            else:
                machine_maintenance_cnt[best_info[0]][best_info[1]] += 1
            if machine_maintenance_cnt[best_info[0]][best_info[1]] <= h:  # 該時段還有資源維修，則更新 new_job_schedule
                new_cu_loss[best_info[0]] = best_loss
                new_loss[best_info[0]][best_index:]= best_loss_list
                new_job_schedule[best_info[0]][best_index:] = best_schedule
                maintenance_schedule.append(best_info)
    return maintenance_schedule, new_cu_loss, new_loss, new_job_schedule

def alt_insert_maintenance(time, maintain_t, pro_rate, schedule, loss, decrease_rate, L_yield_rate, job_dic):  # 在某個時間點插入維修重新規劃後的結果
    time += maintain_t  # 加上維修時間
    init_yr = 100  # 修到 100 %
    new_loss = loss
    new_schedule = []
    new_loss_list = []
    for job_n,_,_ in schedule:  # 剩下還沒有排到的工作
        load = job_dic[job_n][0]
        due = job_dic[job_n][1]
        weight = job_dic[job_n][2]
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

def reschedule_alt(time, init_yr, new_job, pro_rate, schedule, loss, decrease_rate, L_yield_rate, job_dic):  # 將工作重新排列後
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
    for job_n,_,_ in schedule:
        load = job_dic[job_n][0]
        due = job_dic[job_n][1]
        weight = job_dic[job_n][2]
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