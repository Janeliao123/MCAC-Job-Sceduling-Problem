# In[0]:

import alt_main as algorithm
import das_2020_alt_obj as model
import das_2020_relax_y_dict as model_relax


# In[1]
file_num = 20
factors_list = {0:'machine',1:'due_date',2:'weight',3:'main_time',4:'resource_limit',5:'decreasing_rate'}
type = ['H','L']
folder_name = "testdata_0512"
result_name = "result_0512"
run_time = 1800
ip = False
tabu_size = [100]
# rule base method
methods = [2,3]
# 1: 用 maintenance_rule(threshold)
# 0: 用單純 EDD method
maintenance_rule = 1
yield_threshold = [80,70]
loop = 100

# In[2]:
model.das_model(file_num, factors_list, type, folder_name, result_name, run_time, ip)
# In[2]:
model_relax.das_model(file_num, factors_list, type, folder_name, result_name, run_time, ip)
# In[2]:
algorithm.das_algorithm(file_num, factors_list, type, folder_name, result_name, tabu_size, loop, methods, maintenance_rule, yield_threshold)

# In[1]
file_num = 20
factors_list = {0:'machine',1:'due_date',2:'weight',3:'main_time',4:'resource_limit',5:'decreasing_rate'}
type = ['H','L']
folder_name = "testdata_0512"
result_name = "result_0512"
run_time = 1800
ip = True
tabu_size = [100]
# rule base method
methods = [3,4]
# 1: 用 maintenance_rule(threshold)
# 0: 用單純 EDD method
maintenance_rule = 0
yield_threshold = [80,70]
loop = 100

algorithm.das_algorithm(file_num, factors_list, type, folder_name, result_name, tabu_size, loop, methods, maintenance_rule, yield_threshold)

# In[2]:


# %%

# In[] old version
file_num = 20
m_list = [5]
# m_list = [2]
n_list = [25,50]
# n_list = [15]
folder_name = "testdata"
result_name = "result"
run_time = 120
ip = True
tabu_size = [100]
# methods = [1,2,3,4]
methods = [1,2,3]
maintenance_rule = 1
yield_threshold = [80,70]
# yield_threshold = [90]
loop = 100

model.das_model(file_num, m_list, n_list, folder_name, result_name, run_time, ip)

algorithm.das_algorithm(file_num, m_list, n_list, folder_name, result_name, tabu_size, loop, methods, maintenance_rule, yield_threshold)
