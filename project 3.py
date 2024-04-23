from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler
import requests
import operator
import io

tg_token = "7133515232:AAHz_-PxiVAb86A-j_FwbrRAQ0VNa0KL0Jg"
request_args = {"proxy_url": "socks5h://127.0.0.1:9050"}
initial_state = 1


class YaMapMap(object):
    def __init__(self, ll: tuple, spn: tuple, layer_comb: int, points: tuple = (), img_size: tuple = (600, 450)):
        self.server_address = "https://static-maps.yandex.ru/1.x/"
        self.aval_layers = (("map",), ("sat",), ("sat", "skl"), ("sat", "trf", "skl"), ("map", "trf", "skl"))
        if -180 <= ll[0] <= 180 and -90 <= ll[1] <= 90:
            self.ll = ll
        else:
            raise ValueError()
        self.spn = spn
        if 0 <= layer_comb < 5:
            self.layer_comb = layer_comb
        else:
            raise ValueError()
        if all(map(lambda point: isinstance(point, YaMapPoint), points)):
            self.points = points
        else:
            raise TypeError()
        if 1 <= img_size[0] <= 600 and 1 <= img_size[1] <= 450:
            self.img_size = img_size
        else:
            raise ValueError()

    def get_image(self, autopos=False):
        location_string = ",".join(map(str, self.ll))
        layer_string = ",".join(self.aval_layers[self.layer_comb])
        point_strings = "~".join(map(lambda point: point.get_string(), self.points))
        size_string = ",".join(map(str, self.img_size))
        zoom_level_string = ",".join(map(str, self.spn))
        request_parameters = {}
        request_parameters["l"] = layer_string
        request_parameters["spn"] = zoom_level_string
        request_parameters["size"] = size_string
        if not autopos or not point_strings:
            request_parameters["ll"] = location_string
        if point_strings:
            request_parameters["pt"] = point_strings
        response = requests.get(self.server_address, request_parameters)
        if not response:
            print(response.request.body)
            self.err = True
            self.status_code = response.status_code
            self.reason = response.reason
            return
        self.err = False
        return response.content

    def move_map(self, ll_delta: tuple):
        new_ll = tuple(map(operator.add, self.ll, ll_delta))
        if -180 <= new_ll[0] <= 180 and -90 <= new_ll[1] <= 90:
            self.ll = new_ll

    def zoom_in(self):
        if self.scale < 17:
            self.scale += 1

    def zoom_out(self):
        if self.scale > 0:
            self.scale -= 1

    def set_points(self, points: tuple):
        self.points = points

    def req_status(self):
        return (self.status_code, self.reason)

    def set_scale(self, scale: int):
        if 0 <= scale <= 17:
            self.scale = scale

    def set_ll(self, ll: tuple):
        if -180 <= ll[0] <= 180 and -90 <= ll[1] <= 90:
            self.ll = ll

    def cycle_layers(self):
        self.layer_comb = (self.layer_comb + 1) % len(self.aval_layers)

    def get_scale(self):
        return self.scale

    def get_size(self, point):
        return self.img_size

    def is_error(self):
        return self.err


class YaMapPoint(object):
    def __init__(self, ll: tuple, style: str, color: str = "", size: int = "", content: int = ""):
        self.ll = ll
        self.style = style
        self.color = color
        self.size = size
        self.content = content

    def get_string(self):
        return f"{self.ll[0]},{self.ll[1]},{self.style}{self.color}{self.size}{self.content}"


class YaMapSearch(object):
    def __init__(self):
        self.err = False
        self.server_addr = "https://geocode-maps.yandex.ru/1.x/"
        self.apikey = "40d1649f-0493-4b70-98ba-98533de7710b"

    def search_address(self, address: str):
        self.geocode = address
        self.kind = ""
        self._request()

    def search_ll(self, ll: tuple, kind=""):
        self.geocode = ",".join(map(str, ll))
        self.kind = kind
        self._request()

    def get_ll(self, index: int):
        feature_member = self.json_resp["response"]["GeoObjectCollection"]["featureMember"][index]
        ll_string = feature_member["GeoObject"]["Point"]["pos"]
        return tuple(map(float, ll_string.split()))

    def get_address(self, index: int):
        feature_member = self.json_resp["response"]["GeoObjectCollection"]["featureMember"][index]
        return feature_member["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"]

    def get_text(self, index: int):
        feature_member = self.json_resp["response"]["GeoObjectCollection"]["featureMember"][index]
        return feature_member["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]

    def get_point(self, index: int, style: str, color: str = "", size: int = "", content: int = ""):
        ll = self.get_ll(index)
        return YaMapPoint(ll, style, color, size, content)

    def get_postal_code(self, index: int):
        feature_member = self.json_resp["response"]["GeoObjectCollection"]["featureMember"][index]
        try:
            return feature_member["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        except KeyError:
            return ""

    def get_results_count(self):
        return int(
            self.json_resp["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]["found"])

    def get_spn(self, index: int):
        feature_member = self.json_resp["response"]["GeoObjectCollection"]["featureMember"][index]
        toponym_delta_1 = list(map(
            float, feature_member["GeoObject"]["boundedBy"]["Envelope"]['lowerCorner'].split()))
        toponym_delta_2 = list(map(
            float, feature_member["GeoObject"]["boundedBy"]["Envelope"]['upperCorner'].split()))
        d1 = str(abs(toponym_delta_1[0] - toponym_delta_2[0]))
        d2 = str(abs(toponym_delta_1[1] - toponym_delta_2[1]))
        return (d1, d2)

    def _request(self):
        req_params = {
            "apikey": self.apikey,
            "geocode": self.geocode,
            "format": "json"
        }
        if self.kind:
            req_params["kind"] = self.kind
        response = requests.get(self.server_addr, req_params)
        if not response:
            print("here")
            self.err = True
            self.status_code = response.status_code
            self.reason = response.reason
        self.err = False
        self.json_resp = response.json()

    def is_error(self):
        return self.err

    def req_status(self):
        return (self.status_code, self.reason)


def start(update, context):
    update.message.reply_text(f"Bot started\nEnter your request")
    return initial_state


def stop(update, context):
    keyboard = [["/start"]]
    update.message.reply_text("See you later!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ConversationHandler.END


def error(update, context):
    update.message.reply_text(
        f"Update\n{update} caused\n{repr(context.error)}")


def search(update, context):
    print("search start")
    search = YaMapSearch()
    msg_text = update.message.text
    update.message.reply_text("Поиск...")
    search.search_address(msg_text)
    if search.is_error():
        print("search error")
        status = search.req_status()
        update.message.reply_text(f"Ошибка при поиске!\n"
                                  f"Код: {status[0]}\n"
                                  f"Статус: {status[1]}")
        return
    if not search.get_results_count():
        update.message.reply_text("Ничего не найдено")
        return
    ll = search.get_ll(0)
    spn = search.get_spn(0)
    address = search.get_address(0)
    point = search.get_point(0, "comma")
    ya_map = YaMapMap(ll, spn, 0, (point,))
    map_bytes = ya_map.get_image()
    if ya_map.is_error():
        status = ya_map.req_status()
        update.message.reply_text(f"Произошла ошибка при получении карты!\n"
                                  f"Код: {status[0]}\n"
                                  f"Статус: {status[1]}")
        return
    map_filelike = io.BytesIO(map_bytes)
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id, map_filelike, caption=address)


def main():
    updater = Updater(tg_token, request_kwargs=request_args, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start, pass_chat_data=True)],
        states={initial_state: [MessageHandler(filters.text, search)]}, fallbacks=[CommandHandler("stop", stop)])

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
