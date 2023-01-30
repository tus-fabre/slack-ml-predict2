#!/usr/bin/env python
# coding: utf-8
#
# [FILE] modal_view.py
#
# [DESCRIPTION]
#   モーダル画面に関わる便利な関数を定義する
#

#
# [FUNCTION] modalView()
#
# [DESCRIPTION]
#  モーダルビューを表示するためのJSON構造を生成する
# 
# [INPUTS]
#  title - モーダル画面の見出し
#  text  - モーダル画面のテキスト
#
# [OUTPUTS]
#  {"type": "modal", "title":...}
#
def modalView(title, text):

    objView = {
        "type": "modal",
        #"callback_id": "action-none",
        "title": {
            "type": "plain_text",
            "text": title
        },
        "blocks": [
		    {
			    "type": "section",
			    "text": {
				    "type": "plain_text",
				    "text": text
			    }
		    }
        ]
    }
   
    return objView

#
# END OF FILE
#