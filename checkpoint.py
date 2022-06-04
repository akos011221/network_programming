import re

from netmiko import ConnectHandler
from getpass import getpass

fw = input("Firewall hostname: ")
ip = input("IP to be resolved: ")
user = input('Username: ')
passw = getpass()

devices = {
    "device_type": "checkpoint_gaia_ssh",
    "ip": fw,
    "username": "user,
    "password": passw,
}

try:
    net_connect = ConnectHandler(**devices)
    output = net_connect.send_command("show arp dynamic all")
    allines = output.split("\n")

    for entry in allines:
        if ip in entry:
            ipmac = entry.split()
            print(f"{ipmac[0]} resolves to {ipmac[1]}")

    net_connect.disconnect()
except:
    print("Error....")
