import requests
import re
from bs4 import BeautifulSoup
from add_to_db import AddToDb


class Order:
    """Базовый класс с запросом на рентавик."""
    def order(self, pagen):
        """Непосредственно запрос."""
        cookies = {
            '_ym_d': '1663235582',
            '_ym_uid': '1663235582490529038',
            'BX_USER_ID': 'daf395c88b0834a6f2df69fdb5bd99fa',
            'PHPSESSID': 'p1u4sf89nc4huf4badidjl28br',
            '_gid': 'GA1.2.809472181.1676877207',
            '_gat': '1',
            '_ga_93G568L6H3': 'GS1.1.1676877206.39.0.1676877206.0.0.0',
            '_ga': 'GA1.1.1608806329.1663235582',
            '_ym_visorc': 'w',
            '_ym_isad': '2',
        }

        headers = {
            'authority': 'rentavik.ru',
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'cookie': '_ym_d=1663235582; _ym_uid=1663235582490529038; BX_USER_ID=daf395c88b0834a6f2df69fdb5bd99fa; PHPSESSID=p1u4sf89nc4huf4badidjl28br; _gid=GA1.2.809472181.1676877207; _gat=1; _ga_93G568L6H3=GS1.1.1676877206.39.0.1676877206.0.0.0; _ga=GA1.1.1608806329.1663235582; _ym_visorc=w; _ym_isad=2',
            'origin': 'https://rentavik.ru',
            'referer': 'https://rentavik.ru/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.2.987 Yowser/2.5 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        params = {
            'isAjax': 'true',
            'globalFilter': 'true',
            'PAGEN_1': pagen,
        }

        data = {
            'office[TYPE_OFFICE]': '2',
            '': '',
            'office[AREA][from]': '',
            'office[AREA][to]': '',
            'office[REAL_PRICE][from]': '',
            'office[REAL_PRICE][to]': '',
            'building[nearType]': '1',
            'office[FLOOR][from]': '',
            'office[FLOOR][to]': '',
            'building[query]': '',
            'office[ID]': '',
            'building[buildClass][0]': '',
            'building[buildClass][1]': '',
            'building[buildClass][2]': '',
            'building[buildClass][3]': '',
            'only_actual': '',
            'office[bank_VALUE]': '',
            'office[medCentr_VALUE]': '',
            'office[hostel_VALUE]': '',
            'office[vipOffice_VALUE]': '',
            'office[redevelopment_VALUE]': '',
            'office[fromStreet_VALUE]': '',
            'office[FURNITURE_VALUE]': '',
            'office[loft_VALUE]': '',
            'office[highHeader_VALUE]': '',
            'office[balkon_VALUE]': '',
            'building[border]': '',
            'office[arenda_biz]': '',
            'office[type][]': '',
            'office[price-type]': '1',
            'building[metro][]': '',
            'building[ao][]': '',
            'building[region][]': '',
            'office[layout][]': '',
            'office[nds]': 'false',
            'building[tax][]': '',
            'office[stateRoom][]': '',
            'office[arenda_okupaemost]': '0',
        }

        response = requests.post(
            'https://rentavik.ru/',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data
        )
        return response.text


class BaseParsingResult:
    """Базовый класс-обработчик результатов."""
    def results(self):
        """Базовый метод обработки результатов:
           цена, площадь, адрес."""
        pagen = self.get_pagen()
        o = Order()
        for page in range(1, int(pagen)+1):
            response = o.order(page)
            soup = BeautifulSoup(response, 'lxml')

            offer_ids = [
                re.findall(
                 r'(?:Аренда|Продажа)№(\d+)',
                 x.text.replace('\n', '').replace(' ', '')
                ) for x in soup.find_all(
                 'div', class_='filterresults-item-body-block')
            ]

            addresses = [x.text.strip() for x in soup.find_all(
                'div',
                class_='filterresults-header__value')]

            squares = [re.findall(
                r'\d+м2', x.text.replace('\n', '').replace(' ', '')
            ) for x in soup.find_all(
                'div',
                'filterresults-item-body-block')]

            prices = [re.findall(
                r'./м\d+руб.', x.text.replace('\n', '').replace(' ', '')
            ) for x in soup.find_all(
                'div',
                'filterresults-item-body-block')]

            links = ["https://rentavik.ru" + x.find('a')['href'] for x in soup.find_all(
                'div',
                class_='filterresults-item__title'
            ) if x.find('a')]

            for x in range(len(addresses)):
                address = addresses[x]
                offer_id = offer_ids[x]
                price = prices[x]
                square = squares[x]
                link = links[x]
                for b in range(len(price)):
                    keys = [
                        'address',
                        'offer_id',
                        'price',
                        'square',
                        'link'
                    ]
                    values = [
                        address,
                        offer_id[b],
                        price[b].split('./м2')[-1].split('руб.')[0],
                        square[b].split('м2')[0],
                        link
                    ]
                    dictionary = dict(zip(keys, values))

                    a = AddToDb()
                    a.check_database(dictionary, 0)

    def get_pagen(self):
        """Находит количество страниц по указанному запросу"""
        page = 1
        o = Order()
        response = o.order(page)
        soup = BeautifulSoup(response, 'lxml')
        pagen = [x.text for x in soup.find_all('a', 'pagging-list__item')]
        return pagen[-1]


def main():
    p = BaseParsingResult()
    p.results()


if __name__ == '__main__':
    main()
