from functions import *

def feasible_check(job_schedule, machine_infos, job_dic, loss, h):
    check_job_schedule = {}
    check_loss_list = {}
    check_loss = {}
    for m in job_schedule.keys():
        time = 0
        pro_rate = machine_infos[m][0]
        decrease_rate = machine_infos[m][1]
        initial_yield_rate = machine_infos[m][3]
        L_yield_rate = machine_infos[m][4]
        init_yr = initial_yield_rate
        check_job_schedule[m] = []
        check_loss_list[m] = []
        check_loss[m] = 0
        for job_n,_,_ in job_schedule[m]:
            load = job_dic[job_n][0]
            due = job_dic[job_n][1]
            weight = job_dic[job_n][2]
            check_job_schedule[m].append((job_n, time, init_yr))
            while load > 0 and time < due:  # 未完成訂單且未到 due day
                rec_rate = (init_yr/100)*pro_rate
                load -= rec_rate
                if init_yr > L_yield_rate:
                    init_yr -= decrease_rate
                    if init_yr < L_yield_rate:  # 不能低於良率 lower bound
                        init_yr = L_yield_rate
                time += 1
            if load > 0:  # 未滿足交期
                check_loss[m] += load*weight  # 只有太晚做完才要算 cost
            check_loss_list[m].append((job_n,check_loss[m]))
        
        # 插入維修
        check_maint_sche, check_new_cu_loss, check_new_loss, check_new_job_schedule = \
            alt_decide_maintenance(machine_infos, check_job_schedule, check_loss, check_loss_list, h, job_dic)

        # 判斷工作會不會重複
        flag = 1
        work_set = set()
        for m in check_new_job_schedule.keys():
            for j,_,_ in check_new_job_schedule[m]:
                work_set.add(j)
        for i in range(1,len(job_dic)+1):
            if i not in work_set:
                flag == 0

    if loss == sum(check_new_cu_loss.values()) and flag == 1:
        print("tabu 算的：",loss)
        print("feasible check 的：",sum(check_new_cu_loss.values()))
        print("是否(1/0)所有工作都排到：",flag)
        return True
    else:
        print("tabu 算的 loss：", loss)
        print("feasible check 的 loss：",sum(check_new_cu_loss.values()))
        print("feasible check 的 schedule：",check_new_job_schedule)
        print("是否(1/0)所有工作都排到：",flag)
        return False
