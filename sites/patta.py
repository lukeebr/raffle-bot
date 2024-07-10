import requests, json, time, settings, random, cloudscraper, sys
import publicip
from injection import injection
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class Patta:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        if proxy != None:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':False},doubleDown=False,requestPostHook=injection,debug=False)
            self.session.proxies.update(formatProxy(self.proxy))
        else:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':True},doubleDown=False,requestPostHook=injection,debug=False)
        logger.task_pending('Patta', 'Starting Task...')
        self.login()
        self.get_info()
        self.submit()

    def login(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Patta', 'Logging In...')
                data = {
                    'form_type': 'customer_login',
                    'utf8': '✓',
                    'customer[email]': self.profile.email,
                    'customer[password]': self.profile.password
                }
                login = self.session.post('https://www.patta.nl/account/login', data=data, allow_redirects=False)
                if login.status_code == 302:
                    logger.task_normal('Patta', 'Logged In')
                    return
                else:
                    logger.task_failed('Patta', 'Failed Logging In')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Patta', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Patta', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Patta', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Patta', 'Getting Raffle Page...')
            try:
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    self.customer_id = soup.find('input', {'id':'customer-id'})['value']
                    self.product_id = soup.find('input', {'id':'product-id'})['value']
                    self.raffle_id = soup.find('input', {'id':'article-id'})['value']
                    self.raffle_name = soup.find('input', {'id':'product_handle'})['value']
                    if self.profile.size.lower() == 'random':
                        sizes_element = soup.find('div', {'id':'raffle__size-selector-container'}).findChildren()
                        sizes = []
                        for size in sizes_element:
                            if size.name == 'input':
                                sizes.append(size)
                        selected_size = random.choice(sizes)
                        self.profile.size = selected_size['data-sku']
                        self.product_variant = selected_size['data-variant-id']
                    return
                else:
                    logger.task_failed('Patta', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Patta', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Patta', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Patta', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)


    def submit(self):
        while self.errors != settings.error_limit:
            try:
                payload = {
                  "firstName": self.profile.first_name,
                  "lastName": self.profile.first_name,
                  "customerId": self.customer_id,
                  "email": self.profile.email,
                  "productID": self.product_id,
                  "productSizeSKU": self.profile.size,
                  "productVariantId": self.product_variant,
                  "productSlug": self.raffle_name,
                  "raffleId": self.raffle_id,
                  "raffleName": self.raffle_name,
                  "streetAddress": self.profile.address1,
                  "zipCode": self.profile.ZIP,
                  "city": self.profile.city,
                  "country": self.profile.country,
                  "bday": self.profile.birth_day + '/' + self.profile.birth_month + '/' + self.profile.birth_year,
                  "instagram": self.profile.instagram,
                  "newsletter": False
                }
                logger.task_pending('Patta', 'Submitting Entry...')
                submit = self.session.post('https://patta-raffle.vercel.app/api/postRaffleEntry/', json=json.dumps(payload))
                if 'Added to raffle form' in submit.text:
                    logger.task_success('Patta', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Patta', self.profile.email])
                    sendWebhook('raffle', site='Patta', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Patta', 'Entry Failed')
                    sendWebhook('raffle', site='Patta', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Patta', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Patta', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Patta', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
