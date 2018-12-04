import paramiko
import json
import logging
import os
from platform import system
import subprocess

logging.basicConfig(filename="host_actions.log", level=logging.INFO, filemode="w")


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
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def key_present(self):
        """
        Returns True if ssh key already exists.
        False if ssh key was not found.
        """
        stdin, stdout, stderr = self._ssh.exec_command("ls ~/.ssh")
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
        self._ssh.exec_command('ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""')
        self._ssh.exec_command("chmod 700 ~/.ssh | chmod 600 ~/.ssh/id_rsa ")

    def check_connection(self):
        return self._ssh.get_transport().is_active()

    def remove_key(self):
        """
        Removes ssh key for a host machine.
        """
        logging.info("Removing key for {}".format(self.username))
        self._ssh.exec_command("rm -f ~/.ssh/id_rsa")
        self._ssh.exec_command("rm -f ~/.ssh/id_rsa.pub")

    def connect_to_host(self):
        """
        Establishes connection with a host machine.
        """
        self._ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)

    def reboot(self):
        """
        Reboots host machine.
        """
        logging.info("Rebooting host {}".format(self.ip))
        self._ssh.exec_command("reboot")

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

    def reboot_and_wait(self):
        """
        Reboots host and waits until ping is OK
        """
        parameter = '-n' if system().lower() == 'windows' else '-c'
        self._ssh.exec_command("reboot")
        response = os.system("ping {} 1 {}".format(parameter, self.ip))
        while response != os.system("ping {} 1 {}".format(parameter, self.ip)):
            response = os.system("ping {} 1 {}".format(parameter, self.ip))

    def execute_remote_command(self):
        """
        Executes command from user input
        """
        user_input = ""
        self._ssh.exec_command("{}".format(user_input))
        while user_input != 'q':
            user_input = input("You are connected to: {}\nEnter command to execute or 'q' to exit.\n".format(self.ip))
            stdin, stdout, stderr = self._ssh.exec_command("{}".format(user_input))
            for line in stdout.readlines():
                line.strip
                print(line)

    def execute_local_command(self):
        user_input = ""
        while user_input != 'q':
            user_input = input("You are connected to: {}\nEnter command to execute or 'q' to exit.\n".format(self.ip))
            p = subprocess.Popen('{}'.format(user_input), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                print(line.strip())


def main():
    try:
        config = file_opener("config.json")
        for host_machine in config["Host"]:
            host = Host(host_machine)
            host.execute_local_command()
            try:
                host.execute_local_command()
            except paramiko.AuthenticationException:
                logging.error("Authentication failed")
            except paramiko.SSHException:
                logging.error("Unable to establish connection")
    except FileNotFoundError:
        logging.error("Config file was not found")


if __name__ == '__main__':
    main()
