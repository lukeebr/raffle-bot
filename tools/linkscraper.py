import settings, email, quopri, imaplib, sys, csv
from utils import addToCSV, Logger, updateStatusBar
from bs4 import BeautifulSoup, SoupStrainer

logger = Logger()

class LinkScraper:
    def __init__(self):
        self.links_data = []
        self.scrape_data()

    def scrape_data(self):
        logger.task_pending('Link Scraper', 'Scraping Links...')
        try:
            imap_server = imaplib.IMAP4_SSL(host=settings.imap_server)
            imap_server.login(settings.email, settings.password)
            imap_server.select()
        except Exception as e:
            logger.task_failed('Link Scraper', e)
            time.sleep(3)
            sys.exit(0)

        _, message_numbers_raw = imap_server.search(None, 'ALL')
        for message_number in message_numbers_raw[0].split():
            try:
                links = []
                _, msg = imap_server.fetch(message_number, '(RFC822)')
                message = email.message_from_bytes(msg[0][1])
                sender = message['from']
                recipient = message['to']
                if message.is_multipart():
                    multipart_payload = message.get_payload()
                    for sub_message in multipart_payload:
                        source = quopri.decodestring(sub_message.get_payload())
                        for link in BeautifulSoup(source, 'html.parser', parse_only=SoupStrainer('a')):
                            if link.has_attr('href'):
                                links.append(link['href'])
                                updateStatusBar('success')
                                logger.task_success('Link Scraper', 'Scraped Link')
                                
                else:
                    source = quopri.decodestring(message.get_payload())
                    for link in BeautifulSoup(source, 'html.parser', parse_only=SoupStrainer('a')):
                        if link.has_attr('href'):
                            links.append(link['href'])
                            logger.task_success('Link Scraper', 'Scraped Link')
                if links:
                    addToCSV('scraped links.csv', [sender, recipient] + links)
            except:
                logger.task_failed('Link Scraper', 'Failed Scraping Links')
                updateStatusBar('failed')
                continue

        logger.task_normal('Link Scraper Completed', 'Scraped Link')
            
