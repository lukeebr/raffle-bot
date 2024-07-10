import requests, json, time, settings, random, sys
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class Elementos:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        self.session = requests.session()
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('4Elementos', 'Starting Task...')
        self.get_info()
        self.submit_entry()

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('4Elementos', 'Getting Raffle Page...')
            try:
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    self.lang = soup.find('input', {'id':'lang'})['value']
                    self.formID = soup.find('input',{'id':'formId'})['value']
                    self.formURL = soup.find('form')['action']
                    return
                else:
                    logger.task_failed('4Elementos', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('4Elementos', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('4Elementos', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='4Elementos',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def submit_entry(self):
        while self.errors != settings.error_limit:
            logger.task_pending('4Elementos', 'Submitting Entry...')
            try:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Host': 'app3.salesmanago.pl',
                    'Sec-Fetch-Dest': 'iframe',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
                    }
                data = {
                    'lang': self.lang,
                    'formId': self.formID,
                    'sm-form-email': self.profile.email,
                    'sm-form-name': self.profile.first_name + ' ' + self.profile.last_name,
                    'sm-form-birthday': '{}-{}-{}'.format(self.profile.birth_year, self.profile.birth_month, self.profile.birth_day),
                    'sm-form-street': self.profile.address1,
                    'sm-form-city': self.profile.city,
                    'sm-form-province': self.profile.state,
                    'sm-form-zip': self.profile.ZIP,
                    'sm-form-country': self.profile.country,
                    'sm-form-phone': self.profile.phone,
                    'sm-cst.instagram_user': self.profile.instagram,
                    'sm-cst.size': self.profile.size,
                    'sm-form-consent-id-1601-POLITICAPRIVACIDAD': 'true',
                    'sm-form-consent-name-POLITICAPRIVACIDAD': 'true',
                    'sm-form-agreement_agreement_2': 'true'
                    }
                submit = self.session.get('https://app3.salesmanago.pl' + self.formURL, params=data, headers=headers)
                if 'THANKS!' in submit.text:
                    logger.task_success('4Elementos', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['4Elementos', self.profile.email])
                    sendWebhook('raffle', site='4Elementos',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('4Elementos', 'Entry Failed')
                    sendWebhook('raffle', site='4Elementos',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('4Elementos', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('4Elementos', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='4Elementos',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
