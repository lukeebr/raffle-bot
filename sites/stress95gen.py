import requests, json, time, settings, sys, cloudscraper
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from injection import injection

logger = Logger()

class Stress95Gen:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        if proxy != None:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':False},doubleDown=False,requestPostHook=injection,debug=False)
            self.session.proxies.update(formatProxy(self.proxy))
        else:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':True},doubleDown=False,requestPostHook=injection,debug=False)
        logger.task_pending('Stress95 Account Generation', 'Starting Task...')
        self.get_info()
        self.generate_account()

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Stress95 Account Generation', 'Getting Account Generation Page...')
            try:
                page = self.session.get('https://stress95.com/en/auth/view?op=register')
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    self.anti_csrf_token = soup.find('input', {'name':'_AntiCsrfToken'})['value']
                    return
                else:
                    logger.task_failed('Stress95 Account Generation', 'Failed Getting Account Generation Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Stress95 Account Generation', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Stress95 Account Generation', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('accountgen', site='Stress95', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def generate_account(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Stress95 Account Generation', 'Generating Account...')
            try:
                data = {
                    '_AntiCsrfToken': self.anti_csrf_token,
                    'firstName': self.profile.first_name,
                    'email': self.profile.email,
                    'password': self.profile.password,
                    'action': 'register'
                }
                generate_account = self.session.post('https://stress95.com/en/auth/submit', data=data)
                if json.loads(generate_account.text)['Response']['Success']:
                    logger.task_success('Stress95 Account Generation', 'Successful Account Generation')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Stress95 Account Generation', self.profile.email])
                    sendWebhook('accountgen', site='Stress95', proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Stress95 Account Generation', 'Account Generation Failed')
                    sendWebhook('accountgen', site='Stress95', proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Stress95 Account Generation', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Stress95 Account Generation', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('accountgen', site='Stress95', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
