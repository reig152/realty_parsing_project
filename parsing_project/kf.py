import requests
import re
from add_to_db import AddToDb


class KnightParser:
    """Get offers from KnightFrank."""
    def get_json(self, page):
        """Метод для получения json словаря."""
        cookies = {
            'vs_uuid': 'e9ecc9b4091f409d8dafa571da29c43c',
            'header_city': 'msk',
            '_ym_uid': '1663145728383366419',
            '_ym_d': '1663145728',
            '_ga': 'GA1.2.871988550.1663145729',
            'tmr_lvid': '39aedf24b93fa55bd512790f2f1fab17',
            'tmr_lvidTS': '1663145728589',
            'WidgetChat_shownOn': 'on_inv',
            '_gid': 'GA1.2.1041715902.1678694964',
            '_gat_UA-82374931-1': '1',
            '_ym_isad': '2',
            'WhiteCallback_visitorId': '12202962160',
            'WhiteCallback_visit': '20606981749',
            'WhiteSaas_uniqueLead': 'no',
            '_ym_visorc': 'w',
            '_cmg_csstqw9ol': '1678694964',
            '_comagic_idqw9ol': '5655704508.9332102523.1678694964',
            'WhiteCallback_openedPages': 'dwPwe',
            'WhiteCallback_mainPage': 'dwPwe',
            'tmr_detect': '0%7C1678694981952',
            'WidgetChat_invitation_2807478': 'true',
            'WhiteCallback_timeAll': '41',
            'WhiteCallback_timePage': '41',
            '_gr_session': '%7B%22s_id%22%3A%22499f4dbd-68c1-4ae7-b622-38f93fbc3c81%22%2C%22s_time%22%3A1678695020715%7D',
        }

        headers = {
            'authority': 'kf.expert',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en;q=0.9',
            # 'cookie': 'vs_uuid=e9ecc9b4091f409d8dafa571da29c43c; header_city=msk; _ym_uid=1663145728383366419; _ym_d=1663145728; _ga=GA1.2.871988550.1663145729; tmr_lvid=39aedf24b93fa55bd512790f2f1fab17; tmr_lvidTS=1663145728589; WidgetChat_shownOn=on_inv; _gid=GA1.2.1041715902.1678694964; _gat_UA-82374931-1=1; _ym_isad=2; WhiteCallback_visitorId=12202962160; WhiteCallback_visit=20606981749; WhiteSaas_uniqueLead=no; _ym_visorc=w; _cmg_csstqw9ol=1678694964; _comagic_idqw9ol=5655704508.9332102523.1678694964; WhiteCallback_openedPages=dwPwe; WhiteCallback_mainPage=dwPwe; tmr_detect=0%7C1678694981952; WidgetChat_invitation_2807478=true; WhiteCallback_timeAll=41; WhiteCallback_timePage=41; _gr_session=%7B%22s_id%22%3A%22499f4dbd-68c1-4ae7-b622-38f93fbc3c81%22%2C%22s_time%22%3A1678695020715%7D',
            'referer': 'https://kf.expert/office/prodazha?page=1&pay_type_ids=1&separ_group_id=r_office&currency_alias=rur&prices_key_prefix=sale_from_all&sessionId=123456&order_field=order_effective_position',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.777 Yowser/2.5 Safari/537.36',
        }

        params = {
            'page': page,
            'pay_type_ids': '1',
            'separ_group_id': 'r_office',
            'currency_alias': 'rur',
            'prices_key_prefix': 'sale_from_all',
            'sessionId': '123456',
            'order_field': 'order_effective_position',
        }

        response = requests.get('https://kf.expert/vapi/listing_more_cards',
                                params=params,
                                cookies=cookies,
                                headers=headers)

        return response.json()

    def get_pagen(self):
        """Метод высчитывает количество страниц."""
        # найдем количество страниц с первой страницы
        response = self.get_json(1)
        pagen = response['cards'][-2]['pagination']['pages'][-1]['value']

        return pagen

    def get_offer(self):
        """Метод собирает информацию o6 объявлениях."""
        pagen = self.get_pagen()
        for page in range(1, pagen+1):
            cards = self.get_json(page)['cards']

            # отсекаем лишнее из ответа
            for x in cards:
                if 'address' in x:
                    address = x['address'][-1]['text']
                    offer_id = x['display_id']
                    # проверка на количество объектов в блоке
                    if 'offers' in x:
                        for i in x['offers']:
                            pre_price = i['price']['text'].replace(' ', '')
                            price = re.findall(r"\d+", pre_price)
                            if price == []:
                                price = 0
                            else:
                                price = price[0]
                            square = i['bedrooms']['text']
                            square = square.replace('м²', '').strip()
                            pre_url = i['bedrooms']['url']
                            url = 'https://kf.expert/' + pre_url
                            characteristics = x['characteristics']
                            object_class = characteristics[-1]['text']
                            self.add_to_db(address, price,
                                        square, url, object_class, offer_id)
                    else:
                        pre_price = x['price']['begin']
                        pre_price = pre_price.replace(' ', '')
                        price = re.findall(r"\d+", pre_price)
                        if price == []:
                            price = 0
                        else:
                            price = price[0]
                        square = x['characteristics'][0]['text']
                        square = square.replace('м²', '').strip()
                        url = 'https://kf.expert/' + x['title']['url']
                        object_class = x['characteristics'][-2]['text']
                        self.add_to_db(address, price,
                                       square, url, object_class, offer_id)

    def add_to_db(self, address,
                  price, square,
                  url, object_class, offer_id):
        """Метод подготавливает данные к добавлению в БД."""
        offers = {}

        offers['offer_id'] = offer_id
        offers['address'] = address
        offers['object_class'] = object_class
        offers['price'] = price
        offers['square'] = square
        offers['link'] = url

        # добавим в БД
        a = AddToDb()
        a.check_database(offers, 0)


def main():
    k = KnightParser()
    k.get_offer()


if __name__ == '__main__':
    main()
