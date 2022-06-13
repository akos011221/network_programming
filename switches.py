## finds the "Down" interfaces on a list of switches and prints the date since they are down.

from getpass import getpass
from netmiko import ConnectHandler
import os
import re
import csv

password = getpass()
switches = []

with open('switches-list') as f:
    lines = f.readlines()
    for line in lines:
        switches.append(line)

for dev in switches:

    verbose = True
    # print('Connecting to ' + dev)
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
          if "Gi" in inf:
            inf_num = inf.replace("Gi","")
          if "Te" in inf:
            inf_num = inf.replace("Te","")
          out = session.send_command(f"show int {inf} | in line")
          print(out.replace("is down, line protocol is ", ""))
          out = session.send_command(f"show log | in {inf_num}.*down")
          lines = out.split("\n")
          date = lines[-1].partition("%")[0]
          if not date:
            print("No info found.")
          else:
            print("Status is down since\t", date)

          print()

    except Exception as e:
        print(f"Can't connect to {dev} {e}.\n")
