import requests, time, sys, json, settings, subprocess, os, threading, utils, psutil
from utils import Logger, readData, writeData

logger = Logger()

class Authentication:
    def __init__(self):
        os.system('title Authentication')
        self.DISCWEBHOOK = ''
        self.APIKEY = ''
        self.user_key = settings.user_key
        self.session = requests.session()
        self.startSec()
        self.envCheck()
        self.main()

    def main(self):
        self.getActivationToken()
        self.auth()

    def deleteActivationToken(self):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.APIKEY}'
            }
            
            delete_activation = self.session.delete('https://exorobotics.net/api/v1/activations/' + self.activation_token, headers=headers)
            response = json.loads(delete_activation.text)

            if response['success']:
                logger.success('Successfully Deactivated License')
                self.removeActivationToken()
                time.sleep(3)
                os._exit(0)
            else:
                logger.failed(response['message'])
                time.sleep(5)
                os._exit(0)
        except:
            logger.failed('Error Deactivating License')
            time.sleep(5)
            os._exit(0)

    def startSec(self):
        try:
            threading.Thread(target=self.proccessSecurity, args=[True,]).start()
        except Exception as e:
            logger.failed(f'Failed executing [SecProcess {e}]')
            time.sleep(3)
            os._exit(0)

    def proccessSecurity(self, loop):
        os.environ['NO_PROXY'] = 'discordapp.com' 
        os.environ['NO_PROXY'] = self.DISCWEBHOOK
        banned_processes = ['charles', 'wireshark', 'http debugger', 'burp', 'httpdebugger', 'dnspy', 'fiddler', 'http debugger pro', 'httpdebuggerpro', 'ilspy', 'justdecompile', 'just decompile', 'ollydbg', 'ida', 'ida64', 'immunitydebugger', 'megadumper', 'mega dumper', 'processhacker', 'process hacker', 'ollydbg', 'cheat engine', 'cheatengine', 'codebrowser', 'code browser', 'scylla', 'megadumper 1.0 by codecracker / snd']
        if loop:
            while True:
                processes = [n.name().lower().strip(".exe") for n in psutil.process_iter()]
                if any(n in processes for n in banned_processes):
                        banned = [n for n in banned_processes if n in processes][0]
                        webhook = DiscordWebhook(url=self.DISCWEBHOOK)
                        embed = DiscordEmbed(title='Security Issues: HTTP Interceptor')
                        embed.set_footer(text='Security ')
                        embed.add_embed_field(name='Process', value=str(banned))
                        embed.add_embed_field(name='HWID', value=self.GetUUID())
                        embed.add_embed_field(name="Key", value=settings.user_key)
                        webhook.add_embed(embed)
                        webhook.execute()
                        os._exit(0)
                time.sleep(10)
        else:
                processes = [n.name().lower().strip(".exe") for n in psutil.process_iter()]
                if any(n in processes for n in banned_processes):
                        banned = [n for n in banned_processes if n in processes][0]
                        webhook = DiscordWebhook(url=self.DISCWEBHOOK)
                        embed = DiscordEmbed(title='Security Issues: HTTP Interceptor')
                        embed.set_footer(text='Security')
                        embed.add_embed_field(name='Process', value=str(banned))
                        embed.add_embed_field(name='HWID', value=self.GetUUID())
                        embed.add_embed_field(name="Key", value=settings.user_key)
                        webhook.add_embed(embed)
                        webhook.execute()
                        os._exit(0)
            

    def envCheck(self): 
        try:
            if os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('CURL_CA_BUNDLE') or os.environ.get('https_proxy'):
                sys.exit(0)
            if os.environ['REQUEST_CA_BUNDLE'] or os.environ['CURL_CA_BUNDLE'] or os.environ['https_proxy']:
                sys.exit(0)
        except:
            pass

    def getActivationToken(self):
        try:
            data = readData('data.json')
            token = data['activationToken']
            if token != '':
                self.activation_token = token
            else:
                self.createActivation()
        except:
            self.createActivation()

    def createActivation(self):
        try:
            self.hwid = self.getUUID()
            self.device_name = os.environ['COMPUTERNAME']

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.APIKEY}'
            }
            
            payload = {
                'key': self.user_key,
                'activation': {
                    'hwid': self.hwid,
                    'device_name': self.device_name
                }
            }
            
            create_activation = self.session.post('https://exorobotics.net/api/v1/activations', json=payload, headers=headers)
            response = json.loads(create_activation.text)
            
            if response['success']:
                self.setActivationToken(response['activation_token'])
                self.activation_token = response['activation_token']
            else:
                logger.failed(response['message'])
                time.sleep(5)
                os._exit(0)
        except:
            logger.failed('Error Creating Activation')
            time.sleep(5)
            os._exit(0)

    def setActivationToken(self, token):
        try:
            writeData('data.json', {'activationToken':token})
        except:
            logger.failed('Error Setting Activation Token')
            time.sleep(5)
            os._exit(0)
        
    def removeActivationToken(self):
        try:
            writeData('data.json', {'activationToken':''})
        except:
            logger.failed('Error Removing Activation Token')
            time.sleep(5)
            os._exit(0)

    def getUUID(self):
        try:
            cmd = 'wmic csproduct get uuid'
            uuid = str(subprocess.check_output(cmd))
            pos1 = uuid.find("\\n")+2
            uuid = uuid[pos1:-15]
            os.environ['HWID'] = uuid
            return uuid
        except:
            logger.failed("Exiting in 3s, Error Getting ID!")
            time.sleep(5)
            os._exit(0)

    def auth(self):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.APIKEY}'
            }

            get_activation = self.session.get(f'https://exorobotics.net/api/v1/activations/{self.activation_token}', headers=headers)
            response = json.loads(get_activation.text)
            
            if response['success']:
                USER = response['user']['discord_username']
                utils.DISCORDUSER = USER
                logger.success('Successfully Authenticated')
                logger.normal(f'Welcome, {USER}')
                return
            else:
                if response['message'] == 'Invalid activation token':
                    self.removeActivationToken()
                    self.main()
                else:
                    logger.failed(response['message'])
                    time.sleep(5)
                    os._exit(0)
        except:
            logger.failed('Error Authenticating')
            time.sleep(5)
            os._exit(0)
