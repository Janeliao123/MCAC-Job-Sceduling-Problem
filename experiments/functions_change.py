import random
import numpy as np
import copy

def check_maintenance_ability(job_schedule, h, time):
    # 統計 schedule 的使用資源
    check_cnt = {} 
    for m, job_list in job_schedule.items():
        for _,t,_ in job_list:
            if t not in check_cnt:
                check_cnt[t] = 1
            elif check_cnt[t] < h:  # 還有維修資源
                check_cnt[t] += 1
    # 評估是否在時間上有資源
    if check_cnt[time] == h:  # 資源滿了
        return False
    else:
        return True


def select_machine(machine_workload):
    min_machine = sorted(machine_workload.items(), key=lambda item: item[1])[0][0]  # 選目前完成時間最短的機台
    return min_machine

def select_job(job_dic, jobs, t):  # (D-t)/W
    job_value = {}
    for j in jobs:
        job_value[j] = (job_dic[j][1]-t)/job_dic[j][2]
    sort_job_dic = dict(sorted(job_value.items(), key=lambda item: item[1]))
    # print("job weight = ",sort_job_dic)
    return list(sort_job_dic.keys())[0]

def find_job_level(job_schedule):  # 找出同一層的工作
    job_schedule_no_main = {}
    for m, job_list in job_schedule.items():
        job_schedule_no_main[m] = []
        for j, t, yr in job_list:
            if j != 'm':
                job_schedule_no_main[m].append(j)
    jobs_level = {}
    max_level = max([len(x) for x in job_schedule_no_main.values()])
    for l in range(max_level):
        jobs_level[l] = []
        for m in job_schedule_no_main:
            if len(job_schedule_no_main[m]) > l:
                 jobs_level[l].append(job_schedule_no_main[m][l])
    return jobs_level, max_level

def remove_maintenance(job_schedule, job_dic, machine_infos):
    new_job_schedule = {}
    new_loss = {}
    new_cu_loss = {}
    for m in job_schedule.keys():
        new_job_schedule[m] = []
        new_loss[m] = []
        cu_loss = 0
        pro_rate = machine_infos[m][0]
        decrease_rate = machine_infos[m][1]
        maintain_time = machine_infos[m][2]
        init_yr = machine_infos[m][3]
        L_yield_rate = machine_infos[m][4]/100*pro_rate
        time = 0
        for j, _, _ in job_schedule[m]:
            if j != 'm':
                load = job_dic[j][0]
                due = job_dic[j][1]
                weight = job_dic[j][2]
                new_job_schedule[m].append((j, time, init_yr))
                while load > 0 and time < due:  # 未完成訂單且未到 due day
                    rec_rate = (init_yr/100)*pro_rate
                    load -= rec_rate
                    if init_yr > L_yield_rate:
                        init_yr -= decrease_rate
                        if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                            init_yr = L_yield_rate
                    time += 1
                if load > 0:
                    cu_loss += load *weight
                new_loss[m].append((j,cu_loss))
        new_cu_loss[m] = cu_loss
    # print("拔掉維修後的排程：",new_job_schedule)
    # print("拔掉維修後的損失：",new_loss)
    return new_job_schedule, new_loss, new_cu_loss
        
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
    
    # 紀錄插入維修後的最新排程
    new_job_schedule = copy.deepcopy(job_schedule)
    new_cu_loss = copy.deepcopy(cu_loss)
    new_loss = copy.deepcopy(loss)
    unable_maint_list = []
    
    # 1.維修有可能更好，所以繼續找 (flag = 0 則表示維修不會再減少 loss)
    flag = 1
    while flag == 1:
        # 在開始找之前，設定 flag = 0
        flag = 0
        best_improve_loss = 0 
        # 找所有機台中維修後 improve 最多的 (best_improve_loss)
        for machine_no, job_list in new_job_schedule.items():
            m_improve_loss = 0
            m_cu_loss = new_cu_loss[machine_no]
            m_loss = new_loss[machine_no]
            # 找每個機台在各個時段中插入維修後 improve 最多的 (m_improve_loss)
            for index, (job_no, time, yr) in enumerate(job_list):  # 每台機台的每個地方插入維修，求最好的
                # 跳過維修紀錄及剛維修完的工作紀錄，並確認該時段有資源插入維修
                if job_no != 'm' and yr != 100 and check_maintenance_ability(new_job_schedule, h, time):
                    if index == 0:
                        temp_loss_list, temp_loss, temp_schedule = alt_insert_maintenance(machine_no, time, machine_infos, job_list[index:], 0, job_dic)  # index: 表示包含現在的都要重排, loss 從 0 開始
                    else:
                        temp_loss_list, temp_loss, temp_schedule = alt_insert_maintenance(machine_no, time, machine_infos, job_list[index:], m_loss[index-1][1], job_dic)

                    if temp_loss < m_cu_loss and temp_schedule not in unable_maint_list:  # 維修會原先方案更好，則記錄該筆維修
                        flag = 1
                        m_index = index
                        m_improve_loss = new_cu_loss[machine_no] - temp_loss
                        m_cu_loss = temp_loss
                        m_loss_list = temp_loss_list
                        m_schedule = temp_schedule

            if m_improve_loss > best_improve_loss:  # 選出所有機台維修中，最好的一個維修時段
                best_index = m_index
                best_loss = m_cu_loss
                best_loss_list = m_loss_list
                best_schedule = m_schedule
                best_improve_loss = m_improve_loss
                best_m = machine_no
        
        if flag == 1:  # 維修會更好
            # print('能在資源限制下找到插入維修後更好的排程')
            # print('原先排程:', new_job_schedule)
            new_cu_loss[best_m] = best_loss
            new_loss[best_m][best_index:]= best_loss_list
            new_job_schedule[best_m][best_index:] = best_schedule
            # print('更新排程:', new_job_schedule)
            # print("更新的機台 ", best_m,'，loss = ', new_cu_loss[best_m],'維修時間 = ', best_time,"，進步 = ", best_improve_loss)
            # print('新的 loss :\n',new_loss)
    
    return new_cu_loss, new_loss, new_job_schedule

def alt_insert_maintenance(machine_no, time, machine_infos, job_list, m_loss, job_dic):  # 在某個時間點插入維修重新規劃後的結果
    
    pro_rate = machine_infos[machine_no][0]
    decrease_rate = machine_infos[machine_no][1]
    maintain_time = machine_infos[machine_no][2]
    # initial_yield_rate = machine_infos[machine_no][3]
    L_yield_rate = machine_infos[machine_no][4]/100*pro_rate
    new_loss = m_loss
    new_schedule = []
    new_loss_list = []

    # 加入最新維修
    new_schedule.append(('m', time, 0))
    new_loss_list.append(('m',new_loss))
    time += maintain_time
    init_yr = 100

    # 重排後面的工作
    for job_n,_,_ in job_list:
        if job_n == 'm':  # 如果之前有預計要維修，則安排維修
            new_schedule.append(('m', time, 0))
            new_loss_list.append(('m',new_loss))
            time += maintain_time
            init_yr = 100
        else:  # 重新安排工作
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

def alt_reschedule(time, init_yr, new_job, maintain_time, pro_rate, schedule, loss, decrease_rate, L_yield_rate, job_dic):  # 將工作重新排列後
    
    new_loss = loss
    new_loss_list = []
    new_schedule = []
    load = job_dic[new_job][0]
    due = job_dic[new_job][1]
    weight = job_dic[new_job][2]

    # 算新插入的交換工作
    new_schedule.append((new_job, time, init_yr))
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

    # 後面依序重新排工作
    for job_n,_,_ in schedule:
        if job_n == 'm':  # 如果之前有預計要維修，則安排維修
            new_schedule.append(('m', time, 0))
            new_loss_list.append(('m',new_loss))
            time += maintain_time
            init_yr = 100
        else:  # 重新安排工作
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



def calculate_schedule_score(job_schedule, machine_infos, job_dic):
    job_loss_list = {}
    job_cu_loss = {}
    for m, job_list in job_schedule.items():
        job_loss_list[m] = []
        time = 0
        cu_loss = 0
        pro_rate = machine_infos[m][0]
        decrease_rate = machine_infos[m][1]
        maintain_time = machine_infos[m][2]
        init_yr = machine_infos[m][3]
        L_yield_rate = machine_infos[m][4]/100*pro_rate
        for j, _, _ in job_list:
            if j == 'm':
                init_yr = 100
                time += maintain_time
            else:
                load = job_dic[j][0]
                due = job_dic[j][1]
                weight = job_dic[j][2]
                while load > 0 and time < due:  # 未完成訂單且未到 due day
                    rec_rate = (init_yr/100)*pro_rate
                    load -= rec_rate
                    if init_yr > L_yield_rate:
                        init_yr -= decrease_rate
                        if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                            init_yr = L_yield_rate
                    time += 1
                if load > 0:
                    cu_loss += load *weight
                job_loss_list[m].append((j,cu_loss))
        job_cu_loss[m] = cu_loss
    return job_cu_loss, job_loss_list