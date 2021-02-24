import random


file_num = 24
folder_name = "test_data/2001031801"
prefix = "2001031801." # problem 編號

file_list = [str(i+1) for i in range(file_num)]

for f in file_list:
    file = open(folder_name + "/" + prefix + f + ".in", "w+")
    # mean = {"b":[7,3], "p0":[80,50], "L":[0.8,0.5],
    #         "m":[30,20], "a":[650,350], "q":[300,200], "n":[650,350],
    #         "d":[500,250],
    #         "c":[4,2], "h":[0.75,0.25]}
    scenario = {"機台品質":"", "產量比":"", "急迫度":"", "維修難度":""}
    mean = {}
    if(int(f) % 2 == 1):
        mean["b"] = 8
        mean["p0"] = 70
        mean["L"] = 1
        scenario["機台品質"] = "好"
    else:
        mean["b"] = 3
        mean["p0"] = 15
        mean["L"] = 0.5
        scenario["機台品質"] = "壞"

    if(int((int(f)-1)/2) % 2 == 0):
        mean["m"] = 25
        mean["a"] = 250
        mean["q"] = 200
        mean["n"] = 500
        scenario["產量比"] = "高"
    else:
        mean["m"] = 15
        mean["a"] = 100
        mean["q"] = 400
        mean["n"] = 800
        scenario["產量比"] = "低"


    if((int(f)-1)/8 < 1):
        mean["c"] = 2
        mean["h"] = 0.7
        scenario["維修難度"] = "低"
    elif((int(f)-1)/8 >= 1 and (int(f)-1)/8 < 2):
        mean["c"] = 3
        mean["h"] = 0.4
        scenario["維修難度"] = "中"
    else:
        mean["c"] = 4
        mean["h"] = 0.1
        scenario["維修難度"] = "高"

    m = round(random.triangular(1,50, mean["m"]))
    n = round(random.triangular(100, 1000, mean["n"]))
    h = max(1,round(random.triangular(1, m, mean["h"] * m)))

    if(int((int(f)-1)/4) % 2 == 0):
        mean["d"] = 2
        scenario["急迫度"] = "緩"
    else:
        mean["d"] = 0.5
        scenario["急迫度"] = "急"

    print("test" + f + ":\t",scenario)

    a = [round(random.triangular(1, mean["a"]*3, mean["a"])) for i in range(m)]
    b = [round(random.triangular(1, 10, mean["b"])) for i in range(m)]
    c = [round(random.triangular(1, 5, mean["c"])) for i in range(m)]
    p0 = [round(random.triangular(1, 100, mean["p0"])) for i in range(m)]
    L = [max(round(random.triangular(1, p0[i], mean["L"] * p0[i])),1) for i in range(m)]

    q = [round(random.triangular(1, 500, mean["q"])) for i in range(n)]
    # d = [round(random.triangular(1, int(n/m)*2, int(n/m) * mean["d"])) for i in range(n)]
    d = [random.randint(1, int(n/m) * mean["d"] * 2) for i in range(n)]
    

    file.write(str(m) + " " + str(n) + " " + str(h) + "\n")

    for i in range(m):
        file.write(str(a[i]) + " " + str(b[i]) + " " + str(c[i]) + " " + str(p0[i]) + " " + str(L[i]) + "\n")

    for i in range(n-1):
        file.write(str(q[i]) + " " + str(d[i]) + "\n") 

    
    file.write(str(q[n-1]) + " " + str(d[n-1]))       

    
    file.close()