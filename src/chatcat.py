# LINEBotのメインクラス
import os

from src.chat import chat
from src.omikuji import omikuji
from src.roulette import roulette
from src.meeting import meeting_recomend
from src.restaurant import restaurant_recomend
from src.apparel import apparel_recomend
from src.other import other_recomend
from flask import Flask, request, abort

from utils.myGPT import generate_text

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction

place_list = ['待ち合わせ', '飲食店', 'アパレル', 'その他']

class ChatCat():
    replies = list()
    is_running = False          # ボットを起動中かどうか
    data = dict()               # データを保存する辞書
    mode = "normal"
    # モード一覧
    # normal : 通常モード
    # omikuji : おみくじモード
    # roulette : ルーレットモード
    # meeting : 待ち合わせモード
    # restaurant : 飲食店モード
    # apparel : アパレルモード
    # other_recomend : その他モード

    def __init__(self):
        self.mode_dict = {
            "normal" : chat,
            "omikuji" : omikuji,
            "roulette" : roulette,
            "meeting" : meeting_recomend,
            "restaurant" : restaurant_recomend,
            "apparel" : apparel_recomend,
            "other" : other_recomend
        }
        self.talk('こんにちは！')

    def run(self, event):
        self.replies = list()
        if event.type == "message" and event.message.text == 'start':
            self.start()
        elif event.type == "message" and event.message.text == 'stop':
            self.stop()
        elif self.is_running:
            if event.type == "postback":
                self.mode = event.postback.data
            self.reply(event)

    def start(self):
        self.is_running = True
        self.talk('ボットを起動しました')
        self.make_start_carousel()

    def make_start_carousel(self):
        columns_list = []
        columns_list.append(
            CarouselColumn(
                thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                title="飲食店",
                text="指定された条件の飲食店を検索します",
                actions=[
                    PostbackAction(label="検索", data="restaurant"),
                    PostbackAction(label="ヘルプ", data="help")
                ]
            )
        )
        columns_list.append(
            CarouselColumn(
                thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                title="待ち合わせ場所",
                text="指定された条件の待ち合わせ場所を検索します",
                actions=[
                    PostbackAction(label="検索", data="apparel"),
                    PostbackAction(label="ヘルプ", data="help")
                ]
            )
        )

        self.add_carousel("スタート",columns_list)

    def stop(self):
        self.is_running = False
        self.talk('ボットを停止しました')

    def reply(self, event):
        self.mode_dict[self.mode](self, event)

    def talk(self, text):
        self.replies.append(TextSendMessage(text=text))

    def add_carousel(self,alt_text,columns):
        self.replies.append(TemplateSendMessage(alt_text=alt_text,template=CarouselTemplate(columns=columns)))