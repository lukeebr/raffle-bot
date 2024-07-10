import requests, json, time, settings, random, sys
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from captcha import CaptchaSolver

logger = Logger()

class Maha:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        self.solver = CaptchaSolver(settings.API)
        self.session = requests.session()
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('Maha', 'Starting Task...')
        self.get_info()
        self.submit_entry()

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Maha', 'Getting Raffle Page...')
            try:
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    self.product = soup.find('input', {'name':'product'})['value']
                    self.productImage = soup.find('input', {'name':'productImage'})['value']
                    self.productId = soup.find('input', {'name':'productId'})['value']
                    if self.profile.size.lower() == 'random':
                        sizes = soup.findAll('select', {'name':'shoeSize'})[0].findChildren()
                        self.profile.size = random.choice(sizes[1:])['value']
                    return
                else:
                    logger.task_failed('Maha', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Maha', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Maha', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Maha',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def submit_entry(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Maha', 'Solving ReCaptcha...')
            captcha_token = self.solver.reCaptcha(sitekey='6LfEefkUAAAAAKlfwnsHEEcvqAfef0Q7PG5cYJcC', url=self.profile.link)
            logger.task_pending('Maha', 'Submitting Entry...')
            try:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Host': 'apps.shopmonkey.nl',
                    'Sec-Fetch-Dest': 'iframe',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
                }
                data = {
                    'product': self.product,
                    'productImage': self.productImage,
                    'productId': self.productId,
                    'dontfill': '',
                    'g-recaptcha-response': captcha_token,
                    'firstname': self.profile.first_name,
                    'lastname': self.profile.last_name,
                    'phone': self.profile.phone,
                    'email': self.profile.email,
                    'shoeSize': self.profile.size,
                    'instagram': self.profile.instagram,
                    'shipping': 'shipping',
                    'street': self.profile.address1,
                    'nr': self.profile.street_number,
                    'zipcode': self.profile.ZIP,
                    'city': self.profile.city,
                    'country': self.profile.country
                }
                submit = self.session.post('https://apps.shopmonkey.nl/maha/raffle/raffle.php', data=data, headers=headers)
                if json.loads(submit.text)['status'] == 'success':
                    logger.task_success('Maha', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Maha', self.profile.email])
                    sendWebhook('raffle', site='Maha',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Maha', 'Entry Failed')
                    sendWebhook('raffle', site='Maha',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Maha', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Maha', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Maha',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
