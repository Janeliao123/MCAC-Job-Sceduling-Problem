# In[0]:

import das_2020_alt_obj as model
import alt_main as algorithm

file_num = 20
m_list = [2,3,5]
# m_list = [2]
n_list = [15,25,50]
# n_list = [15]
folder_name = "testdata"
result_name = "result"
run_time = 120
ip = True
tabu_size = [50, 100]
methods = [1, 2, 3]
# tabu_size = [10]
loop = 100



# In[1]:

model.das_model(file_num, m_list, n_list, folder_name, result_name, run_time, ip)

# In[2]:

algorithm.das_algorithm(file_num, m_list, n_list, folder_name, result_name, tabu_size, loop, methods)

# %%

# %%
