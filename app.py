import openai

openai.api_key = "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"

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

line_bot_api = LineBotApi('v6JcBNiQFQmHVK7qqXb87rcsVmM8QFXQqEDouXT0wWOt+8lAcaOJ4ieOdlUcHmV+qXfvETZM84p/cC8aiU+0B1/iJDkdqNJm58awIYI0hcjpFejLNIjBxBOn68QyLYGVamSSCSGFf7hi4c6KAKJA0AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6bd4bc0e7b73f5166b81e493b5bd5443')

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
        api_key = "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"
        prompt = event.message.text
        reply = generate_text(prompt,api_key)
        reply = reply.strip()
        print(reply)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

    if event.message.text == "起動":
        bot = True
        reply = "起動しました。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))