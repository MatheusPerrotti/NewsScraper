from datetime import date
import re
import urllib

class support:
    def date_parser(item):
        if 'ago' in item:
            return date.today()
        else:
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