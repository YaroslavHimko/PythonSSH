import paramiko
import json
import logging
import os
from platform import system

logging.basicConfig(filename="host_actions.log", level=logging.INFO, filemode="w")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def file_opener(config):
    """
    Gets config file path as a parameter and returns JSON file content
    """
    with open(config) as f:
        data = json.load(f)
        return data


class Host(object):
    def __init__(self, host_machine):
        self.ip = host_machine["ip"]
        self.port = host_machine["port"]
        self.username = host_machine["username"]
        self.password = host_machine["password"]

    def key_present(self):
        """
        Returns True if ssh key already exists.
        False if ssh key was not found.
        """
        stdin, stdout, stderr = ssh.exec_command("ls ~/.ssh")
        for line in stdout.readlines():
            line.strip

            if "id_rsa" in line:
                logging.info("id_rsa already exists for {}".format(self.username))
                return True
            else:
                logging.info("id_rsa doesn't exist for {}".format(self.username))
                return False

    def generate_key(self):
        """
        Generates ssh key for a host machine.
        """
        logging.info("Generating key for {}".format(self.username))
        ssh.exec_command('ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""')
        ssh.exec_command("chmod 700 ~/.ssh | chmod 600 ~/.ssh/id_rsa ")

    def remove_key(self):
        """
        Removes ssh key for a host machine.
        """
        logging.info("Removing key for {}".format(self.username))
        ssh.exec_command("rm -f ~/.ssh/id_rsa")
        ssh.exec_command("rm -f ~/.ssh/id_rsa.pub")

    def connect_to_host(self):
        """
        Establishes connection with a host machine.
        """
        ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)

    def reboot(self):
        """
        Reboots host machine.
        """
        logging.info("Rebooting host {}".format(self.ip))
        ssh.exec_command("reboot")

    def ping(self):
        """
        Returns True if ping to a host was successful (returned response 0).
        Else returns False.
        """
        parameter = '-n' if system().lower() == 'windows' else '-c'
        response = os.system("ping {} 1 {}".format(parameter, self.ip))
        if response == 0:
            logging.info("Successful ping to a {}".format(self.ip))
            return True
        else:
            logging.info("Ping failed for a {}".format(self.ip))
            return False


def main():
    try:
        config = file_opener("config.json")
        for host_machine in config["Host"]:
            host = Host(host_machine)
            try:
                if host.ping():
                    host.connect_to_host()
                    if not host.key_present():
                        host.generate_key()
                        host.reboot()
            except paramiko.AuthenticationException:
                logging.error("Authentication failed")
            except paramiko.SSHException:
                logging.error("Unable to establish connection")
    except FileNotFoundError:
        logging.error("Config file was not found")


if __name__ == '__main__':
    main()