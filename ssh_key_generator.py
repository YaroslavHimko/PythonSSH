import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def file_opener(config):
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
        Returns True if ssh key already exists, False if ssh key was not found.
        """
        stdin, stdout, stderr = ssh.exec_command("ls ~/.ssh")
        for line in stdout.readlines():
            line.strip

            if "id_rsa" in line:
                print("Key exists for {}".format(self.username))
                return True
            else:
                return False

    def generate_key(self):
        """
        Generates ssh key for a host machine.
        """
        print("Generating key for {}".format(self.username))
        ssh.exec_command('ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""')
        ssh.exec_command("chmod 700 ~/.ssh | chmod 600 ~/.ssh/id_rsa ")

    def remove_key(self):
        """
        Removes ssh key for a host machine.
        """
        print("Removing key for {}".format(self.username))
        ssh.exec_command("rm -f ~/.ssh/id_rsa")
        ssh.exec_command("rm -f ~/.ssh/id_rsa.pub")

    def connect_to_host(self):
        """
        Establishes connection with a host machine.
        """
        ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)

    def reboot(self):
        """
        Reboots host machine
        """
        print("Rebooting host {}".format(self.ip))
        ssh.exec_command("reboot")


def main():
    try:
        config = file_opener("config.json")
        for host_machine in config["Host"]:
            host = Host(host_machine)
            host.connect_to_host()
            if not host.key_present():
                host.generate_key()
            host.reboot()

    except paramiko.SSHException:
        print("Connection Failed")


if __name__ == '__main__':
    main()
