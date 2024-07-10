import settings
from twocaptcha import TwoCaptcha
from capmonster_python import NoCaptchaTaskProxyless
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

class CaptchaSolver:
    def __init__(self, API):
        self.API = API
        self.APIKEY = settings.APIKEY

    def reCaptcha(self, sitekey, url):
        if self.API == '2captcha':
            solver = TwoCaptcha(self.APIKEY)
            result = solver.recaptcha(sitekey=sitekey, url=url)
            return result['code']

        elif self.API == 'capmonster':
            capmonster = NoCaptchaTaskProxyless(client_key=self.APIKEY)
            taskId = capmonster.createTask(website_key=sitekey, website_url=url)
            response = capmonster.joinTaskResult(taskId=taskId)
            return response

        elif self.API == 'anticaptcha':
            client = AnticaptchaClient(self.APIKEY)
            task = NoCaptchaTaskProxylessTask(url, sitekey)
            job = client.createTask(task)
            job.join()
            return job.get_solution_response()

        else:
            raise Exception(f'Provided Captcha API {self.API} Does Not Exist')
