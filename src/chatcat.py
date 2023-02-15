# LINEBotのメインクラス
import os

from src.meeting import meeting_recomend
from src.restaurant import restaurant_recomend
from src.apparel import apparel_recomend
from src.other import other_recomend
from flask import Flask, request, abort

from utils.myGPT import generate_text

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

place_list = ['待ち合わせ', '飲食店', 'アパレル', 'その他']

class ChatCat():
    replies = list()
    is_running = False          # ボットを起動中かどうか

    def __init__(self):
        self.talk('こんにちは！')

    def run(self, event):
        if event.message.text == 'start':
            self.start()
        elif event.message.text == 'stop':
            self.stop()
        elif self.is_running:
            self.reply(event)

    def start(self):
        self.is_running = True
        self.talk('ボットを起動しました')

    def stop(self):
        self.is_running = False
        self.talk('ボットを停止しました')

    def reply(self, event):
        # 各機能ごとの処理に割り振る
        message = event.message.text.split(' ')
        if message[0] in place_list:
            self.recommend(event)
        elif message[0] == 'おみくじ':
            self.omikuji(event)
        elif message[0] == 'ルーレット':
            self.roulette(event)
        else:
            self.chat(event)

    # おすすめ検索機能
    def recommend(self, event):
        # 待ち合わせ、飲食店、アパレル、その他で分類
        if event.message.text == '待ち合わせ':
            meeting_recomend(self,event)
        elif event.message.text == '飲食店':
            restaurant_recomend(self,event)
        elif event.message.text == 'アパレル':
            apparel_recomend(self,event)
        else:
            other_recomend(self,event)

    # おみくじ機能
    def omikuji(self, event):
        pass

    # ルーレット機能
    def roulette(self, event):
        pass

    # 会話機能
    def chat(self, event):
        self.talk(generate_text(event.message.text))

    def talk(self, text):
        self.replies.append(TextSendMessage(text=text))