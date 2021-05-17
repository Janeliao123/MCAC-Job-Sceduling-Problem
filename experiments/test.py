from functions_change import *
#In[]
machine_no = 1
time = 0
# [生產速率, 下降速率, 維修時間, 初始良率, 良率下限]
machine_infos = {1:[100, 5, 1, 90, 60], 2:[100, 1, 1, 90, 60]}
job_list = {(1,0,90),(2,)}
# job_dic[job 編號] = [訂購量, 交期, 權重]
job_dic = {1:[300,3,5],2:[400,5,2],3:[500,5,3]}
work_load = 
for j in job_dic.keys():

alt_decide_maintenance(machine_infos, job_schedule, cu_loss, loss, h, job_dic)