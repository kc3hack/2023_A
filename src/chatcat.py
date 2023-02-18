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

from datetime import datetime, timedelta
import time
from pytz import timezone
JST = timezone('Asia/Tokyo')

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,DatetimePickerAction,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction

line_bot_api = LineBotApi(open("secrets/line_channel_access_token.txt").read().strip())
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
        if event.type == "message" and event.message.type == "text" and event.message.text == 'start':
            self.start()
        elif event.type == "message" and event.message.type == "text" and event.message.text == 'stop':
            self.stop()
        elif self.is_running:
            if event.type == "postback" and event.postback.data in self.mode_dict:
                self.mode = event.postback.data
            elif event.type == "message" and event.message.type == "text":
                if event.message.text == 'おみくじ':
                    self.mode = "omikuji"
                elif event.message.text == 'ルーレット':
                    self.mode = "roulette"
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
                    PostbackAction(label="使用", data="restaurant"),
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
                    PostbackAction(label="使用", data="meeting"),
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

    def add_quick_reply(self,text,items):
        self.replies.append(TextSendMessage(text=text,quick_reply=QuickReply(items=items)))

    def send_message_at_time(event, text, scheduled_time):
        now = datetime.now(JST)
        scheduled_time = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M').replace(tzinfo=JST)
        time_diff = (scheduled_time - now).total_seconds()

        if time_diff < 0:
            time.sleep(time_diff)
            if event.source.type == 'user':
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text=text))
            elif event.source.type == 'group':
                line_bot_api.push_message(event.source.group_id, TextSendMessage(text=text))