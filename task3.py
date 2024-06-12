import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


'''Задание №3
Технологии: python, selenium, excel, chrome, pandas или аналог
Открыть браузер Chrome через selenium. Перейти на сайт:
https://www.domkor-dom.com/prodazha-kvartir-Novostroiki/kvartira-Naberezhnye-Chelny/. 
С помощью робота необходимо получить данные из «шахматки» каждого ЖК, для каждого ЖК сформировать Excel. 
Код загрузить в github. 
№ Подъезда 	Этаж	№ Кв.	Общая площадь	    Цена
1	        1	        2	42,50 кв.м	    4 568 750,00

'''


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"На функцию {func.__name__} затрачено {execution_time} секунд")
        return result

    return wrapper


class Apartments:
    def __init__(self, silence_mode: bool):

        self.URL = "https://www.domkor-dom.com/prodazha-kvartir-Novostroiki/kvartira-Naberezhnye-Chelny"
        self.URL_start = "https://www.domkor-dom.com"
        self.silence_mode = silence_mode

        self.JK_urls = []


    @measure_time
    def act(self):
        """
        Порядок действий робота
        """
        os.makedirs('task3_results', exist_ok=True) # создаю папку с результатами
        self.init_connect()  # коннект к сайту
        self.get_url_JK()  # собираю url всех ЖК где есть шахматки
        for urls in self.JK_urls:  # для каждого жк...
            self.pars_values(self.URL_start + urls)  # ищу со странички информацию и заполняю в ДФ, сохраняю xlsx
        self.driver.quit()  # закрыть браузер

    def init_connect(self):
        options = Options()
        if self.silence_mode:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        # Initialize Chrome WebDriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.URL)
        # self.driver.implicitly_wait(10)  # ждать до 10 секунд

    def get_url_JK(self):
        main_page = self.driver.page_source
        parsed_html = BeautifulSoup(main_page, 'lxml')

        parsed_table = parsed_html.body.find('div', attrs={'class': 'wrap1050'})

        parsed_goods = parsed_table.find_all('a')
        for i in parsed_goods:
            if "https:" not in i['href']:
                self.JK_urls.append(i['href'])

    @staticmethod
    def _search_value(text):
        pattern = r'Квартира №(\d+)\s\((\d+)стр.\)Количество комнат: (\d+)Общая площадь:(\d+,\d+)кв.м.Площадь квартиры:(.+)'
        matches = re.findall(pattern, text)[0]
        return matches

    @staticmethod
    def _name_jk(url):
        if url.endswith('/'):
            url = url[:-1]
        name = url.split('/')[-1]
        return name

    def pars_values(self, url):
        # self.driver.get( 'https://www.domkor-dom.com/prodazha-kvartir-Novostroiki/kvartira-Naberezhnye-Chelny/prodazha-kvartir-v-sidorovke-zhk-vysota-45')

        df = pd.DataFrame(
            columns=['№ Подъезда', 'Этаж', "№ Кв.", "Общая площадь", "Цена"])

        self.driver.get(url)
        main_page = self.driver.page_source
        parsed_html = BeautifulSoup(main_page, 'lxml')
        # name_jk = parsed_html.body.find('li', attrs={'style': 'list-style-type: none; display: inline;'})

        parsed_table = parsed_html.body.find('table', attrs={'class': 'apartments collapsed'})
        entrances = parsed_table.find_all('div', attrs={'class': 'entrance'})
        for entrance in entrances:
            entrance_num = entrance.find('div', attrs={'class': 'nkv'})
            price = entrance.find('font', attrs={'style': 'color:#191919;'})
            appartoments = entrance.find_all('div', attrs={'class': 'lmainText'})

            for el in appartoments:
                vals = self._search_value(el.text)
                df.loc[len(df.index)] = [entrance_num.text, vals[1], vals[2], vals[3], price.text]

        df.to_excel(fr'task3_results\{self._name_jk(url)}.xlsx')


robot = Apartments(silence_mode=True)
robot.act()
