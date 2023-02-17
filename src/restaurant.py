def restaurant_recomend(chatcat,event):
    try:
        flag1,flag2,flag3, = chatcat.data["restaurant_data"]
    except:
        flag1,flag2,flag3 = False,False,False

    if event.type == "postback":
        chatcat.talk("飲食店のおすすめを検索します。")
        chatcat.talk("どのようなお店をお探しですか？")
    else:
        chatcat.talk(f"「{event.message.text}」のおすすめを検索します。")
        chatcat.talk("こちらです。")

    chatcat.data["restaurant_data"] = [flag1,flag2,flag3]