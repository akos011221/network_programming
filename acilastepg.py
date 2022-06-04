import acitoolkit.acitoolkit as ACI
from acitoolkit.acitoolkit import Session
from getpass import getpass
from argparse import ArgumentParser
import sys


LOGIN = input('Username: ')
PASSWORD = getpass()
print()
apicloc = input("DC code: ")
URL = ''
if apicloc.lower() in 'us':
    URL = 'https://usapic'
elif apicloc.lower() in 'fra':
    URL = 'https://fraapic'
elif apicloc.lower() in 'jp':
    URL = 'https://jpapic'
else:
    print('Invalid site code')
    sys.exit(0)

print(f'Finding the last three EPGs in {apicloc.upper()} ({URL})....')
print("*"*20)

session = Session(URL, LOGIN, PASSWORD)
resp = session.login()
if not resp.ok:
    print('%% Could not login to APIC')
    sys.exit(0)

tenants = ACI.Tenant.get(session)



epglist = []
for tenant in tenants:
    apps = ACI.AppProfile.get(session, tenant)
    for app in apps:
        epgs = ACI.EPG.get(session, app, tenant)
        for epg in epgs:
            epgname = epg.name
            epgnumber = epgname.replace("VLAN","")
            epglist.append(epgnumber)

epglist2 = [ x for x in epglist if x.isdigit() ]
sortedepgs = sorted(epglist2)
print(f'- Vlan{sortedepgs[-3]}\n- Vlan{sortedepgs[-2]}\n- Vlan{sortedepgs[-1]}')
print("*"*20)

