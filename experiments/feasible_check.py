from functions_change import *

def feasible_check(job_schedule, machine_infos, job_dic, loss, h, message_na):
    total_flag = 0
    # 檢查維修排程是否正常
    check_job_schedule = {}
    check_loss_list = {}
    check_loss = {}
    main_time = {}
    for m, job_list in job_schedule.items():
        time = 0
        pro_rate = machine_infos[m][0]
        decrease_rate = machine_infos[m][1]
        maintain_time = machine_infos[m][2]
        initial_yield_rate = machine_infos[m][3]
        L_yield_rate = machine_infos[m][4]/100*pro_rate
        init_yr = initial_yield_rate
        check_job_schedule[m] = []
        check_loss_list[m] = []
        check_loss[m] = 0
        for job_n,t,yr in job_list:
            if job_n == 'm':
                if t not in main_time:
                    main_time[t] = 0
                else:
                    main_time[t] += 1
                init_yr = 100
                time += maintain_time
                check_loss_list[m].append(('m',check_loss[m]))
                check_job_schedule[m].append(('m', time, init_yr))
            else:
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

    if loss == sum(check_loss.values()):
        if message_na:
            print("+++ pass +++")
            print("heuristic algorithm 算的 loss：",loss)
            print("feasible check 的：",sum(check_loss.values()))
    else:
        total_flag = 1
        if message_na:
            print("!!! error !!!")
            print("heuristic algorithm 算的 loss：", loss)
            print("feasible check 的 loss：",sum(check_loss.values()))
            print("heuristic algorithm 算的 schedule：", job_schedule)
            print("feasible check 的 schedule：",check_job_schedule)   
    
    # 檢查工作會不會重複
    flag = 1
    work_set = []
    for m, job_list in check_job_schedule.items():
        for j,_,_ in job_list:
            if j != 'm':
                if j in work_set:
                    total_flag = 1
                    if message_na:
                        print("!!! error !!!")
                        print("重複排到一樣的工作。")
                else:
                    work_set.append(j)
    for i in range(1,len(job_dic)+1):
        if i not in work_set:
            flag == 0
    
    if flag == 1:
        if message_na:
            print("+++ pass +++")
            print("所有工作都排到。")
    else:
        total_flag = 1
        if message_na:
            print("!!! error !!!")
            print("有工作沒被排到。")

    # 檢查同時間沒有維修超過 h 台
        for k, v in main_time.items():
            if v > h:
                total_flag = 1
                if message_na:
                    print("!!! error !!!")
                    print("在" + str(t) + "時同時修超過" + str(h) + "台")

    return total_flag