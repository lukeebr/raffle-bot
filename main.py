import threading, settings, time, sys, inquirer, os, utils, random
from authentication import Authentication
from autoupdate import AutoUpdate
from utils import readData, fetchProxies, fetchProfiles, Logger, getProxy, getCSVs
from colorama import init, Fore, Back, Style
from termcolor import colored
from pypresence import Presence
from sites.stress95 import Stress95
from sites.stress95gen import Stress95Gen
from sites.einhalb import Einhalb
from sites.einhalbgen import EinhalbGen
from sites.titolo import Titolo
from sites.solebox import Solebox
from sites.ymegen import YMEGen
from sites.yme import YMEUniverse
from sites.nakedcphgen import NakedCPHGen
from sites.nakedcph import NakedCPH
from sites.woodwood import WoodWood
from sites.woodwoodgen import WoodWoodGen
from sites.bstn import BSTN
from sites.pattagen import PattaGen
from sites.patta import Patta
from sites.elementos import Elementos
from sites.shinzo import Shinzo
from sites.maha import Maha
from sites.warsaw import Warsaw
from tools.linkopener import LinkOpener
from tools.linkscraper import LinkScraper
from tools.typeform import Typeform
from tools.googleform import GoogleForm
from minigame import MiniGame
from inquirer.themes import Theme
from blessed import Terminal

init()

logger = Logger()
term = Terminal()

class ExoRafflesTheme(Theme):
    def __init__(self):
        super(ExoRafflesTheme, self).__init__()
        self.Question.mark_color = term.magenta
        self.Question.brackets_color = term.normal
        self.Question.default_color = term.normal
        self.Editor.opening_prompt_color = term.bright_black
        self.Checkbox.selection_color = term.magenta
        self.Checkbox.selection_icon = '>'
        self.Checkbox.selected_icon = 'X'
        self.Checkbox.selected_color = term.magenta + term.bold
        self.Checkbox.unselected_color = term.normal
        self.Checkbox.unselected_icon = 'o'
        self.List.selection_color = term.magenta
        self.List.selection_cursor = '>'
        self.List.unselected_color = term.normal

class Main():
    def __init__(self):
        AutoUpdate()
        self.loadData()
        self.auth = Authentication()
        self.connectRPC()
        self.homePage()
        

    def connectRPC(self):
        try:
            rpc = Presence('761682412375375953')
            rpc.connect()
            rpc.update( details = 'Exo Raffles' , state = 'Smashing EU Raffles' , large_image= 'exo' , small_image = 'crown', start = time.time())
        except:
            logger.failed('Failed Connecting Discord RPC')

    def randomTip(self):
        tips = [
            'We offer 24/7 support in our Discord server!',
            'Confirm raffle entries with our Link Opener!',
            'You can run multiple sites in the same csv'
        ]
        return random.choice(tips)

    def loadData(self):
        os.system('title Loading Data')
        try:
            global user_key, APIKEY, API, capmonster_key, two_captcha_key, discord_webhook, task_delay, entry_delay, error_limit, error_delay, email, password, imap_server
            settingsData = readData('settings.json')
            settings.user_key, settings.API, settings.capmonster_key, settings.two_captcha_key, settings.anticaptcha_key, settings.discord_webhook, settings.task_delay, settings.entry_delay_min, settings.entry_delay_max, settings.error_limit, settings.error_delay, settings.email, settings.password, settings.imap_server = settingsData['User_Key'], settingsData['API'].lower(), settingsData['Capmonster_Key'], settingsData['2Captcha_Key'], settingsData['Anticaptcha_Key'], settingsData['Discord_Webhook'], settingsData['Task_Delay'], settingsData['Entry_Delay_Min'], settingsData['Entry_Delay_Max'], settingsData['Error_Limit'], settingsData['Error_Limit'], settingsData['Email'], settingsData['Password'], settingsData['IMAP Server']
            if settings.API == '2captcha':
                settings.APIKEY = settings.two_captcha_key
            elif settings.API == 'capmonster':
                settings.APIKEY = settings.capmonster_key
            elif settings.API == 'anticaptcha':
                settings.APIKEY = settings.anticaptcha_key
            elif settings.API == '':
                logger.failed('You Have Not Input A Captcha API In settings.json')
            else:
                logger.failed(f'Captcha API {settings.API} Is Not Supported')
        except:
            logger.failed('Error Loading User Data, Please Check settings.json')
            time.sleep(3)
            sys.exit(0)
            
    def homePage(self):
        os.system('title Exo Raffles')
        print(Style.BRIGHT + colored('''
  ___           ___       __  __ _        
 | __|_ _____  | _ \__ _ / _|/ _| |___ ___
 | _|\ \ / _ \ |   / _` |  _|  _| / -_|_-<
 |___/_\_\___/ |_|_\__,_|_| |_| |_\___/__/

                                          ''', 'magenta'))
        print('Tip: ' + self.randomTip())
        print()
        
        options = {
            'Start Raffle Tasks' : [taskLauncher, 'raffle'],
            'Start Account Generation' : [taskLauncher, 'accountgen'],
            'Link Opener' : [taskLauncher, 'linkopener'],
            'Link Scraper' : LinkScraper,
            'Custom Typeform' : [taskLauncher, 'typeform'],
            'Custom Google Form' : [taskLauncher, 'googleform'],
            'Deactivate License' : self.auth.deleteActivationToken
        }

        choices = ['Start Raffle Tasks', 'Start Account Generation', 'Link Opener', 'Link Scraper', 'Custom Typeform', 'Custom Google Form', 'Deactivate License']

        questions = [
          inquirer.List('option',
                        message="Please Select A Module",
                        choices=choices,
                    ),
        ]

        if random.random() < 0.05:
            options['What Is This?'] = MiniGame
            choices.append('What Is This?')
        
        answers = inquirer.prompt(questions, theme=ExoRafflesTheme())

        if type(options[answers['option']]) is list:
            options[answers['option']][0](options[answers['option']][1])
        else:
            options[answers['option']]()

        self.homePage()

class Task:
    def __init__(self, site, profile, proxy, mode, csv_headers=None):
        self.site = site
        self.profile = profile
        self.proxy = proxy
        self.mode = mode
        self.csv_headers = csv_headers

    def run(self):
        if self.mode == 'raffle':
            if self.site.lower() == 'stress95':
                Stress95(self.profile, self.proxy)
            elif self.site.lower() == '43einhalb':
                Einhalb(self.profile, self.proxy)
            elif self.site.lower() == 'titolo':
                Titolo(self.profile, self.proxy)
            elif self.site.lower() == 'solebox':
                Solebox(self.profile, self.proxy)
            elif self.site.lower() == 'nakedcph':
                NakedCPH(self.profile, self.proxy)
            elif self.site.lower() == 'woodwood':
                WoodWood(self.profile, self.proxy)
            elif self.site.lower() == 'ymeuniverse':
                YMEUniverse(self.profile, self.proxy)
            elif self.site.lower() == 'bstn':
                BSTN(self.profile, self.proxy)
            elif self.site.lower() == '4elementos':
                Elementos(self.profile, self.proxy)
            elif self.site.lower() == 'patta':
                Patta(self.profile, self.proxy)
            elif self.site.lower() == 'shinzo':
                Shinzo(self.profile, self.proxy)
            elif self.site.lower() == 'maha':
                Maha(self.profile, self.proxy)
            elif self.site.lower() == 'warsaw':
                Warsaw(self.profile, self.proxy)  
            else:
                logger.failed('Invalid Site: ' + self.site)
        elif self.mode == 'accountgen':
            if self.site.lower() == 'stress95':
                Stress95Gen(self.profile, self.proxy)
            elif self.site.lower() == 'ymeuniverse':
                YMEGen(self.profile, self.proxy)
            elif self.site.lower() == 'nakedcph':
                NakedCPHGen(self.profile, self.proxy)
            elif self.site.lower() == 'woodwood':
                WoodWoodGen(self.profile, self.proxy)
            elif self.site.lower() == 'patta':
                PattaGen(self.profile, self.proxy)
            elif self.site.lower() == '43einhalb':
                EinhalbGen(self.profile, self.proxy)
            else:
                logger.failed('Invalid Site: ' + self.site)
        elif self.mode == 'linkopener':
            LinkOpener(self.profile, self.proxy)
        elif self.mode == 'typeform':
            Typeform(self.profile, self.proxy, self.csv_headers)
        elif self.mode == 'googleform':
            GoogleForm(self.profile, self.proxy, self.csv_headers)

class taskLauncher:
    def __init__(self, mode):
        self.mode = mode
        self.loadProxies()
        self.loadTasks()
        self.launchTasks()
        self.resultPage()

    def loadProxies(self):
        try:
            self.proxies = fetchProxies('proxies.txt')
        except:
            logger.failed('Error Loading Proxies, Check Proxies.txt')
            self.proxies = []

    def loadTasks(self):
        try:
            self.tasks = []
            csvs = getCSVs()
    
            if len(csvs) == 0:
                logger.failed('No CSV Files Found')
                time.sleep(3)
                os._exit(0)
                
            while True:
                questions = [
                  inquirer.List('csv',
                                message="Please Select A CSV",
                                choices=csvs,
                            ),
                ]
                
                answers = inquirer.prompt(questions, theme=ExoRafflesTheme())
                try:
                    profiles = fetchProfiles(answers['csv'], self.mode)
                    break
                except:
                    logger.failed('Error Loading Profiles From ' + answers['csv'])
            for profile in profiles:
                if self.mode == 'typeform':
                    task = Task('typeform', profile, getProxy(), self.mode, fetchProfiles(answers['csv'], 'headers'))
                elif self.mode == 'googleform':
                    task = Task('googleform', profile, getProxy(), self.mode, fetchProfiles(answers['csv'], 'headers'))
                else:
                    task = Task(profile.site, profile, getProxy(), self.mode)
                self.tasks.append(task)
            utils.CURRENTTASKFILE = answers['csv']
            utils.PROXYCOUNT = len(self.proxies)
        except:
            logger.failed('Error Loading Tasks')
            time.sleep(3)
            sys.exit(0)

    def launchTasks(self):
        threads = []
        logger.pending('Starting ' + str(len(self.tasks)) + ' Tasks With ' + str(len(self.proxies)) + ' Proxies')
        for task in self.tasks:
            thread = threading.Thread(target=task.run)
            threads.append(thread)

        for thread in threads:
            thread.start()
            time.sleep(settings.task_delay)

        for thread in threads:
            thread.join()

    def resultPage(self):
        print()
        logger.normal(f'All {str(len(self.tasks))} Tasks Completed')
        logger.success(str(utils.SUCCESS) + ' Successful Tasks')
        logger.failed(str(utils.FAILED) + ' Failed Tasks')
    
if __name__ == '__main__':
    Main()
