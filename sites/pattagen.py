import requests, json, time, settings, sys, cloudscraper
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from injection import injection

logger = Logger()

class PattaGen:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        if proxy != None:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':False},doubleDown=False,requestPostHook=injection,debug=False)
            self.session.proxies.update(formatProxy(self.proxy))
        else:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':True},doubleDown=False,requestPostHook=injection,debug=False)
        logger.task_pending('Patta Account Generation', 'Starting Task...')
        self.generate_account()

    def generate_account(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Patta Account Generation', 'Generating Account...')
                data = {
                    'form_type': 'create_customer',
                    'utf8': '✓',
                    'customer[first_name]': self.profile.first_name,
                    'customer[last_name]': self.profile.last_name,
                    'customer[email]': self.profile.email,
                    'customer[password]': self.profile.password
                }
                generate_account = self.session.post('https://www.patta.nl/account', data=data, allow_redirects=False)
                if generate_account.status_code == 302:
                    logger.task_success('Patta Account Generation', 'Successful Account Generation')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Patta Account Generation', self.profile.email])
                    sendWebhook('accountgen', site='Patta', proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Patta Account Generation', 'Account Generation Failed')
                    sendWebhook('accountgen', site='Patta', proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Patta Account Generation', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Patta Account Generation', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('accountgen', site='Patta', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
