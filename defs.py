import json
import random
import requests

API = "https://ow-api.com/v1/stats/pc/eu"


def get_stats(battletag):
    response = requests.get(f"{API}/{battletag}/profile")
    if not response:
        return 0
    return response.json()



def crop_centre(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_centre(pil_img, min(pil_img.size), min(pil_img.size))


def generate_quiz(type):
    with open("./static/json/quiz.json", encoding="utf8") as js:
        js = json.load(js)
        sound = js["soundtrack"]
        photo = js["location"]
    if type == "sound":
        quests = list(random.sample(list(zip(list(sound.values()), sound.keys())), 5))
        idk = []
        for i in range(5):
            answ = [quests[i][1]]
            temp = list(sound.keys())
            temp.remove(answ[0])
            answ.extend(random.sample(temp, 3))
            random.shuffle(answ)
            idk.append(answ)
    elif type == "photo":
        quests = list(random.sample(list(zip(list(map(lambda x: random.choice(x), list(photo.values()))), sound.keys())), 5))
        idk = []
        for i in range(5):
            answ = [quests[i][1]]
            temp = list(photo.keys())
            temp.remove(answ[0])
            answ.extend(random.sample(temp, 3))
            random.shuffle(answ)
            idk.append(answ)
    return [quests, idk]
