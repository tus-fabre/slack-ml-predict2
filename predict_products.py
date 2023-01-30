#!/usr/bin/env python
# coding: utf-8
#
# [FILE] predict_products.py
#
# [DESCRIPTION]
#  商品（ドリンク）の売上を予測するSlackアプリトップファイル
#
# [NOTES]
#

import os,sys
from pathlib import Path
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# BOTトークンからアプリを初期化する
slack_token=os.environ.get("SLACK_BOT_TOKEN")
if slack_token == None:
    print("環境変数が設定されていません")
    sys.exit()
app = App(token=slack_token)

# ここのパッケージは重いので、ここでロードする
from drink_model import addDataFrame, createDataFrameInfo, createModel, predictProducts
from utils.modal_view import modalView

# アプリトークン
app_token = os.environ["SLACK_APP_TOKEN"]
# ユーザートークン：ファイルの内容を取得するため用いる
user_token = os.environ.get("SLACK_USER_TOKEN")
# ローカルフォルダー
csv_folder = os.environ.get("LOCAL_FOLDER")
# 商品販売データフレーム情報を作成する
df_info = createDataFrameInfo("DATA/drink_sales.csv")
# 商品販売モデルを作成する
model = createModel(df_info["dataframe"])

#
# [EVENT] message
#
# [DESCRIPTION]
#  次のメッセージを受信したときのリスナー関数
#   Unhandled request ({'type': 'event_callback', 'event': {'type': 'message', 'subtype': 'file_share'}})
#
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

#
# [SLASH COMMAND] /drinks
#
# [DESCRIPTION]
#  天気と気温を問い合わせるメニューを表示する
#
# [NOTES]
#
@app.command("/drinks")
def message_predict(ack, respond):
    ack()
    
    # メニューを作成する
    blocks = createPredictionMenu()
    print(blocks)
    respond(blocks)

#
# [EVENT] file_shared
#
# [DESCRIPTION]
#  ファイルを共有したときに起動するリスナー関数
#  追加学習を行う
#
# [NOTES]
#  対応可能なファイルタイプ：csv
#
@app.event("file_shared")
def file_shared(payload, client, ack, say):
    ack()
    
    # アップロードしたファイルのIDを取得する
    file_id = payload.get('file').get('id')
    
    # ファイル情報を取得する
    file_info = client.files_info(file = file_id).get('file')
    url = file_info.get('url_private')
    csv_path = csv_folder + "/" + file_info.get('title')
    file_type = file_info.get('filetype')

    if file_type != 'csv':
        say(f"サポートしていないファイル形式です： {file_type}")
        return

    # ファイルの内容を取得する
    resp = requests.get(url, headers={'Authorization': 'Bearer %s' % user_token})
    
    # 一時的にファイルをローカルフォルダーに保存する
    save_file = Path(csv_path)
    save_file.write_bytes(resp.content)

    # 追加したファイルの内容を学習モデルに追加する
    addDataFrame(df_info, csv_path)
    global model
    model = createModel(df_info["dataframe"])

    os.remove(csv_path) 
   
#
# [ACTION METHOD] action-select-weather
#
# [DESCRIPTION]
#  メニューから天気を選択したときのアクション関数
#
# [INPUTS]
#
# [OUTPUTS]
#  body['actions'][0]['selected_option']['value'] - 天気のID番号
#
# [NOTES]
#
@app.action("action-select-weather")
def action_select_weather(body, ack):
    ack()
    weather = body['actions'][0]['selected_option']['value']
    print("[Weather] " + str(weather) )

#
# [ACTION METHOD] action-predict-sales
#
# [DESCRIPTION]
#  販売予測ボタンをクリックしたときのアクション
#
# [INPUTS]
#  body['state']['values']['temparature']['action-temparature']['value'] - 記入した気温
#  body['state']['values']['weather']['action-select-weather']['selected_option']['value'] - 選択した天気ID
#
# [OUTPUTS]
#  
# [NOTES]
#
@app.action("action-predict-sales")
def action_predict_sales(body, ack, client):
    ack()
    # 入力値の取得
    temp = body['state']['values']['temparature']['action-temparature']['value']
    weather = body['state']['values']['weather']['action-select-weather']['selected_option']
    
    # 入力値の存在チェック
    msg = None
    if temp == None:
        msg = "気温が指定されていません"
    if weather == None:
        msg = "天気が指定されていません"

    if msg != None:
        viewObj = modalView("注意", msg)
        client.views_open(trigger_id=body["trigger_id"], view=viewObj)
        return

    # 天気、気温から商品を予測する
    weather = weather['value']
    product_id = predictProducts(model, temp, weather)
    
    # 商品番号から名称に変換する
    product_name = "？"
    for key, value in df_info["products"].items():
        if product_id == value:
            product_name = key

    # 予測した商品をモーダルビューで表示する
    viewObj = modalView("予測結果", "売れそうな商品：" + product_name)
    client.views_open(trigger_id=body["trigger_id"], view=viewObj)

#
# [FUNCTION] createPredictionMenu()
#
# [DESCRIPTION]
#  気温と天気を入力し、販売予測を行うUI群を作成する
#
# [INPUTS] None
#
# [OUTPUTS]
#  {blocks:<JSON>}
#
# [NOTES]
#
def createPredictionMenu():

    blocks = []
    # ヘッダーを作成する
    objHeader = {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "商品の販売予測"
      }
    }
    blocks.append(objHeader)

    # 天気選択メニューを作成する
    weathers = []
    for key, value in df_info["weathers"].items(): # <天気>と<天気番号>のペアからなるリストを作成する
        w_structure = {
            "text":{
                "type": "plain_text", 
                "text": key
            },
            "value": str(value)
        }
        weathers.append(w_structure)
        
    objWeather = {
        "type": "input",
        "block_id": "weather",
        "element": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "天気を選択"
            },
            "options": weathers,
            "action_id": "action-select-weather"
        },
        "label": {
            "type": "plain_text",
            "text": "天気"
        }
    }
    blocks.append(objWeather)

    # 気温入力欄を作成する
    objTemp = {
		"type": "input",
        "block_id": "temparature",
		"element": {
			"type": "plain_text_input",
			"action_id": "action-temparature"
		},
		"label": {
			"type": "plain_text",
			"text": "気温"
		}
	}
    blocks.append(objTemp)
    
    # 区切り線を引く
    objDivider = {
      "type": "divider"
    }
    blocks.append(objDivider)

    # ボタンを配置する
    objActions = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "販売予測"
                },
                "style": "primary",
                "value": "predict", # Not used
                "action_id": "action-predict-sales"
            }
        ]
    }
    blocks.append(objActions)

    retVal = {
        "blocks": blocks
    }

    return retVal
 
#
# Start the Slack app
#
if __name__ == "__main__":
    print('⚡️Prediction App starts...')
    SocketModeHandler(app, app_token).start()

#
# END OF FILE
#