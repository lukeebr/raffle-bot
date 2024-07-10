import requests, json, time, settings, random, cloudscraper, sys
import publicip
from injection import injection
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from captcha import CaptchaSolver

logger = Logger()

class WoodWood:
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
        logger.task_pending('WoodWood', 'Starting Task...')
        self.get_info()
        self.submit()

    def get_info(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('WoodWood', 'Getting Raffle Page')
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    self.tags = soup.find('input', {'name':'tags[]'})['value']
                    self.token = soup.find('input', {'name':'token'})['value']
                    get_ip = self.session.get('https://api.myip.com')
                    if get_ip.status_code == 200:
                        self.ip = json.loads(get_ip.text)['ip']
                        return
                    else:
                        logger.task_failed('WoodWood', 'Failed Getting IP')
                        self.errors += 1
                        time.sleep(settings.error_delay)
                else:
                    logger.task_failed('WoodWood', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('WoodWood', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('WoodWood', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='WoodWood', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)


    def submit(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('WoodWood', 'Solving ReCaptcha...')
                captcha_token = self.solver.reCaptcha(sitekey='6LfbPnAUAAAAACqfb_YCtJi7RY0WkK-1T4b9cUO8', url=self.profile.link)
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip',
                    'origin': 'https://www.woodwood.com',
                    'content-type': 'application/x-www-form-urlencoded',
                }
                data = {
                    'tags[]': self.tags,
                    'token': self.token,
                    'rule_email': self.profile.email,
                    'fields[Raffle.Phone Number]': self.profile.phone,
                    'fields[Raffle.First Name]': self.profile.first_name,
                    'fields[Raffle.Last Name]': self.profile.last_name,
                    'fields[Raffle.Shipping Address]': self.profile.address1,
                    'fields[Raffle.Postal Code]': self.profile.ZIP,
                    'fields[Raffle.City]': self.profile.city,
                    'fields[Raffle.Country]': self.profile.country,
                    'fields[SignupSource.ip]': self.ip,
                    'fields[SignupSource.useragent]': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
                    'language': 'sv',
                    'g-recaptcha-response': captcha_token
                }
                logger.task_pending('WoodWood', 'Submitting Entry...')
                submit = self.session.post('https://app.rule.io/subscriber-form/subscriber', data=data, headers=headers, allow_redirects=False)
                if submit.headers['Location'] == 'https://www.woodwood.com/en/raffle-confirm-email':
                    logger.task_success('WoodWood', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['WoodWood', self.profile.email])
                    sendWebhook('raffle', site='WoodWood', link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('WoodWood', 'Entry Failed')
                    sendWebhook('raffle', site='WoodWood', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('WoodWood', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('WoodWood', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='WoodWood', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
