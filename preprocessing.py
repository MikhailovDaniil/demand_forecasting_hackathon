import pandas as pd
import zipfile
from datetime import date
import datetime
import calendar


# Открываем исходный архив
archive = zipfile.ZipFile('./input/Данные.zip', 'r')

orders = pd.read_csv(archive.open("orders.csv"))
delays = pd.read_csv(archive.open("partners_delays.csv"))

orders = orders.rename(columns = {"date": "dttm"})


df = pd.merge(orders, delays, how = "outer", on = ['dttm', "delivery_area_id"])


# перевод строк с датами в даты
df["dttm"] = pd.to_datetime(df["dttm"])
df['dates'] = pd.to_datetime(df['dttm']).dt.date
df['time'] = pd.to_datetime(df['dttm']).dt.time


# Функция, добавляющая переменную "день недели" в dataframe
def get_weekday(row):
    return calendar.day_name[row['dttm'].weekday()]
df["weekday"] = df.apply(lambda row: get_weekday(row), axis = 1)


# Суммируем заказы по часам каждый день
df_by_days_areas = df.groupby(by = ["dates", "delivery_area_id", "weekday"]).sum().drop(labels = ["delay_rate"], axis = 1).reset_index()


# Рассмотрим исторические данные для тренировки модели
# Предсказываем на основе периода в 21 день, с количествами, нормированными на медиану последних семи дней в этом периоде

train_df = pd.DataFrame([], columns = ["dates", "delivery_area_id", "weekday", "orders_cnt", "partners_cnt", "normal_orders"])
max_date = max(df_by_days_areas["dates"])
for last_date in tqdm([max_date- datetime.timedelta(days = 7),
                  max_date- datetime.timedelta(days = 14),
                  max_date- datetime.timedelta(days = 21),
                  max_date- datetime.timedelta(days = 28)]):

    date_7 = last_date - datetime.timedelta(days = 7)
    date_21 = last_date - datetime.timedelta(days = 21)

    for d_id in df_by_days_areas["delivery_area_id"].unique():
        df_area = df_by_days_areas.loc[df_by_days_areas["delivery_area_id"] == d_id]
        df_area_21days = df_area.loc[(df_area["dates"] > date_21) & (df_area["dates"] <= last_date)]
        df_area_7days = df_area.loc[(df_area["dates"] > date_7) & (df_area["dates"] <= last_date)]
        median_7days = df_area_7days["orders_cnt"].median()

        df_area_21days["normal_orders"] = df_area_21days["orders_cnt"] / median_7days
        df_area_21days["last_date"] = last_date

        train_df = train_df.append(df_area_21days, ignore_index = True)


# Создадим dataframe с медианами последней недели (чтобы после перевести нормированные предсказания в обычные)

medians = []

max_date = max(df_by_days_areas["dates"])
last_date = max_date

date_7 = last_date - datetime.timedelta(days = 7)

for d_id in tqdm(df_by_days_areas["delivery_area_id"].unique()):
        df_area = df_by_days_areas.loc[df_by_days_areas["delivery_area_id"] == d_id]
        df_area_7days = df_area.loc[(df_area["dates"] > date_7) & (df_area["dates"] <= last_date)]
        median_7days = df_area_7days["orders_cnt"].median()
        
        medians.append([d_id, median_7days])
df_medians = pd.DataFrame(medians, columns = ["delivery_area_id", "median"])
df_medians.to_csv("./proceeded/medians.csv", sep = ";", index = False)


# преобразуем наши измерения в вектора для предсказаний
train_df["delta_days"] = train_df["last_date"] - train_df["dates"]
list_of_deltas = train_df["delta_days"].unique()
train_list = []

for d_id in tqdm(train_df["delivery_area_id"].unique()):
    for l_day in train_df["last_date"].unique():
        help_list = [d_id, l_day]
        for delta_d in list_of_deltas:
            try:
                n_orders = train_df.loc[(train_df["delivery_area_id"] == d_id) &
                                        (train_df["last_date"] == l_day) &
                                        (train_df["delta_days"] == delta_d)]["normal_orders"].values[0]
            except:
                n_orders = float("nan")
            
            help_list.append(n_orders)
            
        train_list.append(help_list)


train_df_transformed = pd.DataFrame(train_list, columns = ["delivery_area_id", "last_date"] + list(list_of_deltas))

# Создадим таргеты для тренировочной выборки (по дням недели)
target_df = pd.DataFrame([], columns = ["dates", "delivery_area_id", "weekday", "orders_cnt", "partners_cnt", "normal_orders"])
max_date = max(df_by_days_areas["dates"])

for last_date in tqdm([max_date- datetime.timedelta(days = 7),
                  max_date- datetime.timedelta(days = 14),
                  max_date- datetime.timedelta(days = 21),
                  max_date- datetime.timedelta(days = 28)]):

    date_7 = last_date - datetime.timedelta(days = 7)

    for d_id in df_by_days_areas["delivery_area_id"].unique():

        df_area = df_by_days_areas.loc[df_by_days_areas["delivery_area_id"] == d_id]
        df_area_newweek = df_area.loc[(df_area["dates"] > last_date) & (df_area["dates"] <= last_date + datetime.timedelta(days = 7))]
        df_area_7days = df_area.loc[(df_area["dates"] > date_7) & (df_area["dates"] <= last_date)]
        median_7days = df_area_7days["orders_cnt"].median()

        df_area_newweek["normal_orders"] = df_area_newweek["orders_cnt"] / median_7days
        df_area_newweek["last_date"] = last_date
        
        target_df = target_df.append(df_area_newweek, ignore_index = True)


# Объединим train и target датафреймы, сохраним их


help_df = target_df.loc[target_df["weekday"] == "Monday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/monday_train.csv", sep = ";", index = False)

help_df = target_df.loc[target_df["weekday"] == "Tuesday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/tuesday_train.csv", sep = ";", index = False)

help_df = target_df.loc[target_df["weekday"] == "Wednesday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/wednesday_train.csv", sep = ";", index = False)

help_df = target_df.loc[target_df["weekday"] == "Thursday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/thursday_train.csv", sep = ";", index = False)

help_df = target_df.loc[target_df["weekday"] == "Friday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/friday_train.csv", sep = ";", index = False)

help_df = target_df.loc[target_df["weekday"] == "Saturday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/saturday_train.csv", sep = ";", index = False)

help_df = target_df.loc[target_df["weekday"] == "Sunday"]
help_df = help_df[["delivery_area_id", "weekday", "normal_orders", "last_date"]]
help_df = help_df.rename(columns = {"normal_orders": "y"})
df_oneday = train_df_transformed.merge(help_df, how = "inner",
                                          on = ['delivery_area_id', "last_date"])
df_oneday.to_csv("./proceeded/train/sunday_train.csv", sep = ";", index = False)


# Создадим и сохраним файл с данными для предсказаний
test_df_0 = pd.DataFrame([], columns = ["dates", "delivery_area_id", "weekday", "orders_cnt", "partners_cnt", "normal_orders"])
max_date = max(df_by_days_areas["dates"])
last_date = max_date
date_7 = last_date - datetime.timedelta(days = 7)
date_21 = last_date - datetime.timedelta(days = 21)

for d_id in tqdm(df_by_days_areas["delivery_area_id"].unique()):
    df_area = df_by_days_areas.loc[df_by_days_areas["delivery_area_id"] == d_id]
    df_area_21days = df_area.loc[(df_area["dates"] > date_21) & (df_area["dates"] <= last_date)]
    df_area_7days = df_area.loc[(df_area["dates"] > date_7) & (df_area["dates"] <= last_date)]
    median_7days = df_area_7days["orders_cnt"].median()

    df_area_21days["normal_orders"] = df_area_21days["orders_cnt"] / median_7days
    df_area_21days["last_date"] = last_date
    df_area_21days["median"] = median_7days

    test_df_0 = test_df_0.append(df_area_21days, ignore_index = True)

test_df_0["delta_days"] = test_df_0["last_date"] - test_df_0["dates"]

list_of_deltas = test_df_0["delta_days"].unique()

test_list = []

for d_id in tqdm(test_df_0["delivery_area_id"].unique()):
    for l_day in test_df_0["last_date"].unique():
        help_list = [d_id, l_day]
        for delta_d in list_of_deltas:
            try:
                n_orders = test_df_0.loc[(test_df_0["delivery_area_id"] == d_id) &
                                        (test_df_0["last_date"] == l_day) &
                                        (test_df_0["delta_days"] == delta_d)]["normal_orders"].values[0]
            except:
                n_orders = float("nan")
            
            help_list.append(n_orders)
            
        test_list.append(help_list)
        
test_df = pd.DataFrame(test_list, columns = ["delivery_area_id", "last_date"] + list(list_of_deltas))

test_df = test_df.fillna(test_df.median())
test_df.to_csv("./proceeded/test.csv", sep = ";", index = False)