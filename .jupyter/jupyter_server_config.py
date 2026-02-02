c.ServerProxy.servers = {
    'proxy-test': {
    'command': ['python', '-m', 'test_jupyter_proxy'],
    'port': 9999,
    'timeout': 30,
    'absolute_url': False,
    'launcher_entry': {'enabled': True, 'title': 'Jupyter Proxy Test'}
    }
}