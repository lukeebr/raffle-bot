import requests, json, time, settings, sys, cloudscraper
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from injection import injection
from captcha import CaptchaSolver

logger = Logger()

class NakedCPHGen:
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
        logger.task_pending('NakedCPH Account Generation', 'Starting Task...')
        self.get_info()
        self.generate_account()

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('NakedCPH Account Generation', 'Getting Account Generation Page...')
            try:
                page = self.session.get('https://www.nakedcph.com/en/auth/view?op=register')
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    self.anti_csrf_token = soup.find('input', {'name':'_AntiCsrfToken'})['value']
                    return
                else:
                    logger.task_failed('NakedCPH Account Generation', 'Failed Getting Account Generation Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('NakedCPH Account Generation', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('NakedCPH Account Generation', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('accountgen', site='NakedCPH', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def generate_account(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('NakedCPH Account Generation', 'Solving ReCaptcha...')
                captcha_token = self.solver.reCaptcha(sitekey='6LeNqBUUAAAAAFbhC-CS22rwzkZjr_g4vMmqD_qo', url='https://www.nakedcph.com/en/auth/view?op=register')
                logger.task_pending('NakedCPH Account Generation', 'Generating Account...')
                data = {
                    '_AntiCsrfToken': self.anti_csrf_token,
                    'firstName': self.profile.first_name,
                    'email': self.profile.email,
                    'password': self.profile.password,
                    'subscribe':'1',
                    'termsAccepted': 'true',
                    'g-recaptcha-response': captcha_token,
                    'action': 'register'
                }
                generate_account = self.session.post('https://www.nakedcph.com/en/auth/submit', data=data)
                if json.loads(generate_account.text)['Response']['Success']:
                    logger.task_success('NakedCPH Account Generation', 'Successful Account Generation')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['NakedCPH Account Generation', self.profile.email])
                    sendWebhook('accountgen', site='NakedCPH', proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('NakedCPH Account Generation', 'Account Generation Failed')
                    sendWebhook('accountgen', site='NakedCPH', proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('NakedCPH Account Generation', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('NakedCPH Account Generation', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('accountgen', site='NakedCPH', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
