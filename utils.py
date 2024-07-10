import json, csv, random, settings, os, glob, requests, time, ctypes, codecs
from datetime import datetime
from termcolor import colored
from colorama import init, Style
from discord_webhook import DiscordWebhook, DiscordEmbed
import threading

lock = threading.Lock()

SUCCESS = 0
FAILED = 0
PROXYCOUNT = 0
CURRENTTASKFILE = ''
DISCORDUSER = ''

init()

class Logger:
    def task_normal(self, site, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored('[', 'white') + colored(site, 'magenta') + colored('] ', 'white') + colored(msg, 'white'))
        lock.release()
        
    def task_pending(self, site, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored('[', 'white') + colored(site, 'magenta') + colored('] ', 'white') + colored(msg, 'yellow'))
        lock.release()
        
    def task_success(self, site, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored('[', 'white') + colored(site, 'magenta') + colored('] ', 'white') + colored(msg, 'green'))
        lock.release()
        
    def task_failed(self, site, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored('[', 'white') + colored(site, 'magenta') + colored('] ', 'white') + colored(msg, 'red'))
        lock.release()
        
    def normal(self, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored(msg, 'white'))
        lock.release()
        
    def pending(self, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored(msg, 'yellow'))
        lock.release()
        
    def success(self, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored(msg, 'green'))
        lock.release()
        
    def failed(self, msg):
        global lock
        lock.acquire()
        print(colored('[', 'white') + colored(str(datetime.now()), 'white') + colored(']', 'white') + colored(' [', 'white') + colored('ExoRaffles', 'magenta') + colored('] ', 'white') + colored(msg, 'red'))
        lock.release()

class RaffleProfile:
    def __init__(self, site, link, size, first_name, last_name, email, password, phone, address1, address2, ZIP, city, country, instagram, raffle_id, size_id, street_number, salutation, question, birth_day, birth_month, birth_year, store, state, instore, phone_code):
        self.site = site
        self.link = link
        self.size = size
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone = phone
        self.address1 = address1
        self.address2 = address2
        self.ZIP = ZIP
        self.city = city
        self.country = country
        self.instagram = instagram
        self.raffle_id = raffle_id
        self.size_id = size_id
        self.street_number = street_number
        self.salutation = salutation
        self.question = question
        self.birth_day = birth_day
        self.birth_month = birth_month
        self.birth_year = birth_year
        self.store = store
        self.state = state
        self.instore = instore
        self.phone_code = phone_code

class AccountGenProfile:
    def __init__(self, site, first_name, last_name, email, password, salutation, address1, address2, street_number, ZIP, city, country, phone, birth_month, birth_day, birth_year):
        self.site = site
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.salutation = salutation
        self.address1 = address1
        self.address2 = address2
        self.street_number = street_number
        self.ZIP = ZIP
        self.city = city
        self.country = country
        self.phone = phone
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.birth_year = birth_year

def updateStatusBar(updateValue):
    global SUCCESS
    global FAILED
    global CURRENTTASKFILE
    global PROXYCOUNT
    global DISCORDUSER

    if 'success' in updateValue.lower():
        SUCCESS += 1
    elif 'failed' in updateValue.lower():
        FAILED += 1

    os.system(f"title {DISCORDUSER}'s ExoRaffles / Success: {str(SUCCESS)} - Failed: {str(FAILED)} - CSV: {CURRENTTASKFILE} - Proxies: {str(PROXYCOUNT)}")

class LinkOpenerProfile:
    def __init__(self, link):
        self.site = None
        self.link = link
        
def readData(file):
    with open(file, 'r') as f:
        data = json.load(f)
        f.close()
        return data

def writeData(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)
        f.close()

def fetchProfiles(file, mode):
    with codecs.open(file, 'r', 'utf-8') as f:
        profiles = []
        readCSV = csv.reader(f, delimiter=',')
        if mode == 'headers':
            return next(readCSV)
        next(readCSV)
        if mode == 'typeform' or mode == 'googleform':
            for row in readCSV:
                profiles.append(row)
            return profiles
        
        for row in readCSV:
            if mode == 'raffle':
                profile = RaffleProfile(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25])
            elif mode == 'accountgen':
                profile = AccountGenProfile(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15])
            elif mode == 'linkopener':
                profile = LinkOpenerProfile(row[0])
            profiles.append(profile)
        f.close()
        return profiles

def fetchProxies(file):
    with open(file, 'r') as f:
        proxies = []
        lines = f.read().splitlines()
        for line in lines:
            proxies.append(line)
        f.close()
        return proxies

def formatProxy(proxy):
    try:
        proxy_parts = proxy.split(":")
        ip, port, user, passw = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
        return {
            "http": "http://{}:{}@{}:{}".format(user, passw, ip, port),
            "https": "https://{}:{}@{}:{}".format(user, passw, ip, port)
        }
    except IndexError:
        return {"http": "http://" + proxy, "https": "https://" + proxy}

def getProxy():
    try:
        proxies = fetchProxies('proxies.txt')
        if len(proxies) == 0:
            return None
        else:
            return random.choice(proxies)
    except:
        return None

def sendWebhook(webhook_type, site=None, link=None, proxy=None, email=None, size=None, success=True):
    if settings.discord_webhook != '':
        try:
            webhook = DiscordWebhook(url=settings.discord_webhook, username='Exo Raffles', avatar_url='https://cdn.discordapp.com/attachments/760233146976567326/760435744908640256/Profile-Picture.png')
            if success:
                if webhook_type == 'raffle':
                    embed = DiscordEmbed(title='Successful Raffle Entry!', color=1834808)
                    embed.add_embed_field(name='Site', value=str(site),inline=True)
                    embed.add_embed_field(name='Email', value=f'||{email}||',inline=True)
                    embed.add_embed_field(name='Proxy', value=f'||{proxy}||',inline=True)
                    embed.add_embed_field(name='Size', value=str(size),inline=True)
                    embed.add_embed_field(name='Link', value=f'||{link}||',inline=True)
                elif webhook_type == 'accountgen':
                    embed = DiscordEmbed(title='Successful Account Generation!', color=1834808)
                    embed.add_embed_field(name='Site', value=str(site),inline=True)
                    embed.add_embed_field(name='Email', value=f'||{email}||',inline=True)
                    embed.add_embed_field(name='Proxy', value=f'||{proxy}||',inline=True)
                elif webhook_type == 'linkopener':
                    embed = DiscordEmbed(title='Successfully Opened Link!', color=1834808)
                    embed.add_embed_field(name='Link', value=f'||{link}||',inline=True)
            else:
                if webhook_type == 'raffle':
                    embed = DiscordEmbed(title='Failed Raffle Entry!', color=16717600)
                    embed.add_embed_field(name='Site', value=str(site),inline=True)
                    embed.add_embed_field(name='Email', value=f'||{email}||',inline=True)
                    embed.add_embed_field(name='Proxy', value=f'||{proxy}||',inline=True)
                    embed.add_embed_field(name='Size', value=str(size),inline=True)
                    embed.add_embed_field(name='Link', value=f'||{link}||',inline=True)
                elif webhook_type == 'accountgen':
                    embed = DiscordEmbed(title='Failed Account Generation!', color=16717600)
                    embed.add_embed_field(name='Site', value=str(site),inline=True)
                    embed.add_embed_field(name='Email', value=f'||{email}||',inline=True)
                    embed.add_embed_field(name='Proxy', value=f'||{proxy}||',inline=True)
                elif webhook_type == 'linkopener':
                    embed = DiscordEmbed(title='Link Opener Failed!', color=16717600)
                    embed.add_embed_field(name='Link', value=f'||{link}||',inline=True)
            embed.set_footer(text='Powered by Exo Raffles ©', icon_url='https://cdn.discordapp.com/attachments/668496310982279171/822210851858546728/image0.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()

        except:
            pass

def addToCSV(file, data):
    try:
        with open(file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)
            f.close()
    except:
        pass

def getCSVs():
    return glob.glob('tasks*.csv')
    
