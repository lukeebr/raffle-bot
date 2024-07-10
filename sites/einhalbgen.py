import requests, json, time, settings, sys, cloudscraper
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from injection import injection
from captcha import CaptchaSolver

logger = Logger()

class EinhalbGen:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.solver = CaptchaSolver(settings.API)
        self.errors = 0
        self.proxy = proxy
        if proxy != None:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':False},doubleDown=False,requestPostHook=injection,debug=False)
            self.session.proxies.update(formatProxy(self.proxy))
        else:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':settings.API,'api_key':settings.APIKEY, 'no_proxy':True},doubleDown=False,requestPostHook=injection,debug=False)
        logger.task_pending('Einhalb43 Account Generation', 'Starting Task...')
        self.generate_account()
        
    def generate_account(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Einhalb43 Account Generation', 'Solving ReCaptcha...')
                captcha_token = self.solver.reCaptcha(sitekey='6Ld7ha8UAAAAAF1XPgAtu53aId9_SMkVMmsK1hyK', url='https://www.43einhalb.com/registrieren')
                logger.task_pending('Einhalb43 Account Generation', 'Generating Account...')
                if self.profile.salutation == 'm':
                    self.profile.salutation == '1'
                elif self.profile.salutation == 'f':
                    self.profile.salutation == '2'
                elif self.profile.salutation == 'd':
                    self.profile.salutation == '4'
                data = {
                    'personal[email]': self.profile.email,
                    'personal[password]': self.profile.password,
                    'personal[password_repeat]': self.profile.password,
                    'billaddress[company]': '',
                    'billaddress[vatid]': '',
                    'billaddress[salutation]': self.profile.salutation,
                    'billaddress[forename]': self.profile.first_name,
                    'billaddress[lastname]': self.profile.last_name,
                    'billaddress[street]': self.profile.address1,
                    'billaddress[street_number]': self.profile.street_number,
                    'billaddress[addition]': self.profile.address2,
                    'billaddress[zipcode]': self.profile.ZIP,
                    'billaddress[city]': self.profile.city,
                    'billaddress[country]': self.profile.country,
                    'billaddress[phone]': self.profile.phone,
                    'personal[date_of_birth]': self.profile.birth_month + '/' + self.profile.birth_day + '/' + self.profile.birth_year,
                    'shippingaddress[use_shipping_address]': '0',
                    'shippingaddress[company]': '',
                    'shippingaddress[salutation]': '',
                    'shippingaddress[forename]': '',
                    'shippingaddress[lastname]': '',
                    'shippingaddress[street]': '',
                    'shippingaddress[street_number]': '',
                    'shippingaddress[addition]': '',
                    'shippingaddress[zipcode]': '',
                    'shippingaddress[city]': '',
                    'shippingaddress[country]': '',
                    'personal[privacy_consent]': 'register_account_privacy_consent', 
                    'g-recaptcha-response': captcha_token
                }
                generate_account = self.session.post('https://www.43einhalb.com/registrieren', data=data)
                if generate_account.status_code == 200:
                    logger.task_success('Einhalb43 Account Generation', 'Successful Account Generation')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Einhalb43 Account Generation', self.profile.email])
                    sendWebhook('accountgen', site='Einhalb43', proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Einhalb43 Account Generation', 'Account Generation Failed')
                    sendWebhook('accountgen', site='Einhalb43', proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Einhalb43 Account Generation', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Einhalb43 Account Generation', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('accountgen', site='Einhalb43', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
