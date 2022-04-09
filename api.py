from utils import create_scenario
import requests
import re


class YandexAPI:
    quasar_url = "https://iot.quasar.yandex.ru/m/user"
    music_url = "https://api.music.yandex.net"
    session = requests.session()
    csrf_token = None
    music_uid = 0
    login = ""
    password = ""

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.session.headers.update({
            'User-Agent': 'Chrome',
            'Host': 'passport.yandex.ru'
        })

        resp = self.session.get("https://passport.yandex.ru/am?app_platform=android")
        m = re.search(r'"csrf_token" value="([^"]+)"', resp.text)
        auth_payload = {"csrf_token": m[1]}
        self.csrf_token = m[1]

        resp = self.session.post("https://passport.yandex.ru/registration-validations/auth/multi_step/start",
                                 {**auth_payload, "login": login}).json()
        print(resp)
        auth_payload["track_id"] = resp["track_id"]

        self.session.post("https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password",
                          {**auth_payload, "password": password,
                           'retpath': "https://passport.yandex.ru/am/finish?status=ok&from=Login"})
        self.get_music_id()

    def _update_csrf(self):
        raw = self.session.get("https://yandex.ru/quasar").text
        m = re.search('"csrfToken2":"(.+?)"', raw)
        self.csrf_token = m[1]

    def get_scenarios(self):
        return self.session.get(self.quasar_url + "/scenarios").json()['scenarios']

    def get_speakers(self):
        return self.session.get(self.quasar_url + "/devices").json()['speakers']

    def add_scenario(self, payload):
        self._update_csrf()
        return self.session.post(self.quasar_url + "/scenarios", json=payload,
                                 headers={'x-csrf-token': self.csrf_token}).json()

    def exec_scenario(self, id):
        self._update_csrf()
        return self.session.post(self.quasar_url + "/scenarios/" + id + "/actions",
                                 headers={'x-csrf-token': self.csrf_token}).json()

    def play_song(self, speaker, name, id):
        logic = {
            'type': 'devices.capabilities.quasar.server_action',
            'state': {
                'instance': 'text_action',
                'value': 'Включи ' + name,
            }
        }

        scenario = create_scenario('Включи', speaker, logic)
        self._update_csrf()
        self.session.put(self.quasar_url + "/scenarios/" + id, json=scenario, headers={'x-csrf-token': self.csrf_token})
        self._update_csrf()
        return self.session.post(self.quasar_url + "/scenarios/" + id + "/actions",
                                 headers={'x-csrf-token': self.csrf_token}).json()

    def get_music_id(self):
        self.music_uid = str(self.session.get(self.music_url + '/users/' + self.login).json()['result']['uid'])

    def get_liked_tracks(self):
        track_list = \
            self.session.get(self.music_url + "/users/" + self.music_uid + "/likes/tracks").json()['result']['library'][
                'tracks']
        track_ids = [track['id'] for track in track_list]
        self._update_csrf()
        return self.session.post(self.music_url + "/tracks", {'track-ids': track_ids}).json()['result']
