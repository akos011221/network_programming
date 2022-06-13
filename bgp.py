
### usage: python bgp.py <router ip/hostname> 
### print the BGP connections on the router(s) with the peer IP, status, uptime/downtime, peer description

import sys
from getpass import getpass
from prettytable import PrettyTable
from netmiko import ConnectHandler
import os
import pwd

cmargs = []
n = len(sys.argv)
for i in range(1, n):
    cmargs.append(sys.argv[i])
    
uptime = 0
if 'upt' in cmargs:
    uptime = 1
    cmargs.remove('upt')


    
password = getpass()

ptable = PrettyTable()
ptable = PrettyTable(["Peer", "Status", "Time", "Description"])


for dev in cmargs:

    verbose = True
    print('Connecting to ' + dev)
    cisco_dev = {'device_type': 'cisco_ios', 'ip': dev, 'username': os.getlogin(), 'password': password}
    try:
        session = ConnectHandler(**cisco_dev, fast_cli=True)
        
        out = session.send_command('enable')

        out = session.send_command('show ip bgp all summ')
        if '% BGP not active' in out:
            print('[!] BGP is not configured on ' + dev)

        else:
            out = session.send_command('show bgp ipv4 unic sum | begin Nei')

            for i in out.splitlines()[1:]:  

                pieces = i.split()

                out = session.send_command(
                    'show bgp ipv4 unicast neighbors ' + pieces[0] + ' | include Description')
                check = out.split(' ')  
                desc_str = ''

                if len(check) > 1:
                    desc_str = out.strip().replace("Description: ", "")
                else:
                    desc_str = 'N/A'
        
      
                if pieces[9] == 'Active' or pieces[9] == 'Idle':

              
                    if len(pieces) <= 10:

                        ptable.add_row([pieces[0], pieces[9], pieces[8], desc_str])
                        

                    else:
                        ptable.add_row([pieces[0], pieces[9], pieces[8], desc_str])

           
                else:
                    ptable.add_row([pieces[0], "Up", pieces[8], desc_str])
            
            print(ptable)
            ptable.clear_rows()
        
        
        if uptime == 1:
            out = session.send_command('show version | i upt|Last')
            print('\n' + out)
    
            out = ''

 
        out = session.send_command('show clock')
        print(f'[Clock: {out}]')
        print("\n")
    
    except Exception as e:
        print(f"Can't connect to {dev}.\n")

        
    

