from getpass import getpass
from netmiko import ConnectHandler
import os
import re

password = getpass()
switches = []

with open('hostnames') as f:
    lines = f.readlines()
    for line in lines:
        switches.append(line)

for dev in switches:

    verbose = True
    cisco_dev = {'device_type': 'cisco_ios', 'ip': dev, 'username': os.getlogin(), 'password': password}
    try:
        session = ConnectHandler(**cisco_dev, fast_cli=True)
        
        print("<--------------------------------------->")
        print(dev.strip().center(40))
        print("<--------------------------------------->")
        print()
        out = session.send_command("show int status")
        lines = out.split("\n")
        interfaces = []
        for line in lines:
          if "Te" in line and "notconnect" in line:
            intf = line.split()[0]
            interfaces.append(intf)
          if "Gi" in line and "notconnect" in line:
            intf = line.split()[0]
            interfaces.append(intf)
        
        for inf in interfaces:
        
          out = session.send_command(f"show int {inf} | in line")
          print(out.replace("is down, line protocol is ", ""))
          out = session.send_command(f"show log | in {inf2}.*down")
          lines = out.split("\n")
          date = lines[-1].partition("%")[0]
          if not date:
            print("DOWN SINCE --> No info, probably it was never up")
          else:
            print("DOWN SINCE --> ", date)
          
          print()

    except Exception as e:
        print(f"Can't connect to {dev} {e}.\n")
