from gurobipy import*
import numpy as np
import pandas as pd
from pathlib import Path

def das_model(file_num = 0, factors_list={}, type=[], folder_name = "testdata", result_name = "result", run_time = 600, show_result = False):

    path_name = result_name + "/relax_model"
    Path(path_name).mkdir(parents=True, exist_ok=True)

    for factor in factors_list.values():
        # final = open(result_name + "/m" + str(m) + "result_ip_relax_y_dict.txt", "w+")
        
        # # 寫檔案
        # final.write('name runtime gap objectives \n')

        for t in type:

            final_df = pd.DataFrame(columns=['factor', 'type', 'index', 'runtime', 'gap', 'objectives'])
            # 讀取規模
            # prefix = "m"+str(m)+"n"+str(n)+"_" # problem 編號
            prefix = factor + '_' + t  # problem 編號
            file_list = [str(i+1) for i in range(file_num)]

            A_i = {}
            B_i = {}
            F_i = {}
            r_i0 = {}
            L_i = {}
            Q_j = {}
            D_j = {}

            for index in file_list:

                # 讀取同規模的測資
                f = open(folder_name + "/" + prefix + "/" + prefix + '_' + index + ".txt", "r")
                first_line = f.readline().split()

                #=================== 資料部分 ===================#
                M = range(1, int(first_line[0]) + 1)  # set of indices of machines i
                N = range(1, int(first_line[1]) + 1)   # set of indices of orders j, k
                # H = int(first_line[2])    # 0113修正
                for i in M:
               
                    line = f.readline().split()
                    A_i[i] = float(line[0])
                    B_i[i] = float(line[1])/100
                    F_i[i] = int(line[2])
                    r_i0[i] = float(line[3])/100
                    L_i[i] = float(line[4])/100

                for j in N:

                    line = f.readline().split()
                    Q_j[j] = float(line[0])
                    D_j[j] = int(line[1])

                f.close()
                T = range(1, 101)

                #================== 模型部分 ==================#
                # 建立模型
                eg1 = Model("model")  # build a new model, name it as "model"

                # 設定時間
                eg1.setParam('TimeLimit', run_time) # second
             
                # 定義決策變數

                ## yield rate at time period t on machine i
                r_it = eg1.addVars(M, T, vtype=GRB.CONTINUOUS, lb=0, ub=1)

                ## whether it is the first time period after mainmenance at time period t on machine i
                e_it = eg1.addVars(M, T, vtype=GRB.BINARY)
                
                ## whether it is the first time period after mainmenance at time period t on machine i
                c_it = eg1.addVars(M, T, vtype=GRB.BINARY)
                                
                ## completion time of order j
                w_j = eg1.addVars(N, vtype=GRB.CONTINUOUS, lb=0)

                ## maximum completion time of order j
                p_j = eg1.addVars(N, vtype=GRB.CONTINUOUS, lb=0)

                ## whether machine i is during maintenance at time period t
                x_it = eg1.addVars(M, T, vtype=GRB.BINARY)
                                
                ## order j is completed by machine i
                z_ij = eg1.addVars(M, N, vtype=GRB.BINARY)

                ## order j is proccessed by machine at time period t
                g_ijt = eg1.addVars(M, N, T, vtype=GRB.CONTINUOUS, lb=0)

                ## whether yield rate at next time period will be lower than the lower bound
                s_it = eg1.addVars(M, T, vtype=GRB.BINARY)
                                
                ## order j is completed at time period t on machine i
                u_jt = eg1.addVars(N, T, vtype=GRB.BINARY)


                # 0119 add
                y_ijt = eg1.addVars(M, N, T, vtype=GRB.BINARY)
                                        
                # 定義目標變數

                eg1.setObjective((quicksum(p_j[j] for j in N)), GRB.MINIMIZE)

                # 定義限制式  

                # 0119 add z
                eg1.addConstrs(quicksum(g_ijt[i,j,t] for t in T) <= Q_j[j] * z_ij[i,j] for i in M for j in N)
                eg1.addConstrs(quicksum(z_ij[i,j] for i in M) == 1 for j in N)

                # 0119 add y
                eg1.addConstrs(g_ijt[i,j,t] <= A_i[i] * y_ijt[i,j,t] for i in M for j in N for t in T)
                eg1.addConstrs(quicksum(y_ijt[i,j,t] for j in N) <= 1 for i in M for t in T)

                ## order fulfillment
                eg1.addConstrs((quicksum(g_ijt[i,j,t] for i in M for t in T) >= Q_j[j] for j in N), "orderFulfillment")

                ## produced quantity: define g_ijt - 1       
                eg1.addConstrs((quicksum(g_ijt[i,j,t] for j in N) <= A_i[i] * r_it[i,t] for i in M for t in T), "producedQuantity1")

                ## produced quantity: define g_ijt - 2
                M_2 = max(A_i)
                eg1.addConstrs((quicksum(g_ijt[i,j,t] for j in N) <= A_i[i] * (1 - x_it[i,t]) for i in M for t in T), "producedQuantity2")
            
                ## define yield lower bound - 1
                M_3 = 1
                M_4 = 1             
                eg1.addConstrs((r_it[i,T[0]] <= M_3 * e_it[i,T[0]] + M_4 * s_it[i,T[0]] - B_i[i] for i in M), "yieldLB1")
                eg1.addConstrs((r_it[i,t] <= M_3 * e_it[i,t] + M_4 * s_it[i,t] + r_it[i,t-1] - B_i[i] for i in M for t in T[1:]), "yieldLB2")

                ## define yield lower bound - 2
                M_5 = 1
                eg1.addConstrs((r_it[i,t] <= M_3 * e_it[i,t] + M_5 * (1 - s_it[i,t]) + L_i[i] for i in M for t in T), "yieldLB3")

                ## completion time
                eg1.addConstrs((1 + t * u_jt[j,t] <= w_j[j] for j in N for t in T), "completionTime")

                ## define a lot of complete time
                eg1.addConstrs((Q_j[j] - quicksum(g_ijt[i,j,t_p] for i in M for t_p in range(1,t+1)) <= Q_j[j] * u_jt[j,t] for j in N for t in T), "Define end time1" )
                eg1.addConstrs((e_it[i,t] * 2 <=  x_it[i,t-1] - x_it[i,t] + 1 for i in M for t in T[1:]), "Define end time2")
                eg1.addConstrs((e_it[i,T[0]] * 2 <=  - x_it[i,T[0]] + 1 for i in M), "Define end time3")

                ## repairment continue
                eg1.addConstrs((F_i[i] - quicksum(x_it[i,l] for l in range(t-F_i[i],t)) <= F_i[i] * (1 - e_it[i,t]) for i in M for t in T[F_i[i]:]), "repairContinue")

                ## define maximum completion time
                eg1.addConstrs((p_j[j]>= w_j[j] - D_j[j] for j in N), "maximumCompletionTime1")

                # run Gurobi
                eg1.optimize()

                # show result
                print("The run time is %f" % eg1.Runtime)
                # final gap
                # 給我存 lower bound !!!!! 0119
                if eg1.Runtime > run_time:
                    print("Final MIP gap value: %f" % eg1.MIPGap)           

                name = prefix + index

                # 寫檔案
                if eg1.Runtime > run_time:
                    final_df = final_df.append({'factor': factor, 'type': t, 'index': str(index), 'runtime':str(eg1.Runtime), 'gap': str(eg1.MIPGap) , 'objectives': str(eg1.objVal)} , ignore_index=True)
                    # final.write(name + " " + str(eg1.Runtime) + " " + str(eg1.MIPGap) + " " + str(eg1.objVal) + "\n")
                else:
                    final_df = final_df.append({'factor': factor, 'type': t, 'index': str(index), 'runtime':str(eg1.Runtime), 'gap': '-' , 'objectives': str(eg1.objVal)} , ignore_index=True)    

            # final.close()
            with pd.ExcelWriter(result_name + "/relax_model/" + prefix + ".xlsx", engine="openpyxl", mode='w') as writer:
                final_df.to_excel(writer)

        # show the result

        if show_result:          
            print("\n\n Model Result:")
            print("\n")
            
            # # sum_j
            # print("sum_j")
            # total_sum = []
            # for j in N:
            #     total_sum.append(Q_j[j] - sum(g_ijt[i,j,t].x for i in M for t in range(1,D_j[j]+1)))
            # df_total_demand = pd.DataFrame(total_sum).transpose()
            # print(df_total_demand)          
            # df_total_demand.columns = range(1,len(N)+1)
            # df_total_demand.index = ["Order"]
            # print("\n")
            
            # # w_j
            # print("w_j")
            # total_demand = []
            # order_name = []
            # for j in N:
            #     try:
            #         total_demand.append(round(w_j[j].x))
            #     except:
            #         total_demand.append(0)
            # df_total_demand = pd.DataFrame(total_demand).transpose()
            # df_total_demand.columns = range(1,len(N)+1)
            # df_total_demand.index = ["Order"]
            # print(df_total_demand)
            # print("\n")

            # ## z_ij
            # print("z_ij")
            # print("\tOrder")   # head of the result table
            # for i in M:
            #     print("Machine" + str(i), "\t", end="") # mark which item is printed now
            #     for j in N:
            #         try:
            #             print(round(z_ij[i,j].x), "\t", end="") # print qty of each kind of item
            #         except:
            #             print(0, "\t", end="")
            #     print("")  # use for change line
            # print("\n")

            # ## u_jt
            # print("u_jt")
            # print("\tTime")   # head of the result table
            # for j in N:
            #     print("Order" + str(j), "\t", end="") # mark which item is printed now
            #     for t in T:
            #         try:
            #             print(round(u_jt[j,t].x), "\t", end="") # print qty of each kind of item
            #         except:
            #             print(0, "\t", end="")
            #     print("")  # use for change line
            # print("\n")

            # ## x_it
            # print("x_it")
            # print("\tTime")   # head of the result table
            # for i in M:
            #     print("Machine" + str(i), "\t", end="") # mark which item is printed now
            #     for t in T:
            #         try:
            #             print(round(x_it[i,t].x), "\t", end="") # print qty of each kind of item
            #         except:
            #             print(0, "\t", end="")
            #     print("")  # use for change line
            # print("\n")

            # ## e_it
            # print("e_it")
            # print("\tTime")   # head of the result table
            # for i in M:
            #     print("Machine" + str(i), "\t", end="") # mark which item is printed now
            #     for t in T:
            #         try:
            #             print(round(e_it[i,t].x), "\t", end="") # print qty of each kind of item
            #         except:
            #             print(0, "\t", end="")
            #     print("")  # use for change line
            # print("\n")

            ## g_ijt

            print("g_ijt (Order : Amount)")
            define_len = 5
            loop_count = math.ceil(len(T) / define_len)
            
            for loop_index in range(loop_count):
                total_machine = []
                for i in M:
                    total_row = []
                    for t in T[loop_index*define_len:min((loop_index+1)*define_len,len(T))]:
                        row = " "
                        found = False
                        for j in N:
                            try:
                                if g_ijt[i,j,t].x > 0:
                                    if not found:
                                        row += str(j) + ":" + str(round(g_ijt[i,j,t].x))
                                    elif j <= define_len-1:
                                        row += " " + str(j) + ":" + str(round(g_ijt[i,j,t].x))
                                    else:
                                        row += " " + str(j) + ":" + str(round(g_ijt[i,j,t].x))
                                    found = True
                                    continue
                            except:
                                continue
                        if not found:
                            try:
                                if x_it[i,t].x:
                                    if x_it[i,t].x == 1:
                                        row += 'M'
                            except:
                                continue
                        total_row.append(row)
                    total_machine.append(total_row)

                df_total_machine = pd.DataFrame(total_machine)

                list_time = []
                for i in range(loop_index*define_len+1,min((loop_index+1)*define_len,len(T))+1):
                    list_time.append("Time" + str(i))
                print(list_time)
                print(df_total_machine)
                df_total_machine.columns = list_time             
                
                list_machine = []
                for i in M:
                    list_machine.append("Machine" + str(i))
                df_total_machine.index = list_machine

                print(df_total_machine)
                print('\n')

            # objective value
            print("objective value")
            print("z* = ", eg1.objVal)  # print objective value
