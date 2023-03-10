import random
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction

omikuji_list = ['大吉', '吉', '中吉', '小吉']

def omikuji(chatcat, event):
    # LINE Messaging APIから送信されたメッセージがテキストメッセージの場合
    if isinstance(event.message, TextMessage):
        text = event.message.text

        # ユーザーが「おみくじ」と送信した場合
        if text == "おみくじ":
            # Quick Replyを使ってユーザーに1~4の番号から選択するように促す
            items=[
                QuickReplyButton(action=MessageAction(label="1", text="1")),
                QuickReplyButton(action=MessageAction(label="2", text="2")),
                QuickReplyButton(action=MessageAction(label="3", text="3")),
                QuickReplyButton(action=MessageAction(label="4", text="4"))
            ]
            chatcat.add_quick_reply("おみくじの番号を選ぶにゃ！", items)

        # ユーザーが1~4の番号を選択した場合
        elif text in ["1", "2", "3", "4"]:
            # ランダムにおみくじ結果を返信する
            omikuji_results = ["大吉", "中吉", "小吉", "凶"]
            result = random.choice(omikuji_results)
            if result == "大吉":
                chatcat.talk("大吉！！！\nにゃーん！おめでとにゃ！大吉だにゃ！これからも幸せがたくさんやってくるにゃ！")
            elif result == "中吉":
                chatcat.talk("中吉！！\nにゃ～ん、中吉にゃ！まあまあにゃ～！でも、気を抜かずに頑張っていけば、もっといいことがあるにゃ！")
            elif result == "小吉":
                chatcat.talk("小吉！\nにゃん、小吉にゃ…でも、小さな良いことが積み重なって、大きな幸せにつながるにゃ！頑張っていこうにゃ！")
            elif result == "凶":
                chatcat.talk("...凶...\nにゃああああ！凶にゃんて、こんなことにゃ負けないにゃ！一回振り直してみるにゃ！そして、頑張って良いことを引き寄せていこうにゃ！")
