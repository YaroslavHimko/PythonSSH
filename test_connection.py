from host_connector import Host


class TestSuite(object):
    def test_connection(self):
        host_machine = {"ip": "127.0.0.1", "port": 2222, "username": "yaroslav", "password": "passwd"}
        host = Host(host_machine)
        host.connect_to_host()
        assert host.check_connection()
