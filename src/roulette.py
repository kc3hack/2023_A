import random
def roulette(chatcat,event):
    try:
        search_results = chatcat.data["search_results"]
    except:
        search_results = []
    if len(search_results) == 0:
        chatcat.talk("何を選べばいいかわからないにゃ")
    else:
        place_name_list = ""
        for data in search_results:
            place_name_list += data["name"] + "\n"
        chatcat.talk(f"{place_name_list}のルーレットを回してみたにゃ")
        chatcat.talk(search_results[random.randint(0,len(search_results)-1)]["name"] + "にゃ")