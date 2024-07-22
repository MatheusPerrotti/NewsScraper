from robocorp.tasks import task
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import date
import re
import pandas as pd
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from RPA.Robocorp.WorkItems import WorkItems


def date_parser(item):
    if '.' in item:
        text = item.replace(',', '.').split('.')
    else:
        text = item.replace(' ', '.', 1).replace(',', '.').split('.')
    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    return date(int(text[2].replace(' ', '')), months[text[0][0:3]], int(text[1].replace(' ', '')))


def months_to(end, start):
    timedelta = end - start
    return int(timedelta.days / 30)


def contains_money(text):
    money_patterns = [
        r'\$\d+(?:\.\d+)?',
        r'\d+(?:,\d+)*(?:\.\d+)?\s*dollars',
        r'\d+(?:,\d+)*(?:\.\d+)?\s*USD'
    ]
    for pattern in money_patterns:
        if re.search(pattern, text):
            return True
    return False


def baixar_imagem(url, nome_arquivo):
    urllib.request.urlretrieve(url, f'output/{nome_arquivo}')


class NewsScraper:
    def __init__(self, query, time_frame=1):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.get('http://google.com/')
        driver.get("https://www.latimes.com")
        assert "Times" in driver.title
        elem = driver.find_element(By.XPATH, '/html/body/ps-header/header/div[2]/button')
        elem.click()
        search_bar = driver.find_element(By.XPATH, '/html/body/ps-header/header/div[2]/div[2]/form/label/input')
        search_bar.send_keys(query)
        search_bar.send_keys(Keys.RETURN)
        assert "Times" in driver.title
        select = Select(driver.find_element(By.CLASS_NAME, 'select-input'))
        select.select_by_visible_text('Newest')
        driver.refresh()
        assert "Times" in driver.title
        news = driver.find_elements(By.CLASS_NAME, 'promo-wrapper')
        last_date = date_parser(news[-1].text.split('\n')[-1])
        page = 1
        current_url = driver.current_url
        self.data = []
        while months_to(date.today(), last_date) < time_frame:
            for new in news:
                title_description = new.text.split('\n')[0] + ' ' + new.text.split('\n')[1]
                line = []
                for item in new.text.split('\n')[1:]:
                    if item != 'FOR SUBSCRIBERS':
                        line.append(item)
                try:
                    line.append(new.find_element(By.CLASS_NAME, 'image').get_attribute('src'))
                except Exception:
                    line.append('No Image')
                line.append(contains_money(title_description))
                line.append(title_description.count(query))
                self.data.append(line)
            page += 1
            driver.get(current_url + f'&p={page}')
            driver.refresh()
            assert "Times" in driver.title
            news = driver.find_elements(By.CLASS_NAME, 'promo-wrapper')
            last_date = date_parser(news[-1].text.split('\n')[-1])
        driver.close()

    def save(self):
        result = pd.DataFrame(
            self.data,
            columns=['Title', 'Description', 'Date', 'Image', 'Contains money', 'Query matches']
        )
        result['Date'] = result['Date'].apply(date_parser)
        result['Image File'] = result['Title'].apply(lambda x: '_'.join(x.split(' ')[0:4]) + '.jpg')
        result.set_index('Title').to_excel('output/Results.xlsx')
        for image, file in zip(result['Image'], result['Image File']):
            baixar_imagem(image, file)
            
@task
def main():
    work_items = WorkItems()
    work_items.get_input_work_item()
    query = work_items.get_work_item_variable("query")
    time_frame = work_items.get_work_item_variable("time_frame")
    bot = NewsScraper(query,time_frame)
    bot.save()

if __name__ == '__main__':
    main()