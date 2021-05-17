from functions_change import *
from tqdm import tqdm 
import itertools
from feasible_check import *

# Tabu 
def Tabu_alt(h, tabu_size, loop, cross_level, cross_machine, base_maint_loss, job_schedule, loss, cu_loss, job_dic, machine_infos, message_na):

    swtich_range = 5
    tabu_list = []
    job_schedule, loss, cu_loss = remove_maintenance(job_schedule, job_dic, machine_infos)
    
    # 畫圖用
    target_list = []
    schedule_list = []
    
    # best_job_schedule: 目前找到最好的維修排成方案。先將原本排程方案指定為目前最好的維修排程方案。
    best_job_schedule = copy.deepcopy(job_schedule)
    best_cu_loss = copy.deepcopy(cu_loss)
    best_loss = copy.deepcopy(loss)

    # 紀錄還沒換過的維修方案中的最好維修方案，作為下次交換的排程基準
    # (因為不能重複的用最好的解交換，所以需要另外紀錄)
    swap_job_schedule = copy.deepcopy(job_schedule)
    swap_cu_loss = copy.deepcopy(cu_loss)
    swap_loss = copy.deepcopy(loss)
    
    if message_na:
        print("正在用改版找出所有 neighbbor 的 Tabu search 找出更好的排程，一共執行 %d 次迴圈 ：" % loop)
        print("鄰居的交換 range 設定為：", swtich_range)
    for i in range(loop):  # 一共需要重複找 neighbor loop 次
        simple_sche = simple_schedule(swap_job_schedule)
        if message_na:
            print("正在執行第 %d 次迴圈 ：" % i)

        # 找出要交換的鄰居
        neighbor_pair = []
        if cross_machine == True:  # 會跟其他 machine 交換
            # 將工作分層(level)，並記錄各 jobs 的 neighboring jobs
            job_level, max_level = find_job_level(swap_job_schedule)            
            # 不跨 level 的交換範圍只有同 level 的
            for l in range(max_level-1):
                neighbor_pair.extend(list(itertools.combinations(job_level[l], 2)))  # 每個 level 內的工作彼此交換
            # 要跨 level
            if cross_level == True:
                for l in range(max_level-1):
                    for m in range(len(job_level[l])):
                        recent_job = job_level[l][m]    
                        for i in range(swtich_range):
                            if len(job_level) > l+i+1:  # 交換範圍不超過 job_level
                                for job in job_level[l+i+1]:
                                    neighbor_pair.append((recent_job, job))
        else:  # 不會跟其他 machine 交換
            for l in range(len(simple_sche)-1):
                neighbor_pair.extend(list(itertools.combinations(simple_sche[l], 2)))  # 每台 machine 內的工作彼此交換
                     
        flag = 0 # 表示第一次找 neighbor，還沒有初始基準
        # if message_na:
            # print("鄰居 list = ",neighbor_pair)
            # print("neighbor 基準參考 (基準會做為 tabu list 內紀錄的解) = ", simple_sche)
        for (job_1,job_2) in neighbor_pair:  # 更新所有的 neightboring pair
            # print("正在交換...",(job_1,job_2))
            new_simple_shce =  new_simple(job_1, job_2, simple_sche)
            # 開始進行鄰居工作交換
            if new_simple_shce not in tabu_list:
                # temp_job_schedule: 紀錄每次交換後的資料
                # best_temp_job_schedule: 紀錄所有交換後最好的資料，最後會被更新到下次的 swap_job_schedule 內作為下一階段的交換基準
                temp_job_schedule = copy.deepcopy(swap_job_schedule)
                temp_cu_loss = copy.deepcopy(swap_cu_loss)
                temp_loss = copy.deepcopy(swap_loss)
                
                # 找出要交換的工作機台並重新規劃
                for machine in temp_job_schedule.keys():
                    pro_rate = machine_infos[machine][0]
                    decrease_rate = machine_infos[machine][1]
                    maintain_time = machine_infos[machine][2]
                    # initial_yield_rate = machine_infos[machine][3]
                    L_yield_rate = machine_infos[machine][4]/100*pro_rate
                    for index,(job_n, t, init_yr) in enumerate(swap_job_schedule[machine]):
                        if job_n == job_1:
                            machine_1 = machine 
                            index_1 = index 
                            if index_1 == 0:
                                before_loss = 0
                            else:
                                before_loss = swap_loss[machine][index-1][1]
                            new_loss_list_1, new_loss_1, new_schedule_1 = \
                                alt_reschedule(t, init_yr, job_2, maintain_time, pro_rate, swap_job_schedule[machine][index+1:],
                                before_loss, decrease_rate, L_yield_rate, job_dic)

                        elif job_n == job_2:
                            machine_2 = machine 
                            index_2 = index 
                            if index_2 == 0:
                                before_loss = 0
                            else:
                                before_loss = swap_loss[machine][index-1][1]
                            new_loss_list_2, new_loss_2, new_schedule_2 = \
                                alt_reschedule(t, init_yr, job_1, maintain_time, pro_rate, swap_job_schedule[machine][index+1:],
                                before_loss, decrease_rate, L_yield_rate, job_dic)
                        index += 1
                # 將交換排程紀錄下來
                temp_loss[machine_1][index_1:] = new_loss_list_1 
                temp_loss[machine_2][index_2:] = new_loss_list_2
                temp_cu_loss[machine_1] = new_loss_1
                temp_cu_loss[machine_2] = new_loss_2
                temp_job_schedule[machine_1][index_1:] = new_schedule_1 
                temp_job_schedule[machine_2][index_2:] = new_schedule_2

                if machine_1 == machine_2:  # 同機台的工作要重新算，因為後面交換的時候還沒考慮到前面換的影響
                    check_job_schedule = []
                    check_loss_list = []
                    check_loss = 0
                    time = 0
                    pro_rate = machine_infos[machine_1][0]
                    decrease_rate = machine_infos[machine_1][1]
                    maintain_time = machine_infos[machine_1][2]
                    initial_yield_rate = machine_infos[machine_1][3]
                    L_yield_rate = machine_infos[machine_1][4]/100*pro_rate
                    init_yr = initial_yield_rate
                    for job_n,_,_ in temp_job_schedule[machine_1]:
                        if job_n == 'm':  # 如果之前有預計要維修，則安排維修
                            check_job_schedule.append(('m', time, 0))
                            check_loss_list.append(('m',check_loss))
                            time += maintain_time
                            init_yr = 100
                        else:  # 重新安排工作
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

                # print("交換後維修前的排程:\n",temp_job_schedule)
                # print("交換後維修前的 loss:\n",temp_loss)
                
                # 插入維修
                temp_new_cu_loss, temp_new_loss, temp_new_job_schedule = \
                    alt_decide_maintenance(machine_infos, temp_job_schedule, temp_cu_loss, temp_loss, h, job_dic)
                # print("交換後維修後的排程:\n",temp_new_job_schedule)
                # print("交換後維修後的 loss:\n",temp_new_loss)
                
                # 記錄最好且尚未記錄過的 schedule
                if simple_schedule(temp_job_schedule) not in tabu_list:
                    if flag == 0 :  # 表示第一個出現沒紀錄過的交換結果
                        flag = 1
                        best_temp_job_schedule = copy.deepcopy(temp_job_schedule)
                        best_temp_cu_loss = copy.deepcopy(temp_cu_loss)
                        best_temp_loss = copy.deepcopy(temp_loss)
                        best_temp_maint_loss = sum(temp_new_cu_loss.values())
                        # best_pair = (job_1, job_2)
                    
                    # 比先前沒有換過的結果更好，則更新為這次交換後的為最好結果
                    elif sum(temp_new_cu_loss.values()) < best_temp_maint_loss:
                        # 更新排程資訊
                        # print("交換後會更好的 job = ",(job_1,job_2))
                        # print("有維修的 schedule = ",temp_new_job_schedule)
                        # print("沒有維修的 schedule = ",temp_job_schedule)
                        best_temp_maint_loss = sum(temp_new_cu_loss.values())
                        best_temp_loss = temp_loss
                        best_temp_cu_loss = temp_cu_loss
                        best_temp_job_schedule = temp_job_schedule
                    
        # 更新最好的交換方案到 swap_job_schedule
        if flag == 0:
            print("所有交換可能已經都換過了!")
            break
        else:
            # 畫圖用
            target_list.append(sum(best_temp_cu_loss.values()))
            schedule_list.append(best_temp_job_schedule)
            # 更新 swap job schedule
            swap_loss = best_temp_loss
            swap_job_schedule = best_temp_job_schedule
            swap_cu_loss = best_temp_cu_loss

            # 更新 tabu list 資訊
            # tabu_list.append((best_pair[0],best_pair[1]))
            tabu_list.append(simple_schedule(best_temp_job_schedule))
            if len(tabu_list) > tabu_size:
                tabu_list.pop(0) 
            
            # 更新 best job schedule
            if  best_temp_maint_loss < base_maint_loss:
                print("improve! loss = ", best_temp_maint_loss)
                # 更新排程資訊
                base_maint_loss = best_temp_maint_loss
                best_loss = best_temp_loss
                best_job_schedule = best_temp_job_schedule
                best_cu_loss = best_temp_cu_loss
            
    if message_na:
        print("Tabu 後維修前的排程 job schedule:", best_job_schedule)
        print("Tabu 後維修前的 production loss：\n':", best_loss)
        print("Tabu 後維修前的各機台累積 loss: \n':", best_cu_loss)

    # 把最好的排程找維修決策
    best_maint_cu_loss, best_maint_loss, best_maint_job_schedule = \
        alt_decide_maintenance(machine_infos, best_job_schedule, best_cu_loss, best_loss, h, job_dic)
    if message_na:
        print('Tabu 後產生排程 job schedule：\n',best_maint_job_schedule)
        print('Tabu 後的 production loss：\n', best_maint_loss)
        print('各機台累積 loss:', best_maint_cu_loss)
        print('Tabu 後的總 production loss：\n',sum(best_maint_cu_loss.values()))
    tabu_obj = sum(best_maint_cu_loss.values())
    
    # print("check tabu:\n")
    total_flag = feasible_check(best_maint_job_schedule, machine_infos, job_dic, tabu_obj, h, message_na)

    return tabu_obj, total_flag
