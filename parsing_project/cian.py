import logging
import re
import time

from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

from add_to_db import AddToDb


# Здесь задана глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

# А тут установлены настройки логгера для текущего файла - example_for_log.py
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.INFO)
# Указываем обработчик логов
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

# Указываем обработчик логов для файла program.log
handler2 = RotatingFileHandler(
    'program.log',
    maxBytes=50000000,
    backupCount=5
)
logging.getLogger().addHandler(handler2)


class CianParser:
    """Собирает новые объявления циан"""

    # настройки для селениум

    chrome_options = webdriver.FirefoxOptions()
    chrome_options.set_capability("browserVersion", "109.0")
    chrome_options.set_capability("selenoid:options", {
            "enableVNC": True,
            "enableVideo": False})

    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.74 Safari/537.36')

    def get_cian_offer_latest(self):
        """Собирает последние объявления из циан."""
        cian_prox = Proxy()
        cian_prox.proxy_type = ProxyType.MANUAL
        # укажите прокси
        cian_prox.http_proxy = "your_proxy"
        cian_prox.ssl_proxy = "your_proxy"

        cian_capabilities = webdriver.DesiredCapabilities.FIREFOX
        cian_prox.add_to_capabilities(cian_capabilities)

        links_with_types = {
            'Офис': 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&minarea=50&minprice=25000000&offer_type=offices&office_type%5B0%5D=1&region=1&sort=creation_date_desc',
            'Здание': 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&minarea=50&minprice=25000000&offer_type=offices&office_type%5B0%5D=11&region=1&sort=creation_date_desc',
            'ГАБ': 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&minprice=25000000&offer_type=offices&office_type%5B0%5D=10&ready_business_types%5B0%5D=1&region=1&sort=creation_date_desc',
            'Торговая площадь': 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&minarea=50&minprice=25000000&offer_type=offices&office_type%5B0%5D=2&region=1&sort=creation_date_desc',
            }
        for types, data in links_with_types.items():
            try:
                with webdriver.Remote(
                        # укажите ip VPS, на котором установлен selenoid
                        command_executor="http://{ip}/wd/hub",
                        options=self.chrome_options,
                        desired_capabilities=cian_capabilities) as browser:

                    browser.get(f'{data}')

                    title = [
                        x.text.replace(
                            ' ', ''
                        ) for x in browser.find_elements(
                            By.CSS_SELECTOR, '[data-name="CommercialTitle"]'
                        )
                    ]

                    # достаем ссылку
                    link = [
                        x.get_attribute(
                            'href'
                        ) for x in browser.find_elements(
                            By.CSS_SELECTOR, '[data-name="CommercialTitle"]'
                        )
                    ]

                    # id объявления
                    offer_id = [x.split('/')[-2] for x in link]

                    # достаем адрес
                    addr = [x.text.split(
                        ','
                    )[-2:] for x in browser.find_elements(
                        By.CSS_SELECTOR, '[data-name="Address"]'
                    )]
                    address = [",".join(x) for x in addr]

                    # делаем проверку на нашу компанию
                    comp = [x.text for x in browser.find_elements(
                        By.CSS_SELECTOR, '[data-name="HorizontalCard"]'
                    )]
                    company = []
                    for x in comp:
                        a = re.findall(r"OF RU - коммерческая недвижимость", x)
                        if a == ['OF RU - коммерческая недвижимость']:
                            b = 'Не принимать в БД'
                            company.append(b)
                        else:
                            b = 'Принимать в БД'
                            company.append(b)

                    # достаем площадь из тайтла
                    square = []
                    for x in title:
                        a = x.split('м')[0]
                        ploshad = re.findall(r"\d+", a)
                        if ploshad == []:
                            ploshad = 0
                            square.append(ploshad)
                        else:
                            square.append(int(ploshad[0]))

                    # достаем цену из тайтла
                    price = []
                    for x in title:
                        a = x.split('м²')[-1]
                        b = re.findall(r"\d+", a)
                        if len(b) > 1:
                            rub = f'{b[0]}.{b[-1]}'
                            if float(rub) < 25:
                                kes = float(rub) * 1000000000
                                price.append(int(kes))
                            else:
                                kes = float(rub) * 1000000
                                price.append(int(kes))
                        elif len(b) == 1:
                            rub = b[0]
                            if float(rub) < 25:
                                kes = float(rub) * 1000000000
                                price.append(int(kes))
                            elif 25 < float(rub) < 1000:
                                kes = float(rub) * 1000000
                                price.append(int(kes))
                            else:
                                price.append(int(rub))
                        else:
                            rub = 0
                            price.append(rub)

                    # класс объекта
                    obj_class = []
                    for x in comp:
                        a = re.findall(r"Класс \D|КЛАСС \D", x)
                        if a == []:
                            b = '-'
                            obj_class.append(b)
                        elif a == ['Класс "']:
                            b = '-'
                            obj_class.append(b)
                        elif a[0].split(' ')[-1] == '"':
                            b = '-'
                            obj_class.append(b)
                        else:
                            obj_class.append(a[0].split(' ')[-1])

                    # все вместе
                    offer = {}
                    for i in range(len(title)):
                        if company[i] == 'Принимать в БД':
                            offer['company'] = 'Циан'
                            offer['offer_id'] = offer_id[i]
                            offer['object_type'] = types
                            offer['object_class'] = str(obj_class[i]).upper()
                            offer['square'] = square[i]
                            offer['price'] = price[i]
                            offer['address'] = address[i]
                            offer['link'] = link[i]

                            a = AddToDb()
                            a.check_database(offer, 1)

                # делаем паузы между сессиями
                time.sleep(10)

            except Exception as ex:
                logger.error(f'Что-то пошло не так {ex}')
                continue


def main():
    """Распределительный модуль скрипта."""
    c = CianParser()
    c.get_cian_offer_latest()


if __name__ == '__main__':
    main()
