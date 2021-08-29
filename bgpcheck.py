from getpass import getpass
from netmiko import ConnectHandler
import sys

# adding command line args to a list
cmargs = []
n = len(sys.argv)
for i in range(1, n):
    cmargs.append(sys.argv[i])


# device parameters, connecting
device_type = 'cisco_ios'
username = 'te445587teadm'
password = getpass()
verbose = True
device = cmargs[0]
print('-'*20+'\nConnecting to '+device+'\n'+'-'*20)
cisco_dev = {'device_type': 'cisco_ios','ip': device,'username': username,'password': password}
session = ConnectHandler(**cisco_dev)
out = session.send_command_timing('enable')


# bgp summary-check
if 'bgp' in cmargs:
    print('Checking BGP...')

    # checking whether BGP is active on the device..
    out = session.send_command('show bgp ipv4 unicast summary')
    # if not active..
    if '% BGP not active' in out:
        print('BGP is not configured on '+device)

    # if active..
    else:
        # adding each line of the show command output to a list
        out = session.send_command_timing('show bgp ipv4 unicast summary | begin Nei')

        for i in out.splitlines()[1:]:  # looping through the lines, ignoring the header

            pieces = i.split()
            # if peer is Active or Idle and not in Idle (Admin)
            # if pieces' length is larger than 9, then there's an '(Admin)' word after Idle
            if pieces[9] == 'Idle' or 'Active' and len(pieces) <= 9:
                out = session.send_command_timing(
                    'show bgp ipv4 unicast neighbors ' + pieces[0] + ' | include Description')
                check = out.split(
                    ' ')  # checking if there's a Description for the neighbor. If not, then the length of this list is 1
                if len(check) > 1:  # if the length is larger than 1, there's a Description
                    # print via description
                    print('BGP Peer ' + pieces[0] + ' "' + out.replace(' Description: ', '') + '" has been down for ' +
                          pieces[8] + ' on ' + device)
                else:
                    # print w/o description
                    print('BGP Peer ' + pieces[0] + ' has been down for ' + pieces[8] + ' on ' + device)

            elif len(pieces) > 9:  # if the 'pieces' list is larger than 9, the connection is in Idle (Admin) state

                out = session.send_command_timing(
                    'show bgp ipv4 unicast neighbors ' + pieces[0] + ' | include Description')
                check = out.split(' ')  # same description check as above..

                if len(check) > 1:
                    # print via description
                    print('BGP Peer ' + pieces[0] + ' "' + out.replace('Description: ',
                                                                       '') + '" is manually shut down [Idle (Admin)] on ' + device)
                else:
                    # print w/o description
                    print('BGP Peer ' + pieces[0] + ' is manually shut down [Idle (Admin)] on ' + device)









