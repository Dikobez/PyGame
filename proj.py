import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
import requests


class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Конвертер валют')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.amount_label = QLabel('Перевести:')
        layout.addWidget(self.amount_label)

        self.amount_input = QLineEdit()
        layout.addWidget(self.amount_input)

        self.from_label = QLabel('Из:')
        layout.addWidget(self.from_label)

        self.from_currency = QComboBox()
        layout.addWidget(self.from_currency)
        self.from_currency.addItems(["USD", "EUR", "GBP", "RUB", "JPY", "KZT", "UAH", "AED"])

        self.to_label = QLabel('В:')
        layout.addWidget(self.to_label)

        self.to_currency = QComboBox()
        layout.addWidget(self.to_currency)
        self.to_currency.addItems(["USD", "EUR", "GBP", "RUB", "JPY", "KZT", "UAH", "AED"])

        self.convert_button = QPushButton('Конвертировать')
        layout.addWidget(self.convert_button)
        self.convert_button.clicked.connect(self.convert)

        self.result_label = QLabel('')
        layout.addWidget(self.result_label)

    def convert(self):
        amount = float(self.amount_input.text())
        from_currency = self.from_currency.currentText()
        to_currency = self.to_currency.currentText()

        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{from_currency}')
        data = response.json()

        exchange_rate = data['rates'][to_currency]
        converted_amount = round(amount * exchange_rate, 2)

        self.result_label.setText(f'{amount} {from_currency} = {converted_amount} {to_currency}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConverterApp()
    ex.show()
    sys.exit(app.exec_())