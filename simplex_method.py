import pandas as pd
import numpy as np
import seaborn as sn
from scipy.optimize import linprog

monday = pd.read_csv("./proceeded/orders/mond.csv",sep=";")
tuesday = pd.read_csv("./proceeded/orders/tuesd.csv",sep=";")
wednesday = pd.read_csv("./proceeded/orders/wednesd.csv",sep=";")
thursday = pd.read_csv("./proceeded/orders/thursd.csv",sep=";")
friday = pd.read_csv("./proceeded/orders/frid.csv",sep=";")
saturday = pd.read_csv("./proceeded/orders/saturd.csv",sep=";")
sunday = pd.read_csv("./proceeded/orders/sund.csv",sep=";")

monday = monday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open = monday.hour.min()
max_close = monday.hour.max()
n1 = max_close - min_open + 1

#создадим таблицу со всеми возможными сменами для понедельника
number_of_shift = "shift_"
shift_beg = list()
shift_end = list()
shifts = list()
m1 = 5*n1-25
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n1-i+1):
        begin_time = min_open+j
        number_of_shift += str(begin_time)
        number_of_shift += "_"
        end_time = begin_time+i
        number_of_shift += str(end_time)
        shifts.append(number_of_shift)
        number_of_shift = "shift_"
        shift_beg.append(begin_time)
        shift_end.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n1+1-i)
shifts_monday = pd.DataFrame(shifts)
shifts_monday.columns = ["shift"]
shifts_monday["open_hour"] = pd.Series(shift_beg)
shifts_monday["close_hour"] = pd.Series(shift_end)
areas = monday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_mond = 0
m_mond = 0
for t in areas:
    begin1 = monday[monday["delivery_area_id"] == t].hour.min()
    end1 = monday[monday["delivery_area_id"] == t].hour.max()
    n_mond = end1 - begin1 + 1
    m_mond = 5*n_mond-25
    if (n_mond < 6):
        delivery_num = str(t)
        shifts_monday[delivery_num] = np.zeros(m1)
        var_index = 0
        if (n_mond < 5):
            var_index = shifts_monday.loc[(shifts_monday["open_hour"] == begin1) & (shifts_monday["close_hour"] == begin1+4)].index
            couriers_q = monday[monday["delivery_area_id"] == t].partners_cnt.max()
            shifts_monday.loc[var_index, delivery_num] = couriers_q
        else:
            var_index = shifts_monday.loc[(shifts_monday["open_hour"] == begin1) & (shifts_monday["close_hour"] == begin1+5)].index
            couriers_q = monday[monday["delivery_area_id"] == t].partners_cnt.max()
            shifts_monday.loc[var_index, delivery_num] = couriers_q
        continue
    a = np.zeros((m_mond, n_mond))
    times_mond = np.zeros((m_mond, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_mond-i+1):
            begin_time = begin1+j
            end_time = begin_time+i
            times_mond[j+count][0] = begin_time
            times_mond[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a[j + count][k] = -1
        count+=(n_mond+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(monday[monday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_mond:
        hours = np.array(monday[monday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin1, end1):
            if x != hours[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_mond)
    a_transposed = a.transpose()
    res = linprog(c, a_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_monday[delivery_num] = np.zeros(m1)
    for i in range(m_mond):
        present_open, present_close = times_mond[i][0], times_mond[i][1]
        present_index = shifts_monday.loc[(shifts_monday["open_hour"] == present_open) & (shifts_monday["close_hour"] == present_close)].index
        shifts_monday.loc[present_index, delivery_num] = res.x[i]

tuesday = tuesday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open2 = tuesday.hour.min()
max_close2 = tuesday.hour.max()
n2 = max_close2 - min_open2 + 1
#создадим таблицу со всеми возможными сменами для вторника
number_of_shift2 = "shift_"
shift_beg2 = list()
shift_end2 = list()
shifts2 = list()
m2 = 5*n2-25
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n2-i+1):
        begin_time = min_open+j
        number_of_shift2 += str(begin_time)
        number_of_shift2 += "_"
        end_time = begin_time+i
        number_of_shift2 += str(end_time)
        shifts2.append(number_of_shift2)
        number_of_shift2 = "shift_"
        shift_beg2.append(begin_time)
        shift_end2.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n2+1-i)
shifts_tuesday = pd.DataFrame(shifts2)
shifts_tuesday.columns = ["shift"]
shifts_tuesday["open_hour"] = pd.Series(shift_beg2)
shifts_tuesday["close_hour"] = pd.Series(shift_end2)
areas2 = tuesday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_tue = 0
m_tue = 0
for t in areas2:
    begin2 = tuesday[tuesday["delivery_area_id"] == t].hour.min()
    end2 = tuesday[tuesday["delivery_area_id"] == t].hour.max()
    n_tue = end2 - begin2 + 1
    m_tue = 0
    ind_tue = 4
    while ind_tue <= n_tue:
        m_tue += n_tue - ind_tue + 1;
        ind_tue += 1
    if (n_tue < 6):
        delivery_num2 = str(t)
        shifts_tuesday[delivery_num2] = np.zeros(m2)
        var_index = 0
        if (n_mond < 5):
            var_index = shifts_tuesday.loc[(shifts_tuesday["open_hour"] == begin2) & (shifts_tuesday["close_hour"] == begin2+4)].index
            couriers_q = tuesday[tuesday["delivery_area_id"] == t].partners_cnt.max()
            shifts_tuesday.loc[var_index, delivery_num2] = couriers_q
        else:
            var_index = shifts_tuesday.loc[(shifts_tuesday["open_hour"] == begin2) & (shifts_tuesday["close_hour"] == begin2+5)].index
            couriers_q = tuesday[tuesday["delivery_area_id"] == t].partners_cnt.max()
            shifts_tuesday.loc[var_index, delivery_num2] = couriers_q
        continue
    a2 = np.zeros((m_tue, n_tue))
    times_tue = np.zeros((m_tue, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_tue-i+1):
            begin_time = begin2+j
            end_time = begin_time+i
            times_tue[j+count][0] = begin_time
            times_tue[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a2[j + count][k] = -1
        count+=(n_tue+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(tuesday[tuesday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_tue:
        hours2 = np.array(tuesday[tuesday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin2, end2):
            if x != hours2[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_tue)
    a2_transposed = a2.transpose()
    res = linprog(c, a2_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_tuesday[delivery_num] = np.zeros(m2)
    for i in range(m_tue):
        present_open, present_close = times_tue[i][0], times_tue[i][1]
        present_index = shifts_tuesday.loc[(shifts_tuesday["open_hour"] == present_open) & (shifts_tuesday["close_hour"] == present_close)].index
        shifts_tuesday.loc[present_index, delivery_num] = res.x[i]

wednesday = wednesday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open3 = wednesday.hour.min()
max_close3 = wednesday.hour.max()
n3 = max_close3 - min_open3 + 1
#создадим таблицу со всеми возможными сменами для вторника
number_of_shift3 = "shift_"
shift_beg3 = list()
shift_end3 = list()
shifts3 = list()
m3 = 5*n3-25
a = np.zeros((m3, n3))
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n3-i+1):
        begin_time = min_open+j
        number_of_shift3 += str(begin_time)
        number_of_shift3 += "_"
        end_time = begin_time+i
        number_of_shift3 += str(end_time)
        shifts3.append(number_of_shift3)
        number_of_shift3 = "shift_"
        shift_beg3.append(begin_time)
        shift_end3.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n3+1-i)
shifts_wednesday = pd.DataFrame(shifts3)
shifts_wednesday.columns = ["shift"]
shifts_wednesday["open_hour"] = pd.Series(shift_beg3)
shifts_wednesday["close_hour"] = pd.Series(shift_end3)
areas3 = wednesday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_wed = 0
m_wed = 0
for t in areas3:
    begin3 = wednesday[wednesday["delivery_area_id"] == t].hour.min()
    end3 = wednesday[wednesday["delivery_area_id"] == t].hour.max()
    n_wed = end3- begin3 + 1
    m_wed = 0
    ind_wed = 4
    while ind_wed <= n_wed:
        m_wed += n_wed - ind_wed + 1;
        ind_wed += 1
    if (n_wed < 6):
        delivery_num3 = str(t)
        shifts_wednesday[delivery_num3] = np.zeros(m3)
        var_index = 0
        if (n_wed < 5):
            var_index = shifts_wednesday.loc[(shifts_wednesday["open_hour"] == begin3) & (shifts_wednesday["close_hour"] == begin3+4)].index
            couriers_q = wednesday[wednesday["delivery_area_id"] == t].partners_cnt.max()
            shifts_wednesday.loc[var_index, delivery_num3] = couriers_q
        else:
            var_index = shifts_wednesday.loc[(shifts_wednesday["open_hour"] == begin3) & (shifts_wednesday["close_hour"] == begin3+5)].index
            couriers_q = tuesday[tuesday["delivery_area_id"] == t].partners_cnt.max()
            shifts_tuesday.loc[var_index, delivery_num3] = couriers_q
        continue
    a = np.zeros((m_wed, n_wed))
    times_wed = np.zeros((m_wed, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_wed-i+1):
            begin_time = begin3+j
            end_time = begin_time+i
            times_wed[j+count][0] = begin_time
            times_wed[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a[j + count][k] = -1
        count+=(n_wed+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(wednesday[wednesday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_wed:
        hours3 = np.array(wednesday[wednesday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin3, end3):
            if x != hours3[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_wed)
    a_transposed = a.transpose()
    res = linprog(c, a_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_wednesday[delivery_num] = np.zeros(m3)
    for i in range(m_wed):
        present_open, present_close = times_wed[i][0], times_wed[i][1]
        present_index = shifts_wednesday.loc[(shifts_wednesday["open_hour"] == present_open) & (shifts_wednesday["close_hour"] == present_close)].index
        shifts_wednesday.loc[present_index, delivery_num] = res.x[i]

thursday = thursday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open4 = thursday.hour.min()
max_close4 = thursday.hour.max()
n4 = max_close4 - min_open4 + 1
#создадим таблицу со всеми возможными сменами для вторника
number_of_shift4 = "shift_"
shift_beg4 = list()
shift_end4 = list()
shifts4 = list()
m4 = 5*n4-25
a = np.zeros((m4, n4))
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n4-i+1):
        begin_time = min_open+j
        number_of_shift4 += str(begin_time)
        number_of_shift4 += "_"
        end_time = begin_time+i
        number_of_shift4 += str(end_time)
        shifts4.append(number_of_shift4)
        number_of_shift4 = "shift_"
        shift_beg4.append(begin_time)
        shift_end4.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n4+1-i)
shifts_thursday = pd.DataFrame(shifts4)
shifts_thursday.columns = ["shift"]
shifts_thursday["open_hour"] = pd.Series(shift_beg4)
shifts_thursday["close_hour"] = pd.Series(shift_end4)
areas4 = thursday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_th = 0
m_th = 0
for t in areas4:
    begin4 = thursday[thursday["delivery_area_id"] == t].hour.min()
    end4 = thursday[thursday["delivery_area_id"] == t].hour.max()
    n_th = end4- begin4 + 1
    m_th = 0
    ind_th = 4
    while ind_th <= n_th:
        m_th += n_th - ind_th + 1;
        ind_th += 1
    if (n_th < 6):
        delivery_num4 = str(t)
        shifts_thursday[delivery_num4] = np.zeros(m4)
        var_index = 0
        if (n_th< 5):
            var_index = shifts_thursday.loc[(shifts_thursday["open_hour"] == begin4) & (shifts_thursday["close_hour"] == begin4+4)].index
            couriers_q = thursday[thursday["delivery_area_id"] == t].partners_cnt.max()
            shifts_thursday.loc[var_index, delivery_num4] = couriers_q
        else:
            var_index = shifts_thursday.loc[(shifts_thursday["open_hour"] == begin4) & (shifts_thursday["close_hour"] == begin4+5)].index
            couriers_q = thursday[thursday["delivery_area_id"] == t].partners_cnt.max()
            shifts_thursday.loc[var_index, delivery_num4] = couriers_q
        continue
    a = np.zeros((m_th, n_th))
    times_th = np.zeros((m_th, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_th-i+1):
            begin_time = begin4+j
            end_time = begin_time+i
            times_th[j+count][0] = begin_time
            times_th[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a[j + count][k] = -1
        count+=(n_th+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(thursday[thursday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_th:
        hours4 = np.array(thursday[thursday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin4, end4):
            if x != hours4[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_th)
    a_transposed = a.transpose()
    res = linprog(c, a_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_thursday[delivery_num] = np.zeros(m4)
    for i in range(m_th):
        present_open, present_close = times_th[i][0], times_th[i][1]
        present_index = shifts_thursday.loc[(shifts_thursday["open_hour"] == present_open) & (shifts_thursday["close_hour"] == present_close)].index
        shifts_thursday.loc[present_index, delivery_num] = res.x[i]

friday = friday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open5 = friday.hour.min()
max_close5 = friday.hour.max()
n5 = max_close5 - min_open5 + 1
#создадим таблицу со всеми возможными сменами для вторника
number_of_shift5 = "shift_"
shift_beg5 = list()
shift_end5 = list()
shifts5 = list()
m5 = 5*n5-25
a = np.zeros((m5, n5))
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n5-i+1):
        begin_time = min_open+j
        number_of_shift5 += str(begin_time)
        number_of_shift5 += "_"
        end_time = begin_time+i
        number_of_shift5 += str(end_time)
        shifts5.append(number_of_shift5)
        number_of_shift5 = "shift_"
        shift_beg5.append(begin_time)
        shift_end5.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n5+1-i)
shifts_friday = pd.DataFrame(shifts5)
shifts_friday.columns = ["shift"]
shifts_friday["open_hour"] = pd.Series(shift_beg5)
shifts_friday["close_hour"] = pd.Series(shift_end5)
areas5 = friday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_fr = 0
m_fr = 0
for t in areas5:
    begin5 = friday[friday["delivery_area_id"] == t].hour.min()
    end5 = friday[friday["delivery_area_id"] == t].hour.max()
    n_fr = end5- begin5 + 1
    m_fr = 0
    ind_fr = 4
    while ind_fr <= n_fr:
        m_fr += n_fr - ind_fr + 1;
        ind_fr += 1
    if (n_fr < 6):
        delivery_num5 = str(t)
        shifts_friday[delivery_num5] = np.zeros(m5)
        var_index = 0
        if (n_fr < 5):
            var_index = shifts_friday.loc[(shifts_friday["open_hour"] == begin5) & (shifts_friday["close_hour"] == begin5+4)].index
            couriers_q = friday[friday["delivery_area_id"] == t].partners_cnt.max()
            shifts_friday.loc[var_index, delivery_num5] = couriers_q
        else:
            var_index = shifts_friday.loc[(shifts_friday["open_hour"] == begin5) & (shifts_friday["close_hour"] == begin5+5)].index
            couriers_q = friday[friday["delivery_area_id"] == t].partners_cnt.max()
            shifts_friday.loc[var_index, delivery_num5] = couriers_q
        continue
    a = np.zeros((m_fr, n_fr))
    times_fr = np.zeros((m_fr, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_fr-i+1):
            begin_time = begin5+j
            end_time = begin_time+i
            times_fr[j+count][0] = begin_time
            times_fr[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a[j + count][k] = -1
        count+=(n_fr+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(friday[friday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_fr:
        hours5 = np.array(friday[friday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin5, end5):
            if x != hours5[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_fr)
    a_transposed = a.transpose()
    res = linprog(c, a_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_thursday[delivery_num] = np.zeros(m5)
    for i in range(m_fr):
        present_open, present_close = times_fr[i][0], times_fr[i][1]
        present_index = shifts_friday.loc[(shifts_friday["open_hour"] == present_open) & (shifts_friday["close_hour"] == present_close)].index
        shifts_friday.loc[present_index, delivery_num] = res.x[i]

saturday = saturday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open6 = saturday.hour.min()
max_close6 = saturday.hour.max()
n6 = max_close6 - min_open6 + 1
#создадим таблицу со всеми возможными сменами для вторника
number_of_shift6 = "shift_"
shift_beg6 = list()
shift_end6 = list()
shifts6 = list()
m6 = 5*n6-25
a = np.zeros((m6, n6))
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n6-i+1):
        begin_time = min_open+j
        number_of_shift6 += str(begin_time)
        number_of_shift6 += "_"
        end_time = begin_time+i
        number_of_shift6 += str(end_time)
        shifts6.append(number_of_shift6)
        number_of_shift6 = "shift_"
        shift_beg6.append(begin_time)
        shift_end6.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n6+1-i)
shifts_saturday = pd.DataFrame(shifts6)
shifts_saturday.columns = ["shift"]
shifts_saturday["open_hour"] = pd.Series(shift_beg6)
shifts_saturday["close_hour"] = pd.Series(shift_end6)
areas6 = saturday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_st = 0
m_st = 0
for t in areas6:
    begin6 = saturday[saturday["delivery_area_id"] == t].hour.min()
    end6 = saturday[saturday["delivery_area_id"] == t].hour.max()
    n_st = end6- begin6 + 1
    m_st = 0
    ind_st = 4
    while ind_st <= n_st:
        m_st += n_st - ind_st + 1;
        ind_st += 1
    if (n_st < 6):
        delivery_num6 = str(t)
        shifts_saturday[delivery_num6] = np.zeros(m6)
        var_index = 0
        if (n_st < 5):
            var_index = shifts_saturday.loc[(shifts_saturday["open_hour"] == begin6) & (shifts_saturday["close_hour"] == begin6+4)].index
            couriers_q = saturday[saturday["delivery_area_id"] == t].partners_cnt.max()
            shifts_saturday.loc[var_index, delivery_num6] = couriers_q
        else:
            var_index = shifts_saturday.loc[(shifts_saturday["open_hour"] == begin6) & (shifts_saturday["close_hour"] == begin6+5)].index
            couriers_q = saturday[saturday["delivery_area_id"] == t].partners_cnt.max()
            shifts_saturday.loc[var_index, delivery_num6] = couriers_q
        continue
    a = np.zeros((m_st, n_st))
    times_st = np.zeros((m_st, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_st-i+1):
            begin_time = begin6+j
            end_time = begin_time+i
            times_st[j+count][0] = begin_time
            times_st[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a[j + count][k] = -1
        count+=(n_st+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(saturday[saturday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_st:
        hours6 = np.array(saturday[saturday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin6, end6):
            if x != hours6[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_st)
    a_transposed = a.transpose()
    res = linprog(c, a_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_saturday[delivery_num] = np.zeros(m6)
    for i in range(m_st):
        present_open, present_close = times_st[i][0], times_st[i][1]
        present_index = shifts_saturday.loc[(shifts_saturday["open_hour"] == present_open) & (shifts_saturday["close_hour"] == present_close)].index
        shifts_saturday.loc[present_index, delivery_num] = res.x[i]

sunday = sunday.sort_values(['delivery_area_id', 'hour'], ascending=[True, True])
min_open7 = sunday.hour.min()
max_close7 = sunday.hour.max()
n7 = max_close7 - min_open7 + 1
#создадим таблицу со всеми возможными сменами для вторника
number_of_shift7 = "shift_"
shift_beg7 = list()
shift_end7 = list()
shifts7 = list()
m7 = 5*n7-25
a = np.zeros((m7, n7))
count=0;
begin_time = 0
end_time = 0
for i in range(4,9):
    for j in range(n7-i+1):
        begin_time = min_open+j
        number_of_shift7 += str(begin_time)
        number_of_shift7 += "_"
        end_time = begin_time+i
        number_of_shift7 += str(end_time)
        shifts7.append(number_of_shift7)
        number_of_shift7 = "shift_"
        shift_beg7.append(begin_time)
        shift_end7.append(end_time)
        begin_time = 0
        end_time = 0
    count+=(n7+1-i)
shifts_sunday = pd.DataFrame(shifts7)
shifts_sunday.columns = ["shift"]
shifts_sunday["open_hour"] = pd.Series(shift_beg7)
shifts_sunday["close_hour"] = pd.Series(shift_end7)
areas7 = sunday.delivery_area_id.unique()

#запустим сипмлекс-метод отдельно для каждого региона
n_sn = 0
m_sn = 0
for t in areas7:
    begin7 = sunday[sunday["delivery_area_id"] == t].hour.min()
    end7 = sunday[sunday["delivery_area_id"] == t].hour.max()
    n_sn = end7 - begin7 + 1
    m_sn = 0
    ind_sn = 4
    while ind_sn <= n_sn:
        m_sn += n_sn - ind_sn + 1;
        ind_sn += 1
    if (n_sn < 6):
        delivery_num7 = str(t)
        shifts_sunday[delivery_num7] = np.zeros(m7)
        var_index = 0
        if (n_sn < 5):
            var_index = shifts_sunday.loc[(shifts_sunday["open_hour"] == begin7) & (shifts_sunday["close_hour"] == begin7+4)].index
            couriers_q = sunday[sunday["delivery_area_id"] == t].partners_cnt.max()
            shifts_sunday.loc[var_index, delivery_num7] = couriers_q
        else:
            var_index = shifts_sunday.loc[(shifts_sunday["open_hour"] == begin7) & (shifts_sunday["close_hour"] == begin7+5)].index
            couriers_q = sunday[sunday["delivery_area_id"] == t].partners_cnt.max()
            shifts_sunday.loc[var_index, delivery_num7] = couriers_q
        continue
    a = np.zeros((m_sn, n_sn))
    times_sn = np.zeros((m_sn, 2))
    count=0;
    begin_time = 0
    end_time = 0
    for i in range(4,9):
        for j in range(n_sn-i+1):
            begin_time = begin7+j
            end_time = begin_time+i
            times_sn[j+count][0] = begin_time
            times_sn[j+count][1] = end_time
            begin_time = 0
            end_time = 0
            for k in range(j,j+i):
                a[j + count][k] = -1
        count+=(n_sn+1-i)
    #сделали матрицу а для симплекс метода
    b = np.array(sunday[sunday["delivery_area_id"] == t]["partners_cnt"])
    if len(b) < n_sn:
        hours7 = np.array(sunday[sunday["delivery_area_id"] == t]["hour"])
        counter_hours = 0
        for x in range(begin7, end7):
            if x != hours7[counter_hours]:
                b = np.insert(b, counter_hours, x)
            else:
                counter_hours += 1
    for idx in range(len(b)):
        b[idx] = b[idx] * (-1)
    c = np.ones(m_sn)
    a_transposed = a.transpose()
    res = linprog(c, a_transposed, b, method="simplex")
    #собрали результаты для симплекс метода с каждого региона отдельно
    delivery_num = str(t)
    shifts_sunday[delivery_num] = np.zeros(m7)
    for i in range(m_sn):
        present_open, present_close = times_sn[i][0], times_sn[i][1]
        present_index = shifts_sunday.loc[(shifts_sunday["open_hour"] == present_open) & (shifts_sunday["close_hour"] == present_close)].index
        shifts_sunday.loc[present_index, delivery_num] = res.x[i]

shifts_monday.to_csv("./proceeded/shifts/final_monday.csv", sep = ",", index = False)
shifts_tuesday.to_csv("./proceeded/shifts/final_tuesday.csv", sep = ",", index = False)
shifts_wednesday.to_csv("./proceeded/shifts/final_wednesday.csv", sep = ",", index = False)
shifts_thursday.to_csv("./proceeded/shifts/final_thursday.csv", sep = ",", index = False)
shifts_friday.to_csv("./proceeded/shifts/final_friday.csv", sep = ",", index = False)
shifts_saturday.to_csv("./proceeded/shifts/final_saturday.csv", sep = ",", index = False)
shifts_sunday.to_csv("./proceeded/shifts/final_sunday.csv", sep = ",", index = False)