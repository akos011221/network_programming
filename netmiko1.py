#!/usr/bin/env python

from getpass import getpass
from netmiko import ConnectHandler

user = input("TACACS username: ")
passw = getpass()

with open('commands_file') as file:
    commands = file.read().splitlines()

with open('ipaddresses_file') as file:
    devices = file.read().splitlines()

start_time = datetime.now() 

for device in devices:
    print("Connecting to " + device)
    ip_addr = dev
    cisco_dev = {
        'device_type': 'cisco_ios',
        'ip': ip_addr,
        'username': user.encode('ascii'),
        'password': passw
    }
    
    session = ConnectHandler(**cisco_dev)
    out = session.send_config_set(commands)
    print(out)
      
end_time = datetime.now() 
total_time = end_time - start_time
print(total_time)
