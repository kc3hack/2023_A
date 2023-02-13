import openai

# secrets/openai_API_KEY.txtにAPIキーを保存して、それを読み込む
openai.api_key = open("secrets/openai_API_KEY.txt").read().strip()

def generate_text(prompt, api_key):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message




import os

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

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

bot = False
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    global bot
    
    if event.message.text == "終了":
        bot = False
        reply = "終了しました。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
    
    if bot == True:
        api_key = openai.api_key
        prompt = event.message.text
        reply = generate_text(prompt,api_key)
        reply = reply.strip()
        print(reply)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

    if event.message.text == "起動":
        bot = True
        reply = "起動します。爆発まで．．．．"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))