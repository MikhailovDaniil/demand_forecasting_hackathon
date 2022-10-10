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


# Обучение моделей и предсказания

# тренировочные данные

df_friday_train = pd.read_csv("./proceeded/train/friday_train.csv", sep = ";")
df_monday_train = pd.read_csv("./proceeded/train/monday_train.csv", sep = ";")
df_saturday_train = pd.read_csv("./proceeded/train/saturday_train.csv", sep = ";")
df_sunday_train = pd.read_csv("./proceeded/train/sunday_train.csv", sep = ";")
df_thursday_train = pd.read_csv("./proceeded/train/thursday_train.csv", sep = ";")
df_tuesday_train = pd.read_csv("./proceeded/train/tuesday_train.csv", sep = ";")
df_wednesday_train = pd.read_csv("./proceeded/train/wednesday_train.csv", sep = ";")


df_friday_train = df_friday_train.dropna()
df_monday_train = df_monday_train.dropna()
df_saturday_train = df_saturday_train.dropna()
df_sunday_train = df_sunday_train.dropna()
df_thursday_train = df_thursday_train.dropna()
df_tuesday_train = df_tuesday_train.dropna()
df_wednesday_train = df_wednesday_train.dropna()


# данные для предсказаний
test_df = pd.read_csv("./proceeded/test.csv", sep = ";")

# медианы по регионам
medians = pd.read_csv('./proceeded/medians.csv', sep = ";")


# Преобразование тренировочных и тестовых данных

X_mon = df_monday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_mon = df_monday_train[["y"]]

X_tue = df_tuesday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_tue = df_tuesday_train[["y"]]

X_wed = df_wednesday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_wed = df_wednesday_train[["y"]]

X_thu = df_thursday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_thu = df_thursday_train[["y"]]

X_fri = df_friday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_fri = df_friday_train[["y"]]

X_sat = df_saturday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_sat = df_saturday_train[["y"]]

X_sun = df_sunday_train.drop(['delivery_area_id', 'last_date','weekday', 'y'], axis = 1)
y_sun = df_sunday_train[["y"]]

X_for_predictions = test_df.drop(['delivery_area_id', 'last_date'], axis = 1)
X_for_predictions = X_for_predictions.replace(np.inf, 1)


# индексы area_id (для склеивания с предсказаниями)
indexes_id = test_df["delivery_area_id"]



### обучение моделей

lr_mon = LinearRegression().fit(X_mon , y_mon)
lr_tue = LinearRegression().fit(X_tue , y_tue)
lr_wed = LinearRegression().fit(X_wed , y_wed)
lr_thu = LinearRegression().fit(X_thu , y_thu)
lr_fri = LinearRegression().fit(X_fri , y_fri)
lr_sat = LinearRegression().fit(X_sat , y_sat)
lr_sun = LinearRegression().fit(X_sun , y_sun)


# получение предсказаний

pred_mon = lr_mon.predict(X_for_predictions)
pred_tue = lr_tue.predict(X_for_predictions)
pred_wed = lr_wed.predict(X_for_predictions)
pred_thu = lr_thu.predict(X_for_predictions)
pred_fri = lr_fri.predict(X_for_predictions)
pred_sat = lr_sat.predict(X_for_predictions)
pred_sun = lr_sun.predict(X_for_predictions)


df_pred_mon = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_mon).tolist()
             })

df_pred_tue = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_tue).tolist()
             })

df_pred_wed = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_wed).tolist()
             })

df_pred_thu = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_thu).tolist()
             })

df_pred_fri = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_fri).tolist()
             })

df_pred_sat = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_sat).tolist()
             })

df_pred_sun = pd.DataFrame({'delivery_area_id': list(indexes_id),
              'prediction_norm' : np.concatenate(pred_sun).tolist()
             })


medians = medians.fillna(medians.mean())

df_pred_mon = df_pred_mon.merge(medians, how = "inner", on = ["delivery_area_id"])
df_pred_tue = df_pred_tue.merge(medians, how = "inner", on = ["delivery_area_id"])
df_pred_wed = df_pred_wed.merge(medians, how = "inner", on = ["delivery_area_id"])
df_pred_thu = df_pred_thu.merge(medians, how = "inner", on = ["delivery_area_id"])
df_pred_fri = df_pred_fri.merge(medians, how = "inner", on = ["delivery_area_id"])
df_pred_sat = df_pred_sat.merge(medians, how = "inner", on = ["delivery_area_id"])
df_pred_sun = df_pred_sun.merge(medians, how = "inner", on = ["delivery_area_id"])


for df_help in [df_pred_mon, df_pred_tue, df_pred_wed,
                df_pred_thu, df_pred_fri, df_pred_sat, df_pred_sun]:
    df_help["prediction"] =  df_help["prediction_norm"] * df_help["median"]



df_pred_mon = df_pred_mon[["delivery_area_id", "prediction"]]
df_pred_tue = df_pred_tue[["delivery_area_id", "prediction"]]
df_pred_wed = df_pred_wed[["delivery_area_id", "prediction"]]
df_pred_thu = df_pred_thu[["delivery_area_id", "prediction"]]
df_pred_fri = df_pred_fri[["delivery_area_id", "prediction"]]
df_pred_sat = df_pred_sat[["delivery_area_id", "prediction"]]
df_pred_sun = df_pred_sun[["delivery_area_id", "prediction"]]

df_pred_mon.to_csv("./proceeded/predictions/monday.csv", sep = ";", index = False)
df_pred_tue.to_csv("./proceeded/predictions/tuesday.csv", sep = ";", index = False)
df_pred_wed.to_csv("./proceeded/predictions/wednesday.csv", sep = ";", index = False)
df_pred_thu.to_csv("./proceeded/predictions/thursday.csv", sep = ";", index = False)
df_pred_fri.to_csv("./proceeded/predictions/friday.csv", sep = ";", index = False)
df_pred_sat.to_csv("./proceeded/predictions/saturday.csv", sep = ";", index = False)
df_pred_sun.to_csv("./proceeded/predictions/sunday.csv", sep = ";", index = False)
