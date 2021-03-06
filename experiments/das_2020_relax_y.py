# -*- coding: utf-8 -*-
"""DAS_2020_yield.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ezs5nXya3oNEM8RFCHnFOMoR37SoOECW
"""

from gurobipy import*
#import all functions in gurobipy

"""## **12/23 formulation**

### data
"""
def das_model(file_num = 0, m_list = [], n_list = [], folder_name = "testdata", result_name = "result", run_time = 600, optional = True, show_result = False):
    result_list = [] # runtime / gap

    # file_num = 10 - 0106修正
    # file_num = 1
    # m_list = [1, 3, 5] - 0106修正
    # m_list = [5]
    # n_list = [5, 10, 15] - 0106修正
    # n_list = [50]
    # folder_name = "test_data/stage1/1230_good" - 0106修正
    # folder_name = "testdata"
    # m = 5
    # n = 5

    for m in m_list: # - 0106修正
        if optional:
            final = open(result_name + "/m" + str(m) + "result_ip_relax_y_opt.txt", "w+")
        else:
            final = open(result_name + "/m" + str(m) + "result_ip_relax_y.txt", "w+")
        
        # 寫檔案
        final.write('name runtime gap objectives \n')

        for n in n_list:
            prefix = "m"+str(m)+"n"+str(n)+"_" # problem 編號

            file_list = [str(i+1) for i in range(file_num)]

            for index in file_list:
                f = open(folder_name + "/" + prefix + index + ".txt", "r")


    # f = open('test_data/stage1/1230_good/m3n10_1.txt', 'r')
    # f = open('smallTestData.txt', 'r')

                first_line = f.readline().split()

                #=================== data part ===================#
                # indices（記得加一）
                M = range(int(first_line[0]) + 1)  # set of indices of machines i
                N = range(int(first_line[1]) + 1)   # set of indices of orders j, k
                # H = int(first_line[2])    # 0113修正
                for i in M:

                    if i == 0:
                        A_i = [0]
                        B_i = [0]
                        F_i = [0]
                        r_i0 = [0]
                        L_i = [0]
                    else:
                        line = f.readline().split()
                        A_i.append(float(line[0]))
                        B_i.append(float(line[1])/100)
                        F_i.append(int(line[2]))
                        r_i0.append(float(line[3])/100)
                        L_i.append(float(line[4])/100)


                for j in N:

                    if j == 0:
                        Q_j = [0]
                        D_j = [0]
                    else:
                        line = f.readline().split()
                        Q_j.append(float(line[0]))
                        D_j.append(int(line[1]))

                f.close()
                # 時間 T: 訂單量/(所有機台的平均 Li *原本生產量Aij)
                # T = range(round(sum(Q_j) / (0.75 * 200)))  # set of indices of time period t
                T = range(101)

                # #=================== data part ===================#
                # # indices（記得加一）
                # M = range(5+1)  # set of indices of machines i
                # N = range(3+1)   # set of indices of orders j, k
                # T = range(1000+1)  # set of indices of time period t

                # # parameter（第一個位置補0）
                # A_i = [0, 10, 15, 15, 20, 25]   # ideal production rate of machine i
                # B_i = [0, 0.1, 0.2, 0.3, 0.1, 0.2]  # declining rate of yield on mahcine i
                # F_i = [0, 1, 2, 3, 2, 1]            # required maintenance time on machine i
                # L_i = [0, 0.3, 0.4, 0.3, 0.2, 0.3]  # lower bound of yield rate on machine i
                # Q_j = [0, 10, 8, 20]             # quantity of order j
                # D_j = [0, 5, 10, 20]                  # due date of order j
                # H = 2                            # maximum amount of maintenance

                # #=================== simple data part ===================#
                # # indices（記得加一）
                # M = range(1+1)  # set of indices of machines i
                # N = range(2+1)   # set of indices of orders j, k
                # T = range(1000+1)  # set of indices of time period t

                # # parameter（第一個位置補0）
                # A_i = [0, 10]   # ideal production rate of machine i
                # B_i = [0, 0.1]  # declining rate of yield on mahcine i
                # F_i = [0, 1]            # required maintenance time on machine i
                # L_i = [0, 0]  # lower bound of yield rate on machine i
                # Q_j = [0, 10, 8]             # quantity of order j
                # D_j = [0, 20, 20]                  # due date of order j
                # H = 2                            # maximum amount of maintenance

                """### model"""

                #================== model part ==================#
                # build a new model
                eg1 = Model("model")  # build a new model, name it as "model"

                # 設定時間
                # eg1.setParam('TimeLimit', 60*10) # second
                eg1.setParam('TimeLimit', run_time) # second
                # 顯示花費時間
                # runtime = eg1.Runtime

                # decision variable

                ## yield rate at time period t on machine i
                r_it = []
                for i in M:
                    if i == 0:
                        r_it.append([0] * len(T))
                    else:
                        r_it.append([])
                        for t in T:
                            if t == 0:
                                r_it[i].append(r_i0[i])  # 若起始良率不為1，這裡要改!
                            else:
                                r_it[i].append(eg1.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1))

                ## whether it is the first time period after mainmenance at time period t on machine i
                e_it = []
                for i in M:
                    if i == 0:
                        e_it.append([0] * len(T))
                    else:
                        e_it.append([])
                        for t in T:
                            if t == 0:
                                e_it[i].append(0)
                            else:
                                e_it[i].append(eg1.addVar(vtype=GRB.BINARY, lb=0))                          

                ## whether it is the first time period after mainmenance at time period t on machine i
                c_it = []
                for i in M:
                    if i == 0:
                        c_it.append([0] * len(T))
                    else:
                        c_it.append([])
                        for t in T:
                            if t == 0:
                                c_it[i].append(0)
                            else:                               
                                c_it[i].append(eg1.addVar(vtype=GRB.BINARY, lb=0))
                                
                ## constraint controller    # 0113修正  v拿掉
                # v_it = []
                # for i in M:
                #     if i == 0:
                #         v_it.append([0] * len(T))
                #     else:
                #         v_it.append([])
                #         for t in T:
                #             if t == 0:
                #                 v_it[i].append(0)
                #             else:
                #                 v_it[i].append(eg1.addVar(vtype=GRB.CONTINUOUS, lb=0))

                ## completion time of order j
                w_j = []
                for j in N:
                    if j == 0:
                        w_j.append(0)
                    else:                       
                        w_j.append(eg1.addVar(vtype=GRB.CONTINUOUS, lb=0))                    

                ## maximum completion time of order j
                p_j = []
                for j in N:
                    if j == 0:
                        p_j.append(0)
                    else:
                        p_j.append(eg1.addVar(vtype=GRB.CONTINUOUS, lb=0))
                        
                ## whether machine i is during maintenance at time period t
                x_it = []
                for i in M:
                    if i == 0:
                        x_it.append([0] * len(T))
                    else:
                        x_it.append([])
                        for t in T:
                            if t == 0:
                                x_it[i].append(0)
                            else:                              
                                x_it[i].append(eg1.addVar(vtype=GRB.BINARY))
                                
                ## order j is completed by machine i
                z_ij = []
                for i in M:
                    if i == 0:
                        z_ij.append([0] * len(N))
                    else:
                        z_ij.append([])
                        for j in N:
                            if j == 0:
                                z_ij[i].append(0)
                            else:
                                z_ij[i].append(eg1.addVar(vtype=GRB.BINARY))
                                
                ## order j is proccessed by machine at time period t
                y_ijt = []
                for i in M:
                    if i == 0:
                        y_ijt.append([[0] * len(T)] * len(N))
                    else:
                        y_ijt.append([])
                        for j in N:
                            if j == 0:
                                y_ijt[i].append([0] * len(T))
                            else:
                                y_ijt[i].append([])
                                for t in T:
                                    if t == 0:
                                        y_ijt[i][j].append(0)
                                    else:                                       
                                        y_ijt[i][j].append(eg1.addVar(vtype = GRB.CONTINUOUS, lb=0, ub=1)) # 0113修正
                                        
                # add dummy y_ij,t+1
                for i in M:
                    for j in N:
                        y_ijt[i][j].append(0)

                ## order j is proccessed by machine at time period t
                g_ijt = []
                for i in M:
                    if i == 0:
                        g_ijt.append([[0] * len(T)] * len(N))
                    else:
                        g_ijt.append([])
                        for j in N:
                            if j == 0:
                                g_ijt[i].append([0] * len(T))
                            else:
                                g_ijt[i].append([])
                                for t in T:
                                    if t == 0:
                                        g_ijt[i][j].append(0)
                                    else:
                                        g_ijt[i][j].append(eg1.addVar(vtype = GRB.CONTINUOUS, lb=0))

                ## whether yield rate at next time period will be lower than the lower bound
                s_it = []
                for i in M:
                    if i == 0:
                        s_it.append([0] * len(T))
                    else:
                        s_it.append([])
                        for t in T:
                            if t == 0:
                                s_it[i].append(0)
                            else:
                                s_it[i].append(eg1.addVar(vtype = GRB.BINARY))
                                
                ## order j is completed at time period t on machine i
                u_jt = []
                for j in N:
                    if j == 0:
                        u_jt.append([0] * len(T))
                    else:
                        u_jt.append([])
                        for t in T:
                            if t == 0:
                                u_jt[j].append(0)
                            else:                                       
                                u_jt[j].append(eg1.addVar(vtype = GRB.BINARY))
                                        
                # objective function
                # eg1.setObjective((quicksum(p_j[j] for j in N)+5), GRB.MINIMIZE)
                eg1.setObjective((quicksum(p_j[j] for j in N)), GRB.MINIMIZE)

                # add constraints and name them

                ## machine capacity at a time   # 0113修正
                # if optional:    
                #     for i in M:
                #         for t in T[1:]:
                #             eg1.addConstr(
                #                 quicksum(y_ijt[i][j][t] for j in N)
                #                 <= 1, "machineCapacityAtATime"
                #             )

                ## job assignment: with time    # 0113修正
                # for j in N:
                #     for t in T[1:]:
                #         eg1.addConstr(
                #             quicksum(y_ijt[i][j][t] for i in M)
                #             <= 1, "jobAssignment1"
                #         )

                ## job assignment: without time     # 0113修正
                # if optional:    
                #     for j in N[1:]:
                #         eg1.addConstr(
                #             quicksum(z_ij[i][j] for i in M)
                #             == 1, "jobAssignment2"
                #         )

                ## job assignment: define z_ij      # 0113修正
                # M_1 = 10000   
                # M_1 = len(T)
                # for i in M:   
                #     for j in N:
                #         eg1.addConstr(
                #             M_1 * z_ij[i][j]
                #             >= quicksum(y_ijt[i][j][t] for t in T), "jobAssignment3"
                #         )

                ## stop working during repairment       # 0113修正
                # for i in M:
                #     for t in T[1:]:
                #         eg1.addConstr(
                #             quicksum(y_ijt[i][j][t] for j in N)
                #             <= (1 - x_it[i][t]), "stopWorking"
                #         )

                ## repairment limit         # 0113修正 H直接拿掉
                # for t in T[1:]:
                #     eg1.addConstr(
                #         quicksum(x_it[i][t] for i in M)
                #         <= H, "repairLimit"
                #     )

                ## real processing rate: consider yield     # 0113修正  v拿掉
                # for i in M:
                #     for t in T[1:]:
                #         eg1.addConstr(
                #             v_it[i][t]
                #             == A_i[i] * r_it[i][t], "processingRate"
                #         )

                ## order fulfillment
                for j in N:
                    eg1.addConstr(
                        quicksum(g_ijt[i][j][t] for i in M for t in T)
                        >= Q_j[j], "orderFulfillment"
                    )

                ## produced quantity: define g_ijt         # 0113修正  用A*R取代v，j變sum
                for i in M:
                    for t in T[1:]:
                        eg1.addConstr(
                            quicksum(g_ijt[i][j][t] for j in N)
                            <= A_i[i] * r_it[i][t], "producedQuantity1"
                        )

                ## produced quantity: define g_ijt          # 0113修正  用A*R取代M2*y，j變sum
                M_2 = max(A_i)
                for i in M:
                    for t in T[1:]:
                        eg1.addConstr(
                            quicksum(g_ijt[i][j][t] for j in N)
                            <= A_i[i] * (1 - x_it[i][t]), "producedQuantity2"
                        )

                # 0113修正  增加一條和g有關的限制式
                #if optional:
                # for i in M:
                #     for j in N:
                #         eg1.addConstr(
                #             quicksum(g_ijt[i][j][t] for t in T)
                #             <= Q_j[j] * z_ij[i][j], "modify1"
                #         )

                # 0113修正  增加一條和y,g有關的限制式
                #if optional:    
                # for i in M:
                #     for j in N:
                #         for t in T[1:]:                         
                #             eg1.addConstr(
                #                 g_ijt[i][j][t]
                #                 <= A_i[i] * y_ijt[i][j][t], "modify2"
                #             )

                # 原模型中的u並沒有出現在教授的模型之中，暫時先保留
                # 以下維持不變
            
                ## define yield lower bound
                M_3 = 10000
                M_3 = 1
                M_4 = 1
                for i in M:
                    for t in T[1:]:
                        eg1.addConstr(
                            r_it[i][t]
                            <= M_3 * e_it[i][t] + M_4 * s_it[i][t] + r_it[i][t-1] - B_i[i], "yieldLB1"
                        )

                ## define yield lower bound
                M_4 = 10000
                M_5 = 1
                for i in M:
                    for t in T[1:]:
                        eg1.addConstr(
                            r_it[i][t]
                            <= M_3 * e_it[i][t] + M_5 * (1 - s_it[i][t]) + L_i[i], "yieldLB2"
                        )

                ## completion time
                for j in N[1:]:
                    for t in T[1:]:
                        eg1.addConstr(1 + t * u_jt[j][t]
                            <= w_j[j], "completionTime")

                ## define a lot of complete time
                for j in N:
                    for t in T[1:]:
                        eg1.addConstr(Q_j[j] - quicksum(g_ijt[i][j][t_p] for i in M for t_p in range(1,t+1)) <= Q_j[j] * u_jt[j][t], "Define end time" )

                ## job continue: every order has only one completion time     
                # for j in N[1:]:
                #     eg1.addConstr(quicksum(u_ijt[i][j][t] for t in T for i in M)
                #         == 1, "jobContinue1")

                ## job continue: define u_ijt
                # for j in N:
                #     for i in M:
                #         for t in T[1:]:    # T-1 or T????
                #             eg1.addConstr((y_ijt[i][j][t]-y_ijt[i][j][t+1])
                #                 <= u_ijt[i][j][t], "jobContinue2")

                ## yield rate = 100% after repairment
                # for i in M:
                #     for t in T[1:]:    # T-F_i or T????
                #         # eg1.addConstr((x_it[i][t]-x_it[i][t-1])
                #         #         <= r_it[i][t+F_i[i]], "yieldRateAfterRepair1")
                #         eg1.addConstr(e_it[i][t]
                #             <= r_it[i][t], "yieldRateAfterRepair1")

                ## define e_it
                # M_6 = 1
                # for i in M:
                #     for t in T[1:]:
                #         eg1.addConstr(e_it[i][t]
                #             <= M_6 * (1 - c_it[i][t]) + x_it[i][t-1] - x_it[i][t],
                #             "defineIfFirstHourAfterRepairUB")

                # for i in M:
                #     for t in T[1:]:
                #         eg1.addConstr(e_it[i][t]
                #             <= M_6 * (c_it[i][t]) + 0,
                #             "defineIfFirstHourAfterRepairLB")

                for i in M:
                    for t in T[1:]:
                       eg1.addConstr(e_it[i][t] * 2 <=  x_it[i][t-1] - x_it[i][t] + 1)

                ## repairment continue
                for i in M:
                    M_7 = F_i[i]
                    for t in T[F_i[i]:]:
                        eg1.addConstr(F_i[i] - quicksum(x_it[i][l] for l in range(t-F_i[i],t)) #不用減一對吧
                            <= M_7 * (1 - e_it[i][t]), "repairContinue")

                # constraint for e_it when t < F_i
                # for i in M:
                #     for t in T[:F_i[i]]:
                #         eg1.addConstr(e_it[i][t] == 0, "postMaintenanceFirstHourLaterThanFi")

                ## define maximum completion time
                for j in N:
                    eg1.addConstr(
                        p_j[j]
                        >= w_j[j] - D_j[j], "maximumCompletionTime1"
                    )

                # run Gurobi
                eg1.optimize()

                # show result
                print("The run time is %f" % eg1.Runtime)
                # final gap
                if eg1.Runtime > run_time:
                    print("Final MIP gap value: %f" % eg1.MIPGap)           

                name = prefix + index

                # result_list.append([name, eg1.Runtime, eg1.MIPGap])

                # 寫檔案
                if eg1.Runtime > run_time:
                    final.write(name + " " + str(eg1.Runtime) + " " + str(eg1.MIPGap) + " " + str(eg1.objVal) + "\n")
                else:
                    final.write(name + " " + str(eg1.Runtime) + " " + "-" + " " + str(eg1.objVal) + "\n")

        final.close()

        # show the result

        if show_result:          
            print("\n\nModel Result:")
            print("\n")

            # w_j
            print("w_j")
            print("Order", "\t", end="")
            for j in N:
                try:
                    print(w_j[j].x, "\t", end="")
                except:
                    print(0, "\t", end="")
            print("")   # use for change line
            print("\n")

            ## z_ij
            print("z_ij")
            print("\tOrder")   # head of the result table
            for i in M:
                print("Machine" + str(i+1), "\t", end="") # mark which item is printed now
                for j in N:
                    try:
                        print(z_ij[i][j].x, "\t", end="") # print qty of each kind of item
                    except:
                        print(0, "\t", end="")
                print("")  # use for change line
            print("\n")

            ## u_jt
            print("u_jt")
            print("\tTime")   # head of the result table
            for j in N:
                print("Order" + str(j+1), "\t", end="") # mark which item is printed now
                for t in T:
                    try:
                        print(u_jt[j][t].x, "\t", end="") # print qty of each kind of item
                    except:
                        print(0, "\t", end="")
                print("")  # use for change line
            print("\n")

            ## x_it
            print("x_it")
            print("\tTime")   # head of the result table
            for i in M:
                print("Machine" + str(i+1), "\t", end="") # mark which item is printed now
                for t in T:
                    try:
                        print(x_it[i][t].x, "\t", end="") # print qty of each kind of item
                    except:
                        print(0, "\t", end="")
                print("")  # use for change line
            print("\n")

            ## e_it
            print("e_it")
            print("\tTime")   # head of the result table
            for i in M:
                print("Machine" + str(i), "\t", end="") # mark which item is printed now
                for t in T:
                    try:
                        print(e_it[i][t].x, "\t", end="") # print qty of each kind of item
                    except:
                        print(0, "\t", end="")
                print("")  # use for change line
            print("\n")

            print("g_ijt")
            loop_count = (len(T)-1) // 10
            if (len(T)-1) % 10 != 0:
                loop_count += 1
            for loop_index in range(loop_count):
                template = '{:>10}'+'{:>5}'*(10)
                iterator = ['machine'] + [str(t) for t in T[1:][loop_index*10:(loop_index+1)*10]]
                # print(iterator)
                print(template.format(*iterator))
                for i in M[1:]:
                    row = '{:>10}'.format(str(i))
                    for t in T[1:][loop_index*10:(loop_index+1)*10]:
                        row += '  ('
                        found = False
                        for j in N[1:]:
                            try:
                                if g_ijt[i][j][t].x > 0:
                                    if not found:
                                        row += '{:>0}'.format(str(g_ijt[i][j][t].x))
                                    elif j <= 9:
                                        row += '{:>2}'.format(str(g_ijt[i][j][t].x))
                                    else:
                                        row += '{:>3}'.format(str(g_ijt[i][j][t].x))
                                    found = True
                                    continue
                            except:
                                continue
                        if not found:
                            try:
                                if x_it[i][t].x:
                                    if x_it[i][t].x == 1:
                                        row += '{:>0}'.format('M')
                                    else:
                                        row += '{:>5}'.format('')
                            except:
                                continue
                        row += ')  '
                    print(row)

                print('\n')


            # objective value
            print("objective value")
            print("z* = ", eg1.objVal)  # print objective value
