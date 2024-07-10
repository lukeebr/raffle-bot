import requests, json, time, settings, random, sys
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class Titolo:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        self.session = requests.session()
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('Titolo', 'Starting Task...')
        self.get_info()
        self.submit_entry()

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Titolo', 'Getting Raffle Page...')
            try:
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    self.u = soup.find('input',{'tabindex':'-1'})['name'].split('_')[1]
                    self.id = soup.find('input',{'tabindex':'-1'})['name'].split('_')[2]
                    self.raffle_id = soup.find('input',{'tabindex':'-1'})['name']
                    if self.profile.size.lower() == 'random':
                        sizes = soup.find('select', {'name':'MMERGE6'}).findChildren()
                        self.profile.size = random.choice(sizes[1:])['value']
                    if self.profile.salutation.lower() == 'm':
                        self.profile.salutation = 'Male'
                    elif self.profile.salutation.lower() == 'f':
                        self.profile.salutation = 'Female'
                    return
                else:
                    logger.task_failed('Titolo', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Titolo', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Titolo', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Titolo',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def submit_entry(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Titolo', 'Submitting Entry...')
            try:
                headers = {
                    'authority': 'titolo.us6.list-manage.com',
                    'method': 'GET',
                    'scheme': 'https',
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.9',
                    'referer': 'https://titolo.club/',
                    'sec-fetch-dest': 'script',
                    'sec-fetch-mode': 'no-cors',
                    'sec-fetch-site': 'cross-site',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
                    }
                data = {
                    'u': self.u,
                    'id': self.id,
                    'EMAIL': self.profile.email,
                    'FNAME': self.profile.first_name,
                    'LNAME': self.profile.last_name,
                    'MMERGE5': self.profile.address1,
                    'MMERGE8': self.profile.ZIP,
                    'MMERGE12': self.profile.city,
                    'MMERGE3': self.profile.country,
                    'PHONE': self.profile.phone,
                    'MMERGE9': self.profile.salutation,
                    'MMERGE10': 'en',
                    'MMERGE6': self.profile.size,
                    'MMERGE7': self.profile.instagram,
                    'group[395][1]': '1',
                    'gdpr[995]': 'Y',
                    self.raffle_id: '',
                    'subscribe': 'Subscribe',
                    }
                submit = self.session.get('https://titolo.us6.list-manage.com/subscribe/post-json', params=data, headers=headers)
                if submit.status_code == 200 and json.loads(submit.text)['result'] == 'success':
                    logger.task_success('Titolo', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Titolo', self.profile.email])
                    sendWebhook('raffle', site='Titolo',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Titolo', 'Entry Failed')
                    sendWebhook('raffle', site='Titolo',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Titolo', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Titolo', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Titolo',size=self.profile.size, link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
