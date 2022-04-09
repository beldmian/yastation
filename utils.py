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
