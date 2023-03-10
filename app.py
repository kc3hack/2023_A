import os
from utils.myGPT import generate_text
from src.chatcat import ChatCat
import openai

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, LocationMessage,
    PostbackEvent,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction

app = Flask(__name__)
# 送られてきたグループIDとChatCatのインスタンスを紐付ける辞書
chatcat_dict = {}

# secrets/openai_API_KEY.txtにAPIキーを保存して、それを読み込む
openai.api_key = open("secrets/openai_API_KEY.txt").read().strip()

# secrets/line_channel_access_token.txtにアクセストークンを保存して、それを読み込む
line_bot_api = LineBotApi(open("secrets/line_channel_access_token.txt").read().strip())
handler = WebhookHandler(open("secrets/line_channel_secret.txt").read().strip())

@app.route("/")
def test():
    return "OK!!!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    receive_message(event)

@handler.add(PostbackEvent)
def handle_postback(event):
    receive_message(event)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    receive_message(event)

def receive_message(event):
    chatcat = get_chatcat(event)
    chatcat.run(event)
    line_bot_api.reply_message(event.reply_token,chatcat.replies)


def get_chatcat(event):
    # グループチャットの場合
    if (event.source.type == "group"):
        # グループIDが登録されていなかったら、ChatCatのインスタンスを作成して、グループIDと紐付ける
        if event.source.group_id not in chatcat_dict:
            chatcat_dict[event.source.group_id] = ChatCat()

        # グループIDに紐付けられたChatCatのインスタンスを取得
        chatcat = chatcat_dict[event.source.group_id]
    # 個チャの場合
    if (event.source.type == "user"):
        if event.source.user_id not in chatcat_dict:
            chatcat_dict[event.source.user_id] = ChatCat()

        # 個人IDに紐付けられたChatCatのインスタンスを取得
        chatcat = chatcat_dict[event.source.user_id]
    return chatcat


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))