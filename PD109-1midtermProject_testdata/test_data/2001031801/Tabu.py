from functions import *
from tqdm import tqdm 
import itertools

# Tabu 
def Tabu(h, tabu_size, loop, cross_order, cross_machine, maintain_time, base_maint_tard, job_schedule, pro_rate, tardiness, decrease_rate, L_yield_rate, cu_tard, maint_sche, job_dic):

    tabu_list = []
    best_job_schedule = copy.deepcopy(job_schedule)
    best_cu_tard = copy.deepcopy(cu_tard)
    best_tardiness = copy.deepcopy(tardiness)
    best_maint_sche = copy.deepcopy(maint_sche)

    # 將工作分層(order)
    print("正在用改版找出所有 neighbbor 的 Tabu search 找出更好的排程，一共執行 %d 次迴圈 ：" % loop)
    swap_job_schedule = copy.deepcopy(job_schedule)
    swap_cu_tard = copy.deepcopy(cu_tard)
    swap_tardiness = copy.deepcopy(tardiness)
    target_list = []
    schedule_list = []
    for i in range(loop):  # 一共需要重複找 neighbor loop 次
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
                # print("可試試看的 neighbor = ", new_simple_shce)
                temp_job_schedule = copy.deepcopy(swap_job_schedule)
                temp_cu_tard = copy.deepcopy(swap_cu_tard)
                temp_tardiness = copy.deepcopy(swap_tardiness)
                for i in range(len(job_schedule)):  # 找出要交換的工作機台時間位址並重新規劃
                    machine = i+1
                    index = 0
                    for job_n, t, init_yr in swap_job_schedule[machine]:
                        if job_n == job_1:
                            machine_1 = machine 
                            index_1 = index 
                            if index_1 == 0:
                                before_tard = 0
                            else:
                                before_tard = swap_tardiness[machine][index-1][1]
                            new_tardiness_list_1, new_tard_1, new_schedule_1 = \
                                reschedule(t, init_yr, job_2, pro_rate[machine], swap_job_schedule[machine][index+1:],
                                before_tard, decrease_rate[machine], L_yield_rate[machine], job_dic)

                        elif job_n == job_2:
                            machine_2 = machine 
                            index_2 = index 
                            if index_2 == 0:
                                before_tard = 0
                            else:
                                before_tard = swap_tardiness[machine][index-1][1]
                            new_tardiness_list_2, new_tard_2, new_schedule_2 = \
                                reschedule(t, init_yr, job_1, pro_rate[machine], swap_job_schedule[machine][index+1:],
                                before_tard, decrease_rate[machine], L_yield_rate[machine], job_dic)
                        index += 1
                # 將交換排程紀錄下來
                temp_tardiness[machine_1][index_1:] = new_tardiness_list_1 
                temp_tardiness[machine_2][index_2:] = new_tardiness_list_2
                temp_cu_tard[machine_1] = new_tard_1
                temp_cu_tard[machine_2] = new_tard_2
                temp_job_schedule[machine_1][index_1:] = new_schedule_1 
                temp_job_schedule[machine_2][index_2:] = new_schedule_2 
                               
                # 插入維修
                temp_maint_sche, temp_new_cu_tard, temp_new_tardiness, temp_new_job_schedule = \
                    decide_maintenance(decrease_rate, temp_job_schedule, temp_cu_tard, temp_tardiness, h, pro_rate, maintain_time, job_dic, L_yield_rate)
                # 記錄最好的 neighborhood schedule
                if flag == 0 :  # 表示第一個 neighborhood
                    flag = 1
                    best_temp_job_schedule = copy.deepcopy(temp_job_schedule)
                    best_temp_cu_tard = copy.deepcopy(temp_cu_tard)
                    best_temp_tardiness = copy.deepcopy(temp_tardiness)
                    best_temp_maint_tard = sum(temp_new_cu_tard.values())
                    best_pair = (job_1, job_2)
                elif sum(temp_new_cu_tard.values()) < best_temp_maint_tard:
                    # 更新排程資訊
                    # print("交換後會更好的 job = ",(job_1,job_2))
                    # print("schedule = ",temp_job_schedule)
                    best_temp_maint_tard = sum(temp_new_cu_tard.values())
                    best_temp_tardiness = temp_tardiness
                    best_temp_cu_tard = temp_cu_tard
                    best_temp_job_schedule = temp_job_schedule
                    best_pair = (job_1, job_2)
        # 更新最好的 neighborhood
        target_list.append(sum(best_temp_cu_tard.values()))
        schedule_list.append(best_temp_job_schedule)
        swap_tardiness = best_temp_tardiness
        swap_job_schedule = best_temp_job_schedule
        swap_cu_tard = best_temp_cu_tard
        # 沒看過，更新 tabu list 資訊
        # tabu_list.append((best_pair[0],best_pair[1]))
        tabu_list.append(simple_schedule(best_temp_job_schedule))
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0) 
        if  best_temp_maint_tard < base_maint_tard:  # 表示新的交換有進步，則更新排程
            print("improve! tardiness = ", best_temp_maint_tard)
            # 更新排程資訊
            base_maint_tard = best_temp_maint_tard
            best_tardiness = best_temp_tardiness
            best_job_schedule = best_temp_job_schedule
            best_cu_tard = best_temp_cu_tard
            

    # 把最好的排程找維修決策
    best_maint_sche, best_maint_cu_tard, best_maint_tardiness, best_maint_job_schedule = \
        decide_maintenance(decrease_rate, best_job_schedule, best_cu_tard, best_tardiness, h, pro_rate, maintain_time, job_dic, L_yield_rate)
    print('產生排程：\n',best_maint_job_schedule)
    print('產生維修時程：\n',best_maint_sche)
    print('Tabu 後的總 tardiness：\n',sum(best_maint_cu_tard.values()))
    tabu_obj = sum(best_maint_cu_tard.values())

    return tabu_obj, target_list, schedule_list, tabu_list