import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import urllib.request

"""
Открыть браузер Chrome через selenium. Перейти на сайт: https://www.rpachallenge.com/. Считать файл «challenge.xlsx»
с помощью pandas или другого аналога. Полученные данные внести во все формы на сайте https://www.rpachallenge.com/
(их 10 вариантов, появляются после нажатия кнопки «SUBMIT») предварительно нажав кнопку «Start». После выполнения
необходимо сделать скриншот результата. Код загрузить в github.
"""


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"На функцию {func.__name__} затрачено {execution_time} секунд")
        return result

    return wrapper


class Pareser:
    def __init__(self):
        self.URL = "https://www.rpachallenge.com"
        self.url_xlsx = "https://www.rpachallenge.com/assets/downloadFiles/challenge.xlsx"

    @measure_time
    def act(self):
        """
        Порядок действий робота
        """
        self.get_xls()  # сохраняю файл с заданиями

        self.xlsx_to_df()  # файл в дф
        self.init_connect()
        self.start_challenge()  # клацаю кнопку старт
        self.filling_fields()  # заполняю поля
        time.sleep(1)  # наслаждаюсь вкусом победы
        self.driver.save_screenshot("task1.png")
        time.sleep(10)  # наслаждаюсь вкусом победы
        self.driver.quit()

    def start_challenge(self):
        start_button = self.driver.find_element(By.CSS_SELECTOR, "button")
        start_button.click()

    def filling_fields(self):

        for index, row in self.df.iterrows():
            elements = self.driver.find_elements(By.CSS_SELECTOR, "input")
            submit_button = None
            for el in elements:
                ng_reflect_name = el.get_attribute("ng-reflect-name")

                if ng_reflect_name is not None:  # кнопка Submit почему-то тоже считается input
                    el.send_keys(row[ng_reflect_name])

                if ng_reflect_name is None:
                    submit_button = el  # если нашлась кнопка с None - она является Submit, сохраняем, чтоб после кликнуть

            submit_button.click()

    def init_connect(self):
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')

        # Initialize Chrome WebDriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.URL)



    def get_xls(self):
        response = requests.get(self.url_xlsx)
        try:
            with open("challenge.xlsx", "wb") as file:
                file.write(response.content)
        except PermissionError as err:
            print('Ошибка: ', err.args[1])

    def xlsx_to_df(self):
        try:
            self.df = pd.read_excel('challenge.xlsx', header=0, index_col=None)
            self.df.columns = self.df.columns.str.strip()  # в экселевском документе в названия колонок лишние пробелы
            self.df.rename(columns={'First Name': 'labelFirstName',
                                    'Last Name': 'labelLastName',
                                    'Company Name': 'labelCompanyName',
                                    'Role in Company': 'labelRole',
                                    'Address': 'labelAddress',
                                    'Email': 'labelEmail',
                                    'Phone Number': 'labelPhone',
                                    }, inplace=True)
            print(self.df.to_string())
        except PermissionError as err:
            print('Ошибка: ', err.args[1])



robot = Pareser()
robot.act()
