import random
from linebot.models import (
    PostbackAction, QuickReplyButton, QuickReply,MessageAction
)
omikuji_list = ['大吉', '吉', '中吉', '小吉']

def omikuji(chatcat,event):
    if event.type == "message" and event.message.text == 'おみくじ':
        # 例 ボット起動時に表示されるカルーセル
        text = 'くじを引くにゃ！'
        items = [
            QuickReplyButton(
                action = MessageAction(label = '1', text = '1')
            ),
            QuickReplyButton(
                action = MessageAction(label = '2', text = '2')
            ),
            QuickReplyButton(
                action = MessageAction(label = '3', text = '3')
            ),
            QuickReplyButton(
                action = MessageAction(label = '4', text = '4')
            )
        ]
        chatcat.add_quick_reply(text, items)
    else:
        chatcat.talk(random.choice(omikuji_list))
