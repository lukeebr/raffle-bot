import requests, json, time, settings, sys
from utils import Logger, sendWebhook, addToCSV, formatProxy, updateStatusBar
from bs4 import BeautifulSoup
from injection import injection
from captcha import CaptchaSolver

logger = Logger()

class NakedCPH:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        self.solver = CaptchaSolver(settings.API)
        self.session = requests.session()
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('NakedCPH', 'Starting Task...')
        self.submit()
            
    def submit(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('NakedCPH', 'Getting Captcha Token...')
                captcha_token = self.solver.reCaptcha(sitekey='6LfbPnAUAAAAACqfb_YCtJi7RY0WkK-1T4b9cUO8',url='https://app.rule.io/subscriber-form/subscriber')
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip',
                    'origin': 'https://www.nakedcph.com',
                    'content-type': 'application/x-www-form-urlencoded',
                }
                payload = {
                    'tags[]': self.profile.raffle_id,
                    'token': 'c812c1ff-2a5a0fe-efad139-d754416-71e1e60-2ce',
                    'rule_email': self.profile.email,
                    'fields[Raffle.First Name]': self.profile.first_name,
                    'fields[Raffle.Instagram Handle]': self.profile.instagram,
                    'fields[Raffle.Last Name]': self.profile.last_name,
                    'fields[Raffle.Phone Number]': self.profile.phone,
                    'fields[Raffle.Shipping Address]': self.profile.address1,
                    'fields[Raffle.Postal Code]': self.profile.ZIP,
                    'fields[Raffle.City]': self.profile.city,
                    'fields[Raffle.Country]': self.profile.country,
                    'fields[SignupSource.ip]': '192.0.0.1',
                    'fields[SignupSource.useragent]': 'Mozilla',
                    'language': 'sv',
                    'g-recaptcha-response': captcha_token
                }
                logger.task_pending('NakedCPH', 'Submitting Entry...')
                submit = self.session.post('https://app.rule.io/subscriber-form/subscriber', data=payload, headers=headers, allow_redirects=False)
                if submit.headers['Location'] == 'https://www.nakedcph.com/en/772/your-registration-for-our-fcfs-was-successful':
                    logger.task_success('NakedCPH', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['NakedCPH', self.profile.email])
                    sendWebhook('raffle', site='NakedCPH', size=self.profile.raffle_id, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('NakedCPH', 'Entry Failed')
                    sendWebhook('raffle', site='NakedCPH', size=self.profile.raffle_id, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except Exception as e:
                logger.task_failed('NakedCPH', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='NakedCPH', size=self.profile.raffle_id, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
            
