import re
import time
from collections import Counter
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

'''Задание №2
Технологии: python, selenium, chrome
Открыть браузер Chrome через selenium. Перейти на сайт: Вы знайте цвета? (arealme.com).  с помощью робота необходимо 
нажимать на цвет, который отличается от остальных, за 60 секунд необходимо набрать наибольшее количество баллов,
 наш рекорд: 1669. Код загрузить в github. 
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


class FindColor:
    def __init__(self, silence_mode: bool):
        self.URL = "https://www.arealme.com/colors/ru/"
        self.points = 0
        self.silence_mode = silence_mode

    @measure_time
    def act(self):
        """
        Порядок действий робота
        """
        self.init_connect()
        self.start_challenge()  # клацаю кнопку старт

        while True:
            try:
                self.get_colors()  # ищу цвета
            except StaleElementReferenceException:
                time.sleep(10)  # Подсчёт баллов на странице
                if self.silence_mode is False:
                    self.driver.save_screenshot(f"task2 {self.points}.png")
                break
        self.driver.quit()
        print(f'Набрано {self.points} баллов')

    def init_connect(self):
        options = Options()
        if self.silence_mode:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        # Initialize Chrome WebDriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.URL)
        self.driver.implicitly_wait(10)  # ждать до 10 секунд
        time.sleep(2)

    def start_challenge(self):
        start_button = self.driver.find_element(By.ID, "start")
        start_button.click()

    def get_colors(self):

        parent_element = self.driver.find_element(By.CLASS_NAME, "patra-color")  # нахожу область с нужными картинками

        elements = parent_element.find_elements(By.CSS_SELECTOR, "span")  # нахожу элементы с цветами
        list_colors = []  # список цветов
        dict_colors = {}  # словарь чтобы по цвету обратиться к элементу

        for el in elements:
            ng_reflect_name = el.get_attribute("style")
            rgb_color = re.search(r'background-color: rgb\((\d+), (\d+), (\d+)\)', ng_reflect_name).group(1, 2, 3)
            rgb_string = ', '.join(rgb_color)
            list_colors.append(rgb_string)
            dict_colors[rgb_string] = el

        # из списка с цветами беру тот что один
        counts = Counter(list_colors)
        duplicate_element = min(counts, key=counts.get)

        dict_colors[duplicate_element].click()
        self.points += 1


robot = FindColor(silence_mode=False)
robot.act()
