import time
import json
import requests
from datetime import datetime
from xml.etree import ElementTree as ET


class BaseCurrencyList:
    def get_currencies(self, currency_ids_lst: list = None) -> dict:
        pass


class CurrencyList(BaseCurrencyList):
    def __init__(self):
        self.rates_available = False
        self.timestamp = time.time()
        self.current_day = datetime.now().day
        self.rates = None

    def get_currencies(self, currency_ids_lst: list = None) -> dict:
        t = time.time()
        dt = datetime.today().day

        result = {}

        if self.rates_available:
            return self.rates

        if not self.rates_available or (t - self.timestamp > 3600 or dt != self.current_day):
            if currency_ids_lst is None:
                currency_ids_lst = ['R01239', 'R01235']  # использовано RUB и USD
            res = requests.get("http://www.cbr.ru/scripts/XML_daily.asp")
            cur_res_str = res.text

            root = ET.fromstring(cur_res_str)

            valutes = root.findall("Valute")

            for _v in valutes:
                valute_id = _v.get('ID')

                if str(valute_id) in currency_ids_lst:
                    valute_cur_val = _v.find('Value').text
                    valute_cur_name = _v.find('Name').text

                    result[valute_id] = (valute_cur_val, valute_cur_name)

            self.rates = result
            self.rates_available = True

        return result


class Decorator(BaseCurrencyList):
    """
    aka Decorator из примера паттерна
    """

    __wrapped_object: BaseCurrencyList = None

    def __init__(self, currency_lst: BaseCurrencyList):
        self.__wrapped_object = currency_lst

    @property
    def wrapped_object(self) -> BaseCurrencyList:
        return self.__wrapped_object

    def get_currencies(self, currency_ids_lst: list = None) -> dict:
        return self.__wrapped_object.get_currencies(currency_ids_lst)


class JSONDecorator(Decorator):
    def get_currencies(self, currency_ids_lst: list = None) -> str:
        return json.dumps(self.wrapped_object.get_currencies(currency_ids_lst), ensure_ascii=False, indent=4)


class CSVDecorator(Decorator):
    def get_currencies(self, currency_ids_lst: list = None) -> str:
        currency_data = self.wrapped_object.get_currencies(currency_ids_lst)

        if isinstance(currency_data, str):
            currency_data = json.loads(currency_data)

        csv_data = "ID;Rate;Name\n"
        for currency, val in currency_data.items():
            csv_data += f'{currency};{val[0]};{val[1]}\n'
        csv_data = csv_data.rstrip()
        return csv_data


def show_currencies(currencies: BaseCurrencyList):
    """
       aka client_code()
    """

    print(currencies.get_currencies())


if __name__ == "__main__":
    cur_list = CurrencyList()
    wrapped_cur_list = Decorator(cur_list)
    wrapped_cur_list_json = JSONDecorator(cur_list)
    wrapped_cur_list_csv = CSVDecorator(cur_list)

    show_currencies(wrapped_cur_list_json)
    show_currencies(wrapped_cur_list_csv)
    show_currencies(wrapped_cur_list)
