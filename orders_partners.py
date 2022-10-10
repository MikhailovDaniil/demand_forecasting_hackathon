#!/usr/bin/env python
# coding: utf-8

# # Число заказов и партнеров

# In[1]:


import pandas as pd
import zipfile
from datetime import date
import datetime
import calendar
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
import matplotlib.dates as mdates
import random
from tqdm import tqdm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split 


# # Настя и Катя

# In[2]:


df6_m = pd.read_csv("./proceeded/orders/mond.csv", sep = ";")
df6_tu = pd.read_csv("./proceeded/orders/tuesd.csv", sep = ";")
df6_wed = pd.read_csv("./proceeded/orders/wednesd.csv", sep = ";")
df6_thu = pd.read_csv("./proceeded/orders/thursd.csv", sep = ";")
df6_fri = pd.read_csv("./proceeded/orders/frid.csv", sep = ";")
df6_sat = pd.read_csv("./proceeded/orders/saturd.csv", sep = ";")
df6_sun = pd.read_csv("./proceeded/orders/sund.csv", sep = ";")


# In[4]:


display(df6_m)
display(df6_tu)
display(df6_wed)
display(df6_thu)
display(df6_fri)
display(df6_sat)
display(df6_sun)


# In[5]:


sn.barplot(x='hour', y='partners_cnt', data = df6_fri[df6_fri.delivery_area_id == 0]).set(title='Количество курьеров в пятницу по часам в регионе 0');


# In[6]:


sn.barplot(x='hour', y='orders_cnt', data = df6_fri[df6_fri.delivery_area_id == 0]).set(title='Количество заказов в пятницу по часам в регионе 0');


# In[ ]:




