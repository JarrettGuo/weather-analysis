# -*- coding: utf-8 -*-
import datetime as DT
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error
from ProcessData import ProcessData
from sklearn.linear_model import LinearRegression


# 随机森林模型 - 训练并保存模型
def RandomForestRegressorModel(a="Model.pkl"):
    """
    :param a: 模型文件名
    :return:
        [socre: MAE评估结果,
        X_test: 预测数据集]
    """

    # 获取数据
    [X_train, X_valid, y_train, y_valid, X_test] = ProcessData()

    # 用XGB模型，不过用有bug
    # modelX = XGBRegressor(n_estimators=1000, learning_rate=0.05, random_state=0, n_jobs=4)
    # # model.fit(X_train_3, y_train_3)
    # # model.fit(X_train_2, y_train_2)
    # col = ["Ave_t", "Max_t", "Min_t", "Prec","SLpress", "Winddir", "Windsp", "Cloud"]
    # modelX.fit(X_train, y_train,
    #           early_stopping_rounds=5,
    #           eval_set=[(X_valid, y_valid)],
    #           verbose=False)

    # 随机树森林模型
    model = RandomForestRegressor(random_state=0, n_estimators=1001)
    # 训练模型
    model.fit(X_train, y_train)
    # 预测模型，用上个星期的数据
    preds = model.predict(X_valid)
    # 用MAE评估
    score = mean_absolute_error(y_valid, preds)
    # 保存模型到本地
    joblib.dump(model, a)
    # 返回MAE
    return [score, X_test]


# 线性回归模型 - 气温、降雨量预测
def LinearRegressionModel(city, a="Model.pkl"):
    # 获取数据
    [X_train, X_valid, y_train, y_valid, X_test] = ProcessData(city=city)

    # 训练模型
    model = LinearRegression()
    model.fit(X_train.iloc[::, :4], y_train.iloc[::, :4])

    # 预测结果
    y_pred = model.predict(X_test.iloc[::, :4])

    # # 评估模型
    # 用MAE评估
    score = mean_absolute_error(np.array(y_valid.iloc[:5, :4]), y_pred[:5])
    # 返回MAE
    print('score:', score)

    # 保存模型到本地
    joblib.dump(model, a)

    for a in range(1, 8):
        today = DT.datetime.now()
        time = (today + DT.timedelta(days=a)).date()
        print(time.year, '/', time.month, '/', time.day,
              ': 平均气温', y_pred[a][0],
              '最高气温', y_pred[a][1],
              '最低气温', y_pred[a][2],
              "降雨量", y_pred[a][3],
              )

    # 返回MAE
    return [score, X_test.iloc[::, :4]]


def run(city):
    # 城市id  广州59287 深圳59493 北京54511  上海58362
    # 如果是其他城市id 可以在"http://www.meteomanz.com/"上获取
    # r = RandomForestRegressorModel()
    r = LinearRegressionModel(city=city)

    # 训练并保存模型并返回MAE
    print("MAE:", r[0])
    # 读取保存的模型
    model = joblib.load('Model.pkl')

    # 最终预测结果
    preds = model.predict(r[1])

    # 打印结果到控制台
    print("未来7天预测")
    print(preds)

    result = []
    for a in range(1, 7):
        today = DT.datetime.now()
        time = (today + DT.timedelta(days=a)).date()
        print(time.year, '/', time.month, '/', time.day,
              ': 平均气温', preds[a][0],
              '最高气温', preds[a][1],
              '最低气温', preds[a][2],
              "降雨量", preds[a][3])
        if time.month < 10:
            month = '0{}'.format(time.month)
        else:
            month = '{}'.format(time.month)

        if time.day < 10:
            day = '0{}'.format(time.day)
        else:
            day = '{}'.format(time.day)

        if preds[a][3] < 1:
            jyl = 0
        else:
            jyl = preds[a][3]

        item = {'date': str(time.year) + '-' + month + '-' + day,
                'high': round(preds[a][1], 1),
                'low': round(preds[a][2], 1),
                'temp': round(preds[a][0], 1),
                'jyl': jyl}
        print(item)
        result.append(item)
    return result


if __name__ == '__main__':
    res = run(city_id='59493')
    print(res)
