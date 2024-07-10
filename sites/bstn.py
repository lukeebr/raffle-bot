import requests, json, time, settings, random, cloudscraper, sys
import publicip
from injection import injection
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from captcha import CaptchaSolver

logger = Logger()

class BSTN:
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
        logger.task_pending('BSTN', 'Starting Task...')
        self.get_info()
        self.submit()

    def get_info(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('BSTN', 'Getting Raffle Page')
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    if self.profile.size.lower() == 'random':
                        sizes = soup.findAll('select', {'class':'form-control form-control-lg full-width'})[0].findChildren()
                        self.profile.size = random.choice(sizes[1:])['value']
                    if self.profile.salutation.lower() == 'm':
                        self.profile.salutation = 'male'
                    elif self.profile.salutation.lower() == 'f':
                        self.profile.salutation = 'female'
                    elif self.profile.salutation.lower() == 'd':
                        self.profile.salutation = 'other'
                    return
                else:
                    logger.task_failed('BSTN', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('BSTN', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('BSTN', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='BSTN', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)


    def submit(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('BSTN', 'Solving ReCaptcha...')
                captcha_token = self.solver.reCaptcha(sitekey='6LemOsYUAAAAABGFj8B7eEvmFT1D1j8IbXJIdvNn', url=self.profile.link)
                payload = {
                   "additional":{
                      "instagram":self.profile.instagram
                   },
                   "title":self.profile.salutation,
                   "bDay":self.profile.birth_day,
                   "bMonth":self.profile.birth_month,
                   "email":self.profile.email,
                   "firstName":self.profile.first_name,
                   "lastName":self.profile.last_name,
                   "street":self.profile.address1,
                   "streetno":self.profile.street_number,
                   "address2":self.profile.address2,
                   "zip":self.profile.ZIP,
                   "city":self.profile.city,
                   "country":self.profile.country,
                   "acceptedPrivacy":'true',
                   "newsletter":'false',
                   "recaptchaToken":captcha_token,
                   "raffle":{
                      "raffleId":self.profile.raffle_id,
                      "parentIndex":0,
                      "option":self.profile.size
                   },
                   "issuerId":"raffle.bstn.com"
                }
                logger.task_pending('BSTN', 'Submitting Entry...')
                submit = self.session.post('https://raffle.bstn.com/api/register', json=payload)
                if 'success' in submit.text:
                    logger.task_success('BSTN', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['BSTN', self.profile.email])
                    sendWebhook('raffle', site='BSTN', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('BSTN', 'Entry Failed')
                    sendWebhook('raffle', site='BSTN', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('BSTN', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('BSTN', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='BSTN', size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
