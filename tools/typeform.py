import requests, json, time, settings, sys, re, random
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class Typeform:
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
        logger.task_pending('Typeform', 'Starting Task...')
        self.start_submission()
        time.sleep(random.uniform(settings.entry_delay_min, settings.entry_delay_max))
        self.submit_entry()

    def start_submission(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Typeform', 'Starting Submission...')
            try:
                page = self.session.get(self.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    raffle_data = json.loads(str(soup.findAll('script')[2]).split('form: ')[1].split('messages')[0].strip()[:-1])
                    self.raffle_id = raffle_data['id']
                    self.fields = raffle_data['fields']
                    self.site_name = re.search(r'https://(.*?).typeform.com/', self.link).group(1)
                    submit_raffle = self.session.post('https://{}.typeform.com/forms/{}/start-submission'.format(self.site_name, self.raffle_id), headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'})
                    submission_data = json.loads(submit_raffle.text)
                    self.signature = submission_data['signature']
                    self.landed_at = submission_data['submission']['landed_at']
                    return
                else:
                    logger.task_failed('Typeform', 'Failed Starting Submission')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Typeform', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Typeform', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sys.exit(0)

    def submit_entry(self):
        while self.errors != settings.error_limit:
            logger.task_pending('Typeform', 'Submitting Entry...')
            try:
                payload = {
                    'signature':self.signature,
                    'form_id':self.raffle_id,
                    'landed_at':self.landed_at,
                    'answers':[]
                }

                for value in self.csv_headers:
                    for form_field in self.fields:
                        if value == form_field['id']:
                            field_type = form_field['type']
                            answer = self.profile[1:][self.csv_headers[1:].index(value)]
                            if field_type == 'long_text':
                                field = {'field':{'id':form_field['id'],'type':'long_text'},'type':'text','text':answer}
                            elif field_type == 'short_text':
                                field = {'field':{'id':form_field['id'],'type':'short_text'},'type':'text','text':answer}
                            elif field_type == 'multiple_choice':
                                field = {'field':{'id':form_field['id'],'type':'multiple_choice'},'type':'choices','choices':[{'id':answer}]}
                            elif field_type == 'email':
                                self.email = answer
                                field = {'field':{'id':form_field['id'],'type':'email'},'type':'email','email':answer}
                            elif field_type == 'dropdown':
                                field = {'field':{'id':form_field['id'],'type':'dropdown'},'type':'text','text':answer}
                            elif field_type == 'legal':
                                if answer.lower() == 'true':
                                    answer = True
                                elif answer.lower() == 'false':
                                    answer = False
                                field = {'field':{'id':form_field['id'],'type':'legal'},'type':'boolean','boolean':answer}
                            payload['answers'].append(field)
                submit_entry = self.session.post('https://{}.typeform.com/forms/{}/complete-submission'.format(self.site_name, self.raffle_id), json=payload, headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'})
                if submit_entry.status_code == 200:
                    logger.task_success('Typeform', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Typeform', self.email])
                    sendWebhook('raffle', site='Typeform', link=self.link, proxy=self.proxy, email=self.email)
                    return
                else:
                    logger.task_failed('Typeform', 'Entry Failed')
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Typeform', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('Typeform', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sys.exit(0)
                    
