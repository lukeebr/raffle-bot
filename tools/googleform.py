import requests, json, time, settings, sys, re
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class GoogleForm:
    def __init__(self, profile, proxy, csv_headers):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        self.csv_headers = csv_headers
        self.session = requests.session()
        self.link = profile[0]
        self.email = None
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('Google Form', 'Starting Task...')
        self.get_info()
        self.submit_entry()

    def get_info(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Google Form', 'Getting Form Page...')
            try:
                page = self.session.get(self.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    self.fvv = soup.find('input',{'name':'fvv'})['value']
                    self.draft_response = soup.find('input',{'name':'draftResponse'})['value']
                    self.page_history = soup.find('input',{'name':'pageHistory'})['value']
                    self.fbzx = soup.find('input',{'name':'fbzx'})['value']
                    self.form_url = soup.find('form', {'method':'POST'})['action']
                    return
                else:
                    logger.task_failed('Google Form', 'Failed Getting Form Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Google Form', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Google Form', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sys.exit(0)

    def submit_entry(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Google Form', 'Submitting Entry...')
            try:
                data = {}

                for value in self.csv_headers[1:]:
                    answer = self.profile[1:][self.csv_headers[1:].index(value)]
                    data[value] = answer
                    if '@' in answer:
                        self.email = answer

                submit_entry = self.session.post(self.form_url, data=data)
                if submit_entry.status_code == 200:
                    logger.task_success('Google Form', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Google Form', self.email])
                    sendWebhook('raffle', site='Google Form', link=self.link, proxy=self.proxy, email=self.email)
                    return
                else:
                    logger.task_failed('Google Form', 'Entry Failed')
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Google Form', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Google Form', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sys.exit(0)
                    
