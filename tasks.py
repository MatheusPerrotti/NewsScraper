from robocorp.tasks import task
from datetime import date
import pandas as pd
from RPA.Robocorp.WorkItems import WorkItems
from utils import support
from RPA.Browser.Selenium import Selenium


class NewsScraper:
    def __init__(self, query, time_frame=1):
        if time_frame == 0:
            self.time_frame = 1
        else:
            self.time_frame = time_frame
        self.query = query

    
    def extract(self):
        options = [
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
        self.browser = Selenium()
        self.browser.open_available_browser('https://www.latimes.com',options=options,headless=True)
        assert "Times" in self.browser.get_title()
        self.browser.click_button('//html/body/ps-header/header/div[2]/button')
        self.browser.input_text('name:q', self.query)
        self.browser.press_keys('name:q', 'ENTER')
        assert "Times" in self.browser.get_title()

        self.browser.select_from_list_by_label('name:s','Newest')
        self.browser.reload_page()
        assert "Times" in self.browser.get_title()

        self.data = []
        news = self.browser.find_elements('class:promo-wrapper')
        last_date = support.date_parser(news[-1].text.split('\n')[-1])
        page = 1
        current_url = self.browser.get_location()

        while support.months_to(date.today(), last_date) <= self.time_frame:
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
                line.append(title_description.count(self.query))
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
    work_items = WorkItems()
    work_items.get_input_work_item()
    query = work_items.get_work_item_variable("query")
    time_frame = work_items.get_work_item_variable("time_frame")
    bot = NewsScraper(query,time_frame)
    bot.extract()
    bot.save()

if __name__ == '__main__':
    main()