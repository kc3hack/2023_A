# LINEBotのメインクラス
import os

from meeting import meeting_recomend
from restaurant import restaurant_recomend
from apparel import apparel_recomend
from other import other_recomend
from flask import Flask, request, abort

from myGPT import generate_text

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

place_list = ['待ち合わせ', '飲食店', 'アパレル', 'その他']

class ChatCat():
    is_running = False          # ボットを起動中かどうか
    channel_access_token = None # チャンネルアクセストークン
    channel_secret = None       # チャンネルシークレット
    line_bot_api = None         # LINEBotのAPIインスタンス
    handler = None              # LINEBotのハンドラインスタンス

    def __init__(self, channel_access_token):
        self.channel_access_token = channel_access_token
        self.line_bot_api = LineBotApi(channel_access_token)
        self.handler = WebhookHandler(channel_access_token)

    def run(self, event):
        if event.message.text == 'start':
            return self.start()
        elif event.message.text == 'stop':
            return self.stop()
        elif self.is_running:
            return self.reply(event)
        else:
            return None

    def start(self):
        is_running = True
        return 'ボットを起動しました'

    def stop(self):
        is_running = False
        return 'ボットを停止しました'

    def reply(self, event):
        # 各機能ごとの処理に割り振る
        message = event.message.text.split(' ')
        if message[0] in place_list:
            return self.recommend(event)
        elif message[0] == 'おみくじ':
            return self.omikuji(event)
        elif message[0] == 'ルーレット':
            return self.roulette(event)
        else:
            return self.chat(event)

    # おすすめ検索機能
    def recommend(self, event, message):
        # 待ち合わせ、飲食店、アパレル、その他で分類
        if event.message.text == '待ち合わせ':
            return meeting_recomend(self,event,message)
        elif event.message.text == '飲食店':
            return restaurant_recomend(self,event,message)
        elif event.message.text == 'アパレル':
            return apparel_recomend(self,event,message)
        else:
            return other_recomend(self,event,message)

    # おみくじ機能
    def omikuji(self, event):
        pass

    # ルーレット機能
    def roulette(self, event):
        pass

    # 会話機能
    def chat(self, event):
        return generate_text(event.message.text)