from robocorp.tasks import task
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import date
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from RPA.Robocorp.WorkItems import WorkItems
from utils import support
from RPA.Browser.Selenium import Selenium


# class NewsScraper:
#     def __init__(self, query, time_frame=1):
#         if time_frame == 0:
#             time_frame = 1
#         # options = Options()
#         # options.add_argument('--headless')
#         # options.add_argument('--no-sandbox')
#         # options.add_argument('--disable-dev-shm-usage')
#         # driver = webdriver.Chrome(options=options)
#         driver = webdriver.Chrome()
#         driver.get('http://google.com/')
#         driver.get("https://www.latimes.com")
#         assert "Times" in driver.title
#         elem = driver.find_element(By.XPATH, '/html/body/ps-header/header/div[2]/button')
#         elem.click()
#         search_bar = driver.find_element(By.XPATH, '/html/body/ps-header/header/div[2]/div[2]/form/label/input')
#         search_bar.send_keys(query)
#         search_bar.send_keys(Keys.RETURN)
#         assert "Times" in driver.title
#         select = Select(driver.find_element(By.CLASS_NAME, 'select-input'))
#         select.select_by_visible_text('Newest')
#         driver.refresh()
#         assert "Times" in driver.title
#         news = driver.find_elements(By.CLASS_NAME, 'promo-wrapper')
#         last_date = support.date_parser(news[-1].text.split('\n')[-1])
#         page = 1
#         current_url = driver.current_url
#         self.data = []
#         while support.months_to(date.today(), last_date) <= time_frame:
#             for new in news:
#                 title_description = new.text.split('\n')[0] + ' ' + new.text.split('\n')[1]
#                 line = []
#                 for item in new.text.split('\n')[1:]:
#                     if item != 'FOR SUBSCRIBERS':
#                         line.append(item)
#                 try:
#                     line.append(new.find_element(By.CLASS_NAME, 'image').get_attribute('src'))
#                 except Exception:
#                     line.append('No Image')
#                 line.append(support.contains_money(title_description))
#                 line.append(title_description.count(query))
#                 self.data.append(line)
#             page += 1
#             driver.get(current_url + f'&p={page}')
#             driver.refresh()
#             assert "Times" in driver.title
#             news = driver.find_elements(By.CLASS_NAME, 'promo-wrapper')
#             last_date = support.date_parser(news[-1].text.split('\n')[-1])
#         driver.close()
class NewsScraper:
    def __init__(self, query, time_frame=1):
        if time_frame == 0:
            time_frame = 1
        options = [
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
        self.browser = Selenium()
        self.browser.open_available_browser('https://www.latimes.com',options=options,headless=True)
        assert "Times" in self.browser.get_title()
        # Search for the query
        self.browser.click_button('//html/body/ps-header/header/div[2]/button')
        self.browser.input_text('name:q',query)
        self.browser.press_keys('name:q', 'ENTER')
        assert "Times" in self.browser.get_title()

        # Select 'Newest' articles
        self.browser.select_from_list_by_label('name:s','Newest')
        self.browser.reload_page()
        assert "Times" in self.browser.get_title()

        # Extracting news articles
        self.data = []
        news = self.browser.find_elements('class:promo-wrapper')
        last_date = support.date_parser(news[-1].text.split('\n')[-1])
        page = 1
        current_url = self.browser.get_location()

        while support.months_to(date.today(), last_date) <= time_frame:
            for new in news:
                title_description = new.text.split('\n')[0] + ' ' + new.text.split('\n')[1]
                line = []
                for item in new.text.split('\n')[1:]:
                    if item != 'FOR SUBSCRIBERS':
                        line.append(item)
                try:
                    line.append(self.browser.find_element('class:image',new).get_attribute('src'))
                except Exception:
                    line.append('No Image')
                line.append(support.contains_money(title_description))
                line.append(title_description.count(query))
                self.data.append(line)

            page += 1
            self.browser.go_to(f'{current_url}&p={page}')
            self.browser.reload_page()
            assert "Times" in self.browser.get_title()
            news = self.browser.find_elements('class:promo-wrapper')
            last_date = support.date_parser(news[-1].text.split('\n')[-1])

        self.browser.close_all_browsers()

    def save(self):
        result = pd.DataFrame(
            self.data,
            columns=['Title', 'Description', 'Date', 'Image', 'Contains money', 'Query matches']
        )
        result['Date'] = result['Date'].apply(support.date_parser)
        result['Image File'] = result['Title'].apply(lambda x: '_'.join(x.split(' ')[0:4]) + '.jpg')
        result.set_index('Title').to_excel('output/Results.xlsx')
        for image, file in zip(result['Image'], result['Image File']):
            support.baixar_imagem(image, file)
            
@task
def main():
    # work_items = WorkItems()
    # work_items.get_input_work_item()
    # query = work_items.get_work_item_variable("query")
    # time_frame = work_items.get_work_item_variable("time_frame")
    query='Vatican'
    time_frame=2
    bot = NewsScraper(query,time_frame)
    bot.save()

if __name__ == '__main__':
    main()