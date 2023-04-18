import sqlite3
import requests
from config import token, chat_id


class AddToDb:
    """
    Модуль добавления информации в БД
    с отправкой сообщения в ТГ.
    """
    def check_database(self, offer, extra: int):
        """Метод добавляет только новые объявления."""
        offer_id = offer['offer_id']
        address = offer['address']
        with sqlite3.connect(
            'offers.db'
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT offer_id FROM offers WHERE offer_id = (?)
            """, (offer_id, ))
            if extra == 1:
                cursor.execute("""
                    SELECT address FROM offers WHERE address = (?)
                """, (address, ))
            result = cursor.fetchone()
            if result is None:
                # self.send_telegram(offer)
                cursor.execute("""
                    INSERT INTO offers
                    VALUES (
                        :offer_id,
                        :address,
                        :price,
                        :square,
                        :link
                    )
                """, offer)
                connection.commit()
                print(f'Объявление {offer_id} добавлено в базу данных')

                # TODO send_telegram(offer)

    def format_text(self, offer):
        """Метод форматирует сообщение для отправки в ТГ."""
        text = (f"NEW!id: {offer['offer_id']}\n{offer['address']}\n"
                f"Площадь: {offer['square']}м2; "
                f"Стоимость: {offer['price']}руб\n"
                f"Ссылка на объявление: {offer['link']}")

        return text

    def send_telegram(self, offer):
        """Метод отправляет сообщение в ТГ."""
        text = self.format_text(offer)
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        for i in range(len(chat_id)):
            data = {'chat_id': chat_id[i],
                    'text': text
                    }
            response = requests.post(url=url, data=data)
            print(response)


def main():
    """Распределительный модуль скрипта."""
    pass


if __name__ == '__main__':
    main()
