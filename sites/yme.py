import requests, json, time, settings, sys, random
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup

logger = Logger()

class YMEUniverse:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        self.session = requests.session()
        if proxy != None:
            self.session.proxies.update(formatProxy(self.proxy))
        logger.task_pending('YMEUniverse', 'Starting Task...')
        self.start_submission()
        time.sleep(random.uniform(settings.entry_delay_min, settings.entry_delay_max))
        self.submit_entry()

    def start_submission(self):
        while self.errors != settings.error_limit:
            logger.task_pending('YMEUniverse', 'Starting Submission...')
            try:
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    raffle_data = json.loads(str(soup.findAll('script')[2]).split('form: ')[1].split('messages')[0].strip()[:-1])
                    fields = raffle_data['fields']
                    self.name_id = fields[0]['id']
                    self.gender_selection_id = fields[1]['id']
                    
                    if self.profile.salutation == 'm':
                        self.profile.salutation == 'Man'
                        self.gender_id = fields[1]['properties']['choices'][1]['id']
                    elif self.profile.salutation == 'f':
                        self.profile.salutation == 'Woman'
                        self.gender_id = fields[1]['properties']['choices'][0]['id']
                        
                    self.email_id = fields[2]['id']
                    self.phone_id = fields[3]['id']
                    self.instagram_id = fields[4]['id']
                    
                    self.raffle_id = raffle_data['id']
                    submit_raffle = self.session.post('https://ymeuniverse.typeform.com/forms/{}/start-submission'.format(self.raffle_id), headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'})
                    submission_data = json.loads(submit_raffle.text)
                    self.signature = submission_data['signature']
                    self.landed_at = submission_data['submission']['landed_at']
                    return
                else:
                    logger.task_failed('YMEUniverse', 'Failed Starting Submission')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('YMEUniverse', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('YMEUniverse', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='YMEUniverse', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)

    def submit_entry(self):
        while self.errors != settings.error_limit:
            logger.task_pending('YMEUniverse', 'Submitting Entry...')
            try:
                payload = {
                   "signature":self.signature,
                   "form_id":self.raffle_id,
                   "landed_at":self.landed_at,
                   "answers":[
                      {
                         "field":{
                            "id":self.name_id,
                            "type":"long_text"
                         },
                         "type":"text",
                         "text":self.profile.first_name + ' ' + self.profile.last_name
                      },
                      {
                         "field":{
                            "id":self.gender_selection_id,
                            "type":"multiple_choice"
                         },
                         "type":"choices",
                         "choices":[
                            {
                               "id":self.gender_id,
                               "label":self.profile.salutation
                            }
                         ]
                      },
                      {
                         "field":{
                            "id":self.email_id,
                            "type":"email"
                         },
                         "type":"email",
                         "email":self.profile.email
                      },
                      {
                         "field":{
                            "id":self.phone_id,
                            "type":"phone_number"
                         },
                         "type":"phone_number",
                         "phone_number":self.profile.phone
                      },
                      {
                         "field":{
                            "id":self.instagram_id,
                            "type":"short_text"
                         },
                         "type":"text",
                         "text":self.profile.instagram
                      }
                   ]
                }
                submit_raffle = self.session.post('https://ymeuniverse.typeform.com/forms/{}/complete-submission'.format(self.raffle_id), json=payload, headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'})
                if submit_raffle.status_code == 200:
                    logger.task_success('YMEUniverse', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['YMEUniverse', self.profile.email])
                    sendWebhook('raffle', site='YMEUniverse', link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('YMEUniverse', 'Entry Failed')
                    sendWebhook('raffle', site='YMEUniverse', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('YMEUniverse', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
            except Exception as e:
                logger.task_failed('YMEUniverse', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='YMEUniverse', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
                    
