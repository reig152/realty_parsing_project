import requests
import re
from add_to_db import AddToDb


class SnapParser:
    """Парсер сайта snapspace."""
    def get_json(self):
        """Метод выполняющий запрос к api snapspace."""
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru,en;q=0.9',
            'Connection': 'keep-alive',
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
            'Origin': 'https://snapspace.ru',
            'Referer': 'https://snapspace.ru/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.167 YaBrowser/22.7.5.1027 Yowser/2.5 Safari/537.36',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Yandex";v="22"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        json_data = {
            'baseFilter': {
                'contractType': 'sale',
                'priceType': 'whole',
                'currency': 'rub',
                'realtyType': 'office',
            },
            'view': {
                'sort': 'date_change',
                'direction': 'desc',
                'limit': 15,
                'page': 1,
                'mode': 'tile',
            },
        }

        response = requests.post('https://api.snapspace.ru/search/search', headers=headers, json=json_data)
        db = response.json()
        return db

    def get_offer(self, item):
        """Метод обрабатывающий ответ от api."""
        offer = {}
        offer['offer_id'] = item['building']['buildingId']
        a = offer['offer_id']
        offer['link'] = f'https://snapspace.ru/buildings/{a}?searchId=2304'
        offer['address'] = item['building']['fullAddress']
        for x in item['offers']:
            offer['square'] = re.findall(r"\d+", x['rentArea'])[0]
            offer['price'] = x['price']
            offer['price'] = re.findall(r"\d+", x['price'])
            if offer['price'] == []:
                offer['price'] = ['цена не укзана']
            for a in offer['price']:
                offer['price'] = offer['price'][0]

            a = AddToDb()
            a.check_database(offer, 0)

    def get_offers(self):
        """Метод создает запрос на сайт."""
        get_json = self.get_json()
        entities = get_json['data']
        for item in entities:
            self.get_offer(item)


def main():
    """Распределительный модуль скрипта."""
    s = SnapParser()
    s.get_offers()


if __name__ == '__main__':
    main()
