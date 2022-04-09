NEEDED_SCENARIOS = ['Старт', 'Стоп', 'Следующий', 'Предыдущий', 'Тише', 'Громче', 'Включи']
NEEDED_SCENARIOS_LOGICS = {
    'Старт': {
        'type': 'devices.capabilities.quasar.server_action',
        'state': {
            'instance': 'text_action',
            'value': 'Включи мою музыку вперемешку',
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
