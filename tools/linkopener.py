import requests, time, settings, cloudscraper, sys
from injection import injection
from utils import getProxy, formatProxy, Logger, sendWebhook, addToCSV, updateStatusBar

logger = Logger()

class LinkOpener:
    def __init__(self, profile, proxy):
        self.profile = profile
        self.errors = 0
        self.proxy = proxy
        if proxy != None:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':'2captcha','api_key':settings.two_captcha_key, 'no_proxy':False},doubleDown=False,requestPostHook=injection,debug=False)
            self.session.proxies.update(formatProxy(self.proxy))
        else:
            self.session = cloudscraper.create_scraper(browser={'browser': 'chrome','mobile': False,'platform': 'windows'},captcha={'provider':'2captcha','api_key':settings.two_captcha_key, 'no_proxy':True},doubleDown=False,requestPostHook=injection,debug=False)
        logger.task_pending('Link Opener', 'Starting Task...')
        self.open_link()

    def open_link(self):
        while self.errors != settings.error_limit:
            try:
                logger.task_pending('Link Opener', 'Opening Link...')
                page = self.session.get(self.profile.link)
                if page.status_code == 200:
                    logger.task_success('Link Opener', 'Successfully Opened Link')
                    updateStatusBar('success')
                    addToCSV('entered.csv', ['Link Opener', self.profile.link])
                    sendWebhook('linkopener', proxy=self.proxy, link=self.profile.link)
                    return
                else:
                    logger.task_failed('Link Opener', 'Failed Opening Link')
                    self.errors += 1
                    time.sleep(settings.error_delay)
            except requests.exceptions.ProxyError:
                logger.task_failed('Link Opener', 'Proxy Error, Rotating Proxy')
                self.proxy = getProxy()
                self.session.proxies.update(formatProxy(self.proxy))
            except Exception as e:
                logger.task_failed('Link Opener', e)
                self.errors += 1
                time.sleep(settings.error_delay)
        else:
            updateStatusBar('failed')
            sys.exit(0)
