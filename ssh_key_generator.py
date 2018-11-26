import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

with open("config.json") as f:
    data = json.load(f)
    ips = data["ips"]
    port = data["port"]
    username = data["username"]
    password = data["password"]


    def key_present():
        stdin, stdout, stderr = ssh.exec_command("ls /home/{}/.ssh".format(username))
        for line in stdout.readlines():
            line.strip

            if "id_rsa" in line:
                print("Key exists")
                return True
            else:
                return False


def generate_key(user):
    print("Generating key")
    ssh.exec_command('ssh-keygen -t rsa -f /home/{}/.ssh/id_rsa -q -P ""'.format(user))
    ssh.exec_command("chmod 700 ~/.ssh | chmod 600 ~/.ssh/id_rsa ")


def remove_key(user):
    print("Removing key")
    ssh.exec_command("rm -f /home/{}/.ssh/id_rsa".format(user))
    ssh.exec_command("rm -f /home/{}/.ssh/id_rsa.pub".format(user))


def connect_to_linux(ip):
    ssh.connect(hostname=ip, port=port, username=username, password=password)

    if not key_present():
        generate_key(username)
    else:
        remove_key(username)


def main():
    try:
        for ip in ips:
            connect_to_linux(ip)

    except paramiko.SSHException:
        print("Connection Failed")


if __name__ == '__main__':
    main()
