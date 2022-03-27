import yaml
import requests
import re

with open("config.yaml", "r") as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

LOGIN = conf['username']
PASSWORD = conf['password']

NEEDED_SCENARIOS = ['Старт', 'Стоп', 'Следующий', 'Предыдущий', 'Тише', 'Громче', 'Включи']
NEEDED_SCENARIOS_LOGICS = {
    'Старт': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Включи мою музыку',
        }
    },
    'Стоп': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Выключи музыку',
        }
    },
    'Следующий': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Следующий трек',
        }
    },
    'Предыдущий': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Прошлый трек',
        }
    },
    'Тише': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Сделай тише',
        }
    },
    'Громче': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Сделай громче',
        }
    },
    'Включи': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Включи Never gonna give you up',
        }
    },

}

def create_scenario(scenario, speaker, logic):
    return {
            'name': scenario,
            'icon': 'home',
            'triggers': [{
                'type': 'scenario.trigger.voice',
                'value': scenario[1:]
            }],
            'steps': [{
                'type': 'scenarios.steps.actions',
                'parameters': {
                    'requested_speaker_capabilities': [],
                    'launch_devices': [{
                        'id': speaker,
                        'capabilities': [logic]
                    }]
                }
            }]
        }
class YandexAPI():
    quasar_url = "https://iot.quasar.yandex.ru/m/user"
    session = requests.session()
    csrf_token = None
    def __init__(self):
        resp = self.session.get("https://passport.yandex.ru/am?app_platform=android")
        m = re.search(r'"csrf_token" value="([^"]+)"', resp.text)
        auth_payload = {"csrf_token": m[1]}
        self.csrf_token = m[1]

        resp = self.session.post("https://passport.yandex.ru/registration-validations/auth/multi_step/start",
                {**auth_payload, "login": LOGIN}).json()
        auth_payload["track_id"] = resp["track_id"]

        self.session.post("https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password",
                {**auth_payload, "password": PASSWORD, 'retpath': "https://passport.yandex.ru/am/finish?status=ok&from=Login"})
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
        return self.session.post(self.quasar_url + "/scenarios", json=payload, headers={'x-csrf-token': self.csrf_token}).json()
    def exec_scenario(self, id):
        self._update_csrf()
        return self.session.post(self.quasar_url + "/scenarios/" + id + "/actions", headers={'x-csrf-token': self.csrf_token}).json()
    def play_song(self, speaker, name, id):
        logic = {
            'type': 'devices.capabilities.quasar.server_action',
            'state': {
                'instance': 'text_action',
                'value': 'Включи '+ name,
            }
        }

        scenario = create_scenario('Включи', speaker, logic)
        self._update_csrf()
        self.session.put(self.quasar_url + "/scenarios/" + id, json=scenario, headers={'x-csrf-token': self.csrf_token})
        self._update_csrf()
        return self.session.post(self.quasar_url + "/scenarios/" + id + "/actions", headers={'x-csrf-token': self.csrf_token}).json()



api = YandexAPI()

speakers = api.get_speakers()
print("Выберете устройство: ")
for (i, speaker) in enumerate(speakers):
    print(str(i+1) + ". " + speaker['name'])

number = int(input("Номер: ")) - 1
speaker = speakers[number]['id']
scenarios = api.get_scenarios()
existing_scenarios = [scenario['name'] for scenario in scenarios]
for scenario in NEEDED_SCENARIOS:
    if scenario in existing_scenarios: continue
    if scenario in NEEDED_SCENARIOS_LOGICS:
        logic = NEEDED_SCENARIOS_LOGICS[scenario]
        api.add_scenario(create_scenario(scenario, speaker, logic))
scenarios = api.get_scenarios()
while True:
    print("Выберете действие:")
    print("1. Старт")
    print("2. Стоп")
    print("3. Следующий трек")
    print("4. Предыдущий трек")
    print("5. Тише")
    print("6. Громче")
    print("7. Включи песню")
    number = int(input("Номер: ")) - 1
    if number == 6:
        name = input("Название: ")
        api.play_song(speaker, name, [scenario['id'] for scenario in scenarios if scenario['name'] == 'Включи'][0])
        continue
    scenario = NEEDED_SCENARIOS[number]
    id = ''
    for exscenario in scenarios:
        if exscenario['name'] == scenario:
            id = exscenario['id']
    api.exec_scenario(id)
    print("Done")
