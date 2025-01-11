import unittest
from unittest.mock import patch, MagicMock
import json
from main import CurrencyList, Decorator, JSONDecorator, CSVDecorator, show_currencies

class TestCurrencyList(unittest.TestCase):
    @patch('requests.get')
    def test_get_currencies(self, mock_get):
        # Мокаем ответ от API
        mock_response = MagicMock()
        mock_response.text = """
        <ValCurs Date="01.01.2025" name="Foreign Currency Market">
            <Valute ID="R01239">
                <NumCode>643</NumCode>
                <CharCode>RUB</CharCode>
                <Nominal>1</Nominal>
                <Name>Российский рубль</Name>
                <Value>75,1234</Value>
            </Valute>
            <Valute ID="R01235">
                <NumCode>840</NumCode>
                <CharCode>USD</CharCode>
                <Nominal>1</Nominal>
                <Name>Доллар США</Name>
                <Value>80,5678</Value>
            </Valute>
        </ValCurs>
        """
        mock_get.return_value = mock_response

        # Тестируем метод get_currencies
        cur_list = CurrencyList()
        result = cur_list.get_currencies(['R01239', 'R01235'])

        expected_result = {
            'R01239': ('75,1234', 'Российский рубль'),
            'R01235': ('80,5678', 'Доллар США')
        }

        self.assertEqual(result, expected_result)

    def test_decorator_get_currencies(self):
        # Тестируем, что декоратор просто оборачивает данные
        cur_list = CurrencyList()
        decorator = Decorator(cur_list)

        result = decorator.get_currencies(['R01239', 'R01235'])

        expected_result = {
            'R01239': ('105,0464', 'Евро'),
            'R01235': ('101,9146', 'Доллар США')
        }

        self.assertEqual(result, expected_result)

    def test_json_decorator(self):
        # Тестируем декоратор JSON
        cur_list = CurrencyList()
        json_decorator = JSONDecorator(cur_list)

        result = json_decorator.get_currencies(['R01239', 'R01235'])
        expected_result = json.dumps({
            'R01239': ('105,0464', 'Евро'),
            'R01235': ('101,9146', 'Доллар США')
        }, ensure_ascii=False, indent=4)

        # Сравнение через json.loads для игнорирования порядка ключей
        self.assertEqual(json.loads(result), json.loads(expected_result))

    def test_csv_decorator(self):
        # Тестируем декоратор CSV
        cur_list = CurrencyList()
        csv_decorator = CSVDecorator(cur_list)

        result = csv_decorator.get_currencies(['R01239', 'R01235'])

        expected_result = "ID;Rate;Name\nR01235;101,9146;Доллар США\nR01239;105,0464;Евро"
        self.assertEqual(result, expected_result)

    @patch('requests.get')
    def test_show_currencies(self, mock_get):
        # Мокаем ответ от API
        mock_response = MagicMock()
        mock_response.text = """
        <ValCurs Date="01.01.2025" name="Foreign Currency Market">
            <Valute ID="R01239">
                <NumCode>978</NumCode>
                <CharCode>EUR</CharCode>
                <Nominal>1</Nominal>
                <Name>Евро</Name>
                <Value>105,0464</Value>
            </Valute>
            <Valute ID="R01235">
                <NumCode>840</NumCode>
                <CharCode>USD</CharCode>
                <Nominal>1</Nominal>
                <Name>Доллар США</Name>
                <Value>101,9146</Value>
            </Valute>
        </ValCurs>
        """
        mock_get.return_value = mock_response

        cur_list = CurrencyList()
        wrapped_cur_list_json = JSONDecorator(cur_list)
        wrapped_cur_list_csv = CSVDecorator(cur_list)

        with patch('builtins.print') as mock_print:
            show_currencies(wrapped_cur_list_json)
            show_currencies(wrapped_cur_list_csv)

            # Получаем JSON-строку, которую вывел `print`
            printed_json = [
                call.args[0] for call in mock_print.call_args_list if "R01239" in call.args[0]
            ][0]

            # Ожидаемое значение JSON
            expected_json = json.dumps({
                "R01239": ["105,0464", "Евро"],
                "R01235": ["101,9146", "Доллар США"]
            }, ensure_ascii=False, indent=4)

            # Сравнение с использованием json.loads
            self.assertEqual(json.loads(printed_json), json.loads(expected_json))

            # Проверяем вывод CSV
            csv_result = """ID;Rate;Name
    R01235;101,9146;Доллар США
    R01239;105,0464;Евро"""

            printed_csv = [
                call.args[0].strip() for call in mock_print.call_args_list if "ID;Rate;Name" in call.args[0]
            ][0]

            # Приводим обе строки к списку строк без лишних пробелов
            result_lines = [line.strip() for line in printed_csv.split('\n')]
            expected_lines = [line.strip() for line in csv_result.split('\n')]

            self.assertCountEqual(result_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()
