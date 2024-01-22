# -*- coding: utf-8 -*-
import os
from Persistence import write
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# 功能: 数据预处理
def ProcessData(city):
    """
    :return:
        [X_train X训练数据集,
        X_valid X训练数据集的验证集,
        y_train Y训练数据集,
        y_valid Y训练数据集的验证集,
        imputed_X_test 预测数据集]
    """
    # 用近几年的数据做训练集
    # 如 [1,1], [20, 0]就是用2023年的今天的20天前到2023年的今天数据做训练集
    # 写入csv
    cur_date = str(datetime.now().date())
    data_path = os.path.join(os.getcwd(), 'data', cur_date)
    if not os.path.exists(data_path):
        print(f'init dir: {data_path}')
        os.makedirs(data_path)

    write([1, 1], [20, 0], os.path.join(data_path, "weather_train_train.csv"), city=city)
    write([1, 1], [0, 20], os.path.join(data_path, "weather_train_valid.csv"), city=city)
    write([0, 0], [20, 0], os.path.join(data_path, "weather_test.csv"), city=city)

    X_test = pd.read_csv(os.path.join(data_path, "weather_test.csv"))
    X_test['Time'] = pd.to_datetime(
        [t.split('/')[2] + "-" + t.split('/')[1] + "-" + t.split('/')[0] for t in X_test['Time']])
    X_test.sort_values('Time', ascending=True, inplace=True)
    X_test.set_index('Time', inplace=True)

    # 读取测试集和验证集
    X = pd.read_csv(os.path.join(data_path, "weather_train_train.csv"))
    X['Time'] = pd.to_datetime([t.split('/')[2] + "-" + t.split('/')[1] + "-" + t.split('/')[0] for t in X['Time']])
    X.sort_values('Time', ascending=True, inplace=True)
    X.set_index('Time', inplace=True)
    y = pd.read_csv(os.path.join(data_path, "weather_train_valid.csv"))
    y['Time'] = pd.to_datetime([t.split('/')[2] + "-" + t.split('/')[1] + "-" + t.split('/')[0] for t in y['Time']])
    y.sort_values('Time', ascending=True, inplace=True)
    y.set_index('Time', inplace=True)


    # 把全部丢失的数据都drop，MAE=3.7又高了，所以去掉了
    # dxtcol = [col for col in X_test.columns
    #           if X_test[col].isnull().all()]
    # dxcol = [col for col in X.columns
    #          if X[col].isnull().all()]
    # dycol = [col for col in y.columns
    #          if y[col].isnull().all()]
    # for a1 in [dxtcol, dxcol, dycol]:
    #     for a2 in a1:
    #         if a2 in X_test.columns:
    #             X_test = X_test.drop(a2, axis=1)
    #         if a2 in X.columns:
    #             X = X.drop(a2, axis=1)
    #         if a2 in y.columns:
    #             y = y.drop(a2, axis=1)
    # 数据归一化和标准化，无法还原不用
    # scaler = preprocessing.StandardScaler()
    # pars = [cols for cols in X.columns if cols != "Time"]
    # for data in [X, y, X_test]:
    #     for par in pars:
    #         data[par] = scaler.fit_transform(data[par].values.reshape(-1, 1))
    #         # temp = scaler.fit(data[par].values.reshape(-1, 1))
    #         # data[par] = scaler.fit_transform(data[par].values.reshape(-1, 1), temp)

    # 填充缺少的数值用方差，不清楚效果如何
    my_imputer = SimpleImputer()
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=0)
    imputed_X_train = pd.DataFrame(my_imputer.fit_transform(X_train))
    imputed_X_valid = pd.DataFrame(my_imputer.transform(X_valid))
    imputed_X_train.columns = X_train.columns
    imputed_X_valid.columns = X_valid.columns
    imputed_y_train = pd.DataFrame(my_imputer.fit_transform(y_train))
    imputed_y_valid = pd.DataFrame(my_imputer.transform(y_valid))
    imputed_y_train.columns = y_train.columns
    imputed_y_valid.columns = y_valid.columns
    imputed_X_test = pd.DataFrame(my_imputer.fit_transform(X_test))

    # 画折线图
    # sns.lineplot(data=X)
    # plt.show()
    # sns.lineplot(data=y)
    # plt.show()
    # sns.lineplot(data=X_test)
    # plt.show()
    # 返回分割后的数据集
    return [imputed_X_train, imputed_X_valid, imputed_y_train, imputed_y_valid, imputed_X_test]
