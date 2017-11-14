import requests
import logging

from bs4 import BeautifulSoup

from service.brewconfig import BrewConfig

class PowerStrip:
    url = None
    password = None

    PLUG_1 = 'cte1'
    PLUG_2 = 'cte2'
    PLUG_3 = 'cte3'
    PLUG_4 = 'cte4'
    ON = 1
    OFF = 0

    status = {
        PLUG_1: 0,
        PLUG_2: 0,
        PLUG_3: 0,
        PLUG_4: 0
    }

    def __init__(self, url=None, password='1'):
        if url:
            self.url = url
        else:
            self.url = BrewConfig().get('powerstrip')['url']
        self.password = password
        self.status = self.login(password)

    def get_url(self):
        return self.url

    def login(self, password):
        values = '{"pw": password}'
        resp, ok = self.request(referrer="login.html", values=values)
        if ok is not None:
            return None, "couldn't log in"
        return resp, None

    def logout(self):
        values = {}
        self.status = self.request(referrer="login.html", values=values)
        return self.status

    def switch(self, plug, value):
        values = {plug: value}
        self.status, ok = self.request(values=values)
        return self.status

    def request(self, referrer='', values=''):
        url = self.url + referrer
        r = requests.Response
        ok = "Something went wrong"
        try:
            r = requests.post(url, data=values, timeout=10.0)
            r = self.parse_response(r.text)
            ok = None
        except requests.ConnectionError as err:
            r = err.response
            logging.error("PowerStrip ConnectionError: %s", str(err))
            ok = 'ConnectionError'
        finally:
            return r, ok

    def check(self):
        r, ok = self.login(self.password)
        if ok is None:
            return True
        return False

    def parse_response(self, response_data):
        soup = BeautifulSoup(response_data, 'html.parser')
        status = {}
        if soup.script.string[:8] == 'function':
            print("logged out")
        if soup.script.string[4:14] == 'sockstates':
            # soup.script.string[17:26]
            status[PowerStrip.PLUG_1] = int(soup.script.string[18])
            status[PowerStrip.PLUG_2] = int(soup.script.string[20])
            status[PowerStrip.PLUG_3] = int(soup.script.string[22])
            status[PowerStrip.PLUG_4] = int(soup.script.string[24])
        return status

    def fetch_status(self):
        return self.login(self.password)

    def all_off(self):
        self.switch(PowerStrip.PLUG_1, PowerStrip.OFF)
        self.switch(PowerStrip.PLUG_2, PowerStrip.OFF)
        self.switch(PowerStrip.PLUG_3, PowerStrip.OFF)
        # switched on permanently
        self.switch(PowerStrip.PLUG_4, PowerStrip.ON)
