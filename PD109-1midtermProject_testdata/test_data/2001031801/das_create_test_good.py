import random


# file_num = 10
# folder_name = "test_data/stage1/1230_good"
# prefix = "m5n5_" # problem 編號

# m = 5
# n = 5

# file_list = [str(i+1) for i in range(file_num)]

# for f in file_list:
#     file = open(folder_name + "/" + prefix + f + ".in", "w+")
#     # b = B_i, a = A_ij原始生產速率, r_i0 初始良率, Q_j 訂單量, d due date
#     # mean = {"B_i":[8,3], "r_i0":[80,25], "L_i":[0.8,0.5],
#     #         "m":[30,20], "A_ij":[250,50], "Q_j":[150,50], "n":[650,350],
#     #         "D_j":[500,250],
#     #         "F_i":[2,3,4], "H":[0.7,0.5,0.3]}
#     scenario = {"機台品質":"", "產量比":"", "急迫度":"", "維修難度":""}
#     mean = {}
#     if(int(f) % 2 == 1):
#         mean["B_i"] = 8
#         mean["r_i0"] = 80
#         mean["L_i"] = 0.8
#         scenario["機台品質"] = "好"
#     else:
#         mean["B_i"] = 3
#         mean["r_i0"] = 25
#         mean["L_i"] = 0.5
#         scenario["機台品質"] = "壞"

#     if(int((int(f)-1)/2) % 2 == 0):
#         # mean["m"] = 25
#         mean["A_ij"] = 250
#         mean["Q_j"] = 150
#         # mean["n"] = 500
#         scenario["產量比"] = "高"
#     else:
#         # mean["m"] = 15
#         mean["A_ij"] = 50
#         mean["Q_j"] = 50
#         # mean["n"] = 800
#         scenario["產量比"] = "低"


#     if((int(f)-1)/8 < 1):
#         mean["F_i"] = 2
#         mean["H"] = 0.7
#         scenario["維修難度"] = "低"
#     elif((int(f)-1)/8 >= 1 and (int(f)-1)/8 < 2):
#         mean["F_i"] = 3
#         mean["H"] = 0.5
#         scenario["維修難度"] = "中"
#     else:
#         mean["F_i"] = 4
#         mean["H"] = 0.3
#         scenario["維修難度"] = "高"

#     # m = round(random.triangular(1,50, mean["m"]))
#     # n = round(random.triangular(100, 1000, mean["n"]))
#     m = 2
#     n = 5
#     H = max(1,round(random.triangular(1, m, mean["H"] * m)))

#     if(int((int(f)-1)/4) % 2 == 0):
#         mean["D_j"] = 2
#         scenario["急迫度"] = "緩"
#     else:
#         mean["D_j"] = 0.5
#         scenario["急迫度"] = "急"

#     print("test" + f + ":\t",scenario)

file_num = 10
m_list = [1, 3, 5]
n_list = [5, 10, 15]
folder_name = "test_data/stage1/1230_good"

# m = 5
# n = 5

for m in m_list:
    for n in n_list:
        prefix = "m"+str(m)+"n"+str(n)+"_" # problem 編號


        file_list = [str(i+1) for i in range(file_num)]

        for f in file_list:
            file = open(folder_name + "/" + prefix + f + ".txt", "w+")

            Q_j = [round(random.uniform(500, 700)) for i in range(n)]
            A_ij = [200 for i in range(m)]
            r_i0 = [100 for i in range(m)] # *100
            B_i = [5 for i in range(m)] # *100
            L_i = [70 for i in range(m)] # *100
            eta = (n * (600 / (200*0.85))) / m
            D_j = [round(random.uniform(0.8 * eta, 1.2 * eta)) for i in range(n)]

            # F_i: 1 / 3
            F_i = [2 for i in range(m)]
            H = m


            file.write(str(m) + " " + str(n) + " " + str(H) + "\n")

            for i in range(m):
                file.write(str(A_ij[i]) + " " + str(B_i[i]) + " " + str(F_i[i]) + " " + str(r_i0[i]) + " " + str(L_i[i]) + "\n")

            for i in range(n-1):
                file.write(str(Q_j[i]) + " " + str(D_j[i]) + "\n")


            file.write(str(Q_j[n-1]) + " " + str(D_j[n-1]))


            file.close()