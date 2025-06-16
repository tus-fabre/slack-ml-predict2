#!/usr/bin/env python
# coding: utf-8
#
# [FILE] drink_model.py
#
# [DESCRIPTION]
#  気温、天気から売れる飲み物を予測するモデル作成に関わる関数
#
# [NOTES]
#  必要なソフトウェア
#  $ pip install xgboost
#  $ pip install pandas
#
# 参考
#  https://zenn.dev/nishimoto/articles/4f24d5be7ac463
#
import warnings
import pandas as pd
import xgboost as xgb

warnings.filterwarnings("ignore") # 警告文無視用

#
# [FUNCTION] addDataFrame()
#
# [DESCRIPTION]
#  トレーニング用モデルに追加する
# 
# [INPUTS]
#  df_info - 既に作成されたデータフレーム情報
#            {dataframe:<DataFrame>, weathers:{<天気>:<天気番号>, ...}, products:{<商品名>:<商品番号>, ...}}
#  train_file - 追加するトレーニング用CSVファイル
#
# [OUTPUTS] None
#
def addDataFrame(df_info, train_file):
    df_train = pd.read_csv(train_file)
    print(df_train)

    weathers = df_info["weathers"]
    weather_id = len(weathers) # 新規天気番号
    for w in df_train["天気"]:
        if w not in weathers: # 存在チェック
            weathers[w] = weather_id
            weather_id += 1
    print(weathers)
    
    products = df_info["products"]
    product_id = len(products) # 新規商品番号
    for p in df_train["商品"]:
        if p not in products:  # 存在チェック
            products[p] = product_id
            product_id += 1
    print(products)
    
    # トレーニングの前処理
    df_train["天気"] = df_train["天気"].replace(weathers)
    df_train["気温"] = df_train["気温"].fillna(df_train["気温"].mean())
    df_train["商品"] = df_train["商品"].replace(products)
    df_train = pd.get_dummies(df_train)
    
    # データフレームを追加する
    #df_info["dataframe"] = df_info["dataframe"].append(df_train)
    # pandas 2.0で廃止された機能
    df_info["dataframe"] = pd.concat([df_info["dataframe"], df_train], ignore_index=True)
    df_info["weathers"] = weathers
    df_info["products"] = products
    print(df_info["dataframe"])

#
# [FUNCTION] createDataFrameInfo()
#
# [DESCRIPTION]
#  トレーニング用ファイルからデータフレーム情報を生成する
# 
# [INPUTS]
#  train_file - トレーニング用CSVファイル
# 
# [OUTPUTS]
# { dataframe:<DataFrame>, 
#   weathers:{<天気>:<天気番号>, ...},
#   products:{<商品名>:<商品番号>, ...} }
#
def createDataFrameInfo(train_file):
    df_info = {}
    df_train = pd.read_csv(train_file)
    print(df_train)

    # 天気情報を作成する
    weathers = {}
    weather_id = 0
    for w in df_train["天気"]:
        if w not in weathers: # 存在チェック
            weathers[w] = weather_id
            weather_id += 1
    print(weathers)

    # 商品情報を作成する
    products = {}
    product_id = 0
    for p in df_train["商品"]:
        if p not in products:  # 存在チェック
            products[p] = product_id
            product_id += 1
    print(products)
    
    # トレーニングの前処理
    df_train["天気"] = df_train["天気"].replace(weathers)
    df_train["気温"] = df_train["気温"].fillna(df_train["気温"].mean())
    df_train["商品"] = df_train["商品"].replace(products)
    df_train = pd.get_dummies(df_train)

    # 返り値を構成する
    df_info["dataframe"] = df_train.copy() # 複製を設定
    df_info["weathers"] = weathers
    df_info["products"] = products
    
    return df_info

#
# [FUNCTION] createModel()
#
# [DESCRIPTION]
#  データフレームからモデルを生成する
# 
# [INPUTS]
#   df_train - トレーニング用CSVファイルから生成したデータフレーム
#
# [OUTPUTS]
#  決定木の勾配ブースティングアルゴリズムに基づく分類モデル
#
def createModel(df_train):

    # 説明変数、目的変数への分割
    train_y = df_train["商品"]
    train_x = df_train.drop("商品", axis=1)

    # 機械学習アルゴリズムの宣言と学習
    model = xgb.XGBClassifier()
    model.fit(train_x, train_y)
    
    return model

#
# [FUNCTION] predictProducts()
#
# [DESCRIPTION]
#  Predict the best-selling drink from the temparature and weather
# 
# [INPUTS]
#  model - createModel()の返り値（分類モデル）
#  temp  - 気温
#  weather - 天気（番号）
#
# [OUTPUTS]
#  商品番号
#
def predictProducts(model, temp, weather):
    # 天気と気温から構成されるデータフレームを作成する
    input=[[int(temp), int(weather)]]
    row = ["Row1"]
    columns =["気温", "天気"]
    df = pd.DataFrame(data=input, index=row, columns=columns)

    # 予測結果を取得
    result = model.predict(df)
    print("売れるであろう商品：" + str(result))
        
    return result[0]

#
# END OF FILE
#