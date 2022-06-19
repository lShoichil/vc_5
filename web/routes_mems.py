import random

from flask import Blueprint, redirect, url_for, jsonify, request
import vk

from . import db
from .models import Mems
from .config import access_token

mem_routes = Blueprint("mem", __name__, template_folder="templates")


@mem_routes.route("/load_mems", methods=["POST"])
def load_mems():
    url_albom_mems = request.form["url"]

    session = vk.Session()
    api = vk.API(session)

    album_id = url_albom_mems.split("/")[-1].split("_")[1]
    owner_id = url_albom_mems.split("/")[-1].split("_")[0].replace("album", "")

    mems = api.photos.get(
        v=5.131,
        album_id=album_id,
        owner_id=owner_id,
        access_token=access_token,
        extended=1,
        rev=1,
    )

    for image in mems["items"]:
        vk_links = f'https://vk.com/id{image["user_id"]}'
        vk_id = image["user_id"]
        likes_parse = image["likes"]["count"]
        url_image = image["sizes"][-1]["url"]

        new_mem = Mems(
            vk_links=vk_links,
            vk_id=vk_id,
            likes_parse=likes_parse,
            url_image=url_image,
            likes_count=0,
        )
        db.session.add(new_mem)
        db.session.commit()

    return redirect(url_for("mem.get_all_mems"))


@mem_routes.route("/get_all_mems", methods=["GET"])
def get_all_mems():
    Sort_Mems = db.session.query(Mems).order_by(Mems.likes_count).all()
    reversed(Sort_Mems)

    output = []

    for mem in Sort_Mems:
        mem_data = {
            "id": mem.id,
            "likes_count": mem.likes_count,
            "url_image": mem.url_image,
        }
        output.append(mem_data)

    if Sort_Mems:
        return jsonify({"mems": output})
    else:
        return jsonify({"message": "У вас нет мемов :("})


@mem_routes.route("/delete_all_mems", methods=["DELETE"])
def delete_all_mems():
    mems = Mems.query.all()
    if not mems:
        return jsonify({"message": "Мемы уже удалены"})

    for mem in mems:
        db.session.delete(mem)
    db.session.commit()

    return jsonify({"message": "Все мемы были удалены"})


count_mems = 48
it_first = True


@mem_routes.route("/likes_or_skip", methods=["POST"])
def likes_or_skip():
    global count_mems, it_first
    rows = db.session.query(Mems).count()

    if rows == 0:
        return jsonify({"message": "У вас нет мемов:("})

    if count_mems == 0 and it_first:
        it_first = False
        mem_first = Mems.query.all()[0]
        message = f"Это первый мем из {rows}! Лайкните или пропустите?"
        return jsonify({"message": message, "url_mem_now": mem_first.url_image})

    l_or_p = request.form["l_or_p"]

    if rows == count_mems + 1:
        count_mems = 0
        it_first = True
        mem_last = Mems.query.all()[count_mems - 1]
        if l_or_p == '1':
            mem_last.likes_count += 1
            db.session.commit()

        return jsonify(
            {
                "message": "Это был последний! Больше мемов у нас нет. :( "
                           "При следующем запросе вы начнёте сначала. Так же продвижение поста приостановленно"
            }
        )

    count_mems += 1
    mem_now = Mems.query.all()[count_mems]

    url_mem_now = mem_now.url_image


    if l_or_p == "1":  # Лайк

        Mems.query.all()[count_mems - 1].likes_count += 1
        db.session.commit()

        message = f"Вы лайкнули {count_mems} мем из {rows}! Вы сейчас на {count_mems + 1} меме."
        return jsonify({"message": message, "url_mem_now": url_mem_now})
    elif l_or_p == "0":  # Пропуск
        message = f"Вы пропустили {count_mems} мем из {rows}! Вы сейчас на {count_mems + 1} меме."
        return jsonify({"message": message, "url_mem_now": url_mem_now})


@mem_routes.route("/test_for_third")
def test_for_third():

    mems = Mems.query.all()

    if not mems:
        return jsonify({"message": "Мемов для накрутки нет:("})

    for mem in mems:
        tt = random.randint(1, 3)
        if tt != 1:
            mem.likes_count = random.randint(25, 1000)
    db.session.commit()
    return jsonify({"message": "Успешно"})
