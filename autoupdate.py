import requests, time, json, os
from utils import Logger, readData, writeData
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

logger = Logger()

class AutoUpdate:
    def __init__(self):
        self.version = '2.00.05'
        self.checkForUpdate()

    def checkForUpdate(self):
        logger.pending('Checking For Update...')
        try:
            newestVersion = json.loads(requests.get('https://exoraffles.s3.eu-north-1.amazonaws.com/version.json').text)['Version']
            if self.version != newestVersion:
                logger.pending(f'Found New Version {newestVersion}, Starting Update...')
                self.update()
            else:
                return
        except:
            logger.failed('Error Checking For Update')
            time.sleep(10)
            os._exit(0)

    def update(self):
        try:
            resp = urlopen("https://exoraffles.s3.eu-north-1.amazonaws.com/Exo+Raffles.zip")
            zipfile = ZipFile(BytesIO(resp.read()))
            
            with zipfile.open('Exo Raffles/settings.json') as f:
                serverJSON = json.load(f)

            with open('settings.json', 'r') as f:
                hostJSON = json.load(f)
                for key in serverJSON:
                    if key not in hostJSON:
                        hostJSON.update({key:serverJSON[key]})
                for key in list(hostJSON):
                    if key not in serverJSON:
                        del hostJSON[key]

            with open('settings.json', 'w') as f:
                f.write(json.dumps(hostJSON, indent=4, separators=(',', ': ')))

            for file in zipfile.namelist():
                if file.endswith('.exe'):
                    exe_file = file

            with zipfile.open(exe_file) as f:
                exe_data = f.read()

            with open(exe_file.split('/')[-1], 'wb') as f:
                f.write(exe_data)

            logger.success('Successfully Updated! Closing In 3 Seconds...')
            time.sleep(3)
            os._exit(0)
            
        except:
            logger.failed('Error Updating Application')
            time.sleep(10)
            os._exit(0)
