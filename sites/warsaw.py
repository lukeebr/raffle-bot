import requests, json, time, settings, random, cloudscraper, sys
import publicip
from injection import injection
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class Warsaw:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        if proxy != None:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':False},doubleDown=False,requestPostHook=injection,debug=False)
            self.session.proxies.update(formatProxy(self.proxy))
        else:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':True},doubleDown=False,requestPostHook=injection,debug=False)
        logger.task_pending('Warsaw', 'Starting Task...')
        self.get_info()
        self.submit()

    def get_info(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Warsaw', 'Getting Raffle Page')
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    if self.profile.size.lower() == 'random':
                        sizes = soup.findAll('select', {'name':'drop_down'})[0].findChildren()
                        self.profile.size = random.choice(sizes[1:])['value']
                    self.token = soup.find('input', {'name':'_token'})['value']
                    return
                else:
                    logger.task_failed('Warsaw', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Warsaw', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Warsaw', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Warsaw', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)


    def submit(self):
        while self.errors != settings.error_limit:
            try:
                data = {
                    '_token': self.token,
                    'imie': self.profile.first_name,
                    'nazwisko': self.profile.last_name,
                    'email': self.profile.email,
                    'numer_telefonu': self.profile.phone,
                    'numer_telefonu': self.profile.phone_code + ' ' + self.profile.phone,
                    'odpowiedz': self.profile.city,
                    'birthday': self.profile.birth_year + '-' + self.profile.birth_month + '-' + self.profile.birth_day,
                    'country': self.profile.country,
                    'drop_down': self.profile.size,
                    'regulamin': 'on',
                    'zgoda': 'on',
                    'zapisz': 'save'
                }
                logger.task_pending('Warsaw', 'Submitting Entry...')
                submit = self.session.post('https://z.chmielna20.pl/skepta-x-nike', data=data)
                if submit.status_code == 200:
                    logger.task_success('Warsaw', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Warsaw', self.profile.email])
                    sendWebhook('raffle', site='Warsaw', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Warsaw', 'Entry Failed')
                    sendWebhook('raffle', site='Warsaw', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Warsaw', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Warsaw', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Warsaw', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
