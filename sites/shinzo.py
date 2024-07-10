import requests, json, time, settings, random, cloudscraper, sys
from injection import injection
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar
from bs4 import BeautifulSoup
from captcha import CaptchaSolver

logger = Logger()

class Shinzo:
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
        logger.task_pending('Shinzo', 'Starting Task...')
        self.get_info()
        self.submit()

    def get_info(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Shinzo', 'Getting Raffle Page')
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, features='html.parser')
                    self._wpcf7 = soup.find('input', {'name':'_wpcf7'})['value']
                    self._wpcf7_version = soup.find('input', {'name':'_wpcf7_version'})['value']
                    self._wpcf7_locale = soup.find('input', {'name':'_wpcf7_version'})['value']
                    self._wpcf7_unit_tag = soup.find('input', {'name':'_wpcf7_unit_tag'})['value']
                    self._wpcf7_container_post = soup.find('input', {'name':'_wpcf7_container_post'})['value']
                    self._wpcf7cf_hidden_group_fields = soup.find('input', {'name':'_wpcf7cf_hidden_group_fields'})['value']
                    self._wpcf7cf_hidden_groups = soup.find('input', {'name':'_wpcf7cf_hidden_groups'})['value']
                    self._wpcf7cf_visible_groups = soup.find('input', {'name':'_wpcf7cf_visible_groups'})['value']
                    self._wpcf7cf_options = soup.find('input', {'name':'_wpcf7cf_visible_groups'})['value']
                    self.bb2_screener_ = str(soup.findAll('script', {'type':'text/javascript'})[2]).split("'")[13]
                    self.form_data_element = soup.find('input', {'class':'wpcf7-form-control wpcf7-text'})['name']
                    if self.profile.size.lower() == 'random':
                        sizes = soup.find('select', {'name':'size'}).findChildren()
                        self.profile.size = random.choice(sizes[1:])['value']
                    return
                else:
                    logger.task_failed('Shinzo', 'Failed Getting Raffle Page')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Shinzo', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Shinzo', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Shinzo', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)


    def submit(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Shinzo', 'Solving ReCaptcha...')
                captcha_token = self.solver.reCaptcha(sitekey='6LczOjoUAAAAABEfbqdtD11pFD5cZ0n5nhz89nxI', url=self.profile.link)
                data = {
                    '_wpcf7': self._wpcf7,
                    '_wpcf7_version': self._wpcf7_version,
                    '_wpcf7_locale': self._wpcf7_locale,
                    '_wpcf7_unit_tag': self._wpcf7_unit_tag,
                    '_wpcf7_container_post': self._wpcf7_container_post,
                    '_wpcf7cf_hidden_group_fields': self._wpcf7cf_hidden_group_fields,
                    '_wpcf7cf_hidden_groups': self._wpcf7cf_hidden_groups,
                    '_wpcf7cf_visible_groups': self._wpcf7cf_visible_groups,
                    '_wpcf7cf_options': self._wpcf7cf_options,
                    'lang': 'fr',
                    'your-firstname': self.profile.first_name,
                    'your-name': self.profile.last_name,
                    'your-email': self.profile.email,
                    'your-instagram': self.profile.instagram,
                    'your-tel': self.profile.phone,
                    'delivery[]': '1',
                    'your-address': self.profile.address1,
                    'your-postcode': self.profile.ZIP,
                    'your-city': self.profile.city,
                    'your-country': self.profile.country,
                    'size': self.profile.size,
                    'accept': '1',
                    'g-recaptcha-response': captcha_token,
                    self.form_data_element: '',
                    'bb2_screener_': self.bb2_screener_
                }
                logger.task_pending('Shinzo', 'Submitting Entry...')
                submit = self.session.post('https://raffle.shinzo.paris/wp-json/contact-form-7/v1/contact-forms/' + self._wpcf7 + '/feedback', data=data)
                if 'mail_sent' in submit.text:
                    logger.task_success('Shinzo', 'Successful Entry')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Shinzo', self.profile.email])
                    sendWebhook('raffle', site='Shinzo', link=self.profile.link, proxy=self.proxy, email=self.profile.email)
                    return
                else:
                    logger.task_failed('Shinzo', 'Entry Failed')
                    sendWebhook('raffle', site='Shinzo', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
                    self.errors += 1
            except requests.exceptions.ProxyError:
                logger.task_failed('Shinzo', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Shinzo', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sendWebhook('raffle', site='Shinzo', link=self.profile.link, proxy=self.proxy, email=self.profile.email, success=False)
            sys.exit(0)
