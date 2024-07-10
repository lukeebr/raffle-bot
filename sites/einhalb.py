import requests, json, time, settings, random, sys
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from captcha import CaptchaSolver

logger = Logger()

class Einhalb:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.solver = CaptchaSolver(settings.API)
        self.errors = 0
        self.proxy = proxy
        self.session = requests.session()
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('43Einhalb', 'Starting Task...')
        self.submit()

    def submit(self):
        headers = {
            'authority': 'releases.43einhalb.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://releases.43einhalb.com/en/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
        }
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('43Einhalb', 'Solving ReCaptcha...')
                captcha_token = self.solver.reCaptcha(sitekey='6Ld7ha8UAAAAAF1XPgAtu53aId9_SMkVMmsK1hyK', url='https://releases.43einhalb.com/')
                if self.profile.salutation == 'm':
                    self.profile.salutation = '1'
                elif self.profile.salutation == 'f':
                    self.profile.salutation = '2'
                data = {
                    'productBsId': self.profile.size_id,
                    'salutation': self.profile.salutation,
                    'firstName': self.profile.first_name,
                    'lastName': self.profile.last_name,
                    'email': self.profile.email,
                    'instagramName': self.profile.instagram,
                    'street': self.profile.address1,
                    'streetNr': self.profile.street_number,
                    'zipCode': self.profile.ZIP,
                    'city': self.profile.city,
                    'country': self.profile.country,
                    'consent': 'Yes, I hereby accept the terms of participation. I confirm to receive emails from 43einhalb about this or similar products regularly. I agree with the privacy policy, which I can revoke any time at datenschutz@43einhalb.com',
                    'gCaptchaToken': captcha_token
                }
                logger.task_pending('43Einhalb', 'Submitting Entry...')
                submit = self.session.post('https://releases.43einhalb.com/enter-raffle', data=data, headers=headers)
                if submit.status_code == 200:
                    logger.task_success('43Einhalb', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['43Einhalb', self.profile.email])
                    sendWebhook('raffle', site='43Einhalb', proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('43Einhalb', 'Entry Failed')
                    sendWebhook('raffle', site='43Einhalb', proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('43Einhalb', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('43Einhalb', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='43Einhalb', proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
