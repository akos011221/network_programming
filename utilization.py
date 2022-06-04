import sys
from sys import exit
from getpass import getpass
from netmiko import ConnectHandler
import os
import re
import math
from prettytable import PrettyTable
import socket

print("-"*18)
ipaddr = input("Device hostname or IP: ")
passw = getpass() 
print("-"*18)


with ConnectHandler(ip=ipaddr,
                    username=os.getlogin(),
                    password=passw,
                    fast_cli=False,
                    device_type="cisco_ios") as ch:

    command = ch.send_command("show ver | i cisco.*with|Cisco.*with")
    model = re.findall(r"[cC]isco.*\(", command)
    model = " ".join(model)
    model = model.replace(" (", "").replace("Cisco", "").replace("cisco", "").strip().replace(")","")
    model = model.split("/")[0]
    

    command = ch.send_command("show interface desc")
    lines = command.split("\n")

    wan_int = ""
    for line in lines:
        if "WAN" in line and "down" not in line and "Tu" not in line:
            wan_int = line

    if wan_int == "":
        print("Couldn't find the WAN interface or it's down")
        exit()
    else:
        wan_int = re.findall(r".*up", wan_int)
        wan_int = " ".join(wan_int)
        wan_int = wan_int.split()[0]
               
        txload = ""
        rxload = ""

        command = ch.send_command(f'show interface {wan_int}')
        command = command.strip()
        
        int_desc = re.findall(r"Desc.*", command)
        int_desc = " ".join(int_desc)
        int_desc = int_desc.replace("Description: ", "")
        
        bw = re.findall(r"BW \d{0,7}", command)
        bw = " ".join(bw).replace("BW ", "").strip()
        bw = int(bw) / 1000
        
        txload = re.findall(r"txload.*,", command)
        txload = " ".join(txload)
        rxload = re.findall(r"rxload [0-99].*", command)
        rxload = " ".join(rxload)
        
        txload = txload.replace("txload ","").replace(",","")
        rxload = rxload.replace("rxload ","")
        split = txload.split("/")
        txload = ( int(split[0])/int(split[1]) )
        split = rxload.split("/")
        rxload = ( int(split[0])/int(split[1]) )
     

        primary = True
        
        command = ch.send_command('show run | i route-map in-from-dc')
        if not command:
            pass    
        else:
            primary = False
        
        
        packetloss = ""
        destip = ""
        nexthop = ""
        dc_core_sw = ""
        
        
        if primary:
            dc_core_sw = ""
            command = ch.send_command(f'show run | i snmp-server location')
            if "AMER" in command:
                dc_core_sw = "10.123.1.1"
            elif "EMEA" in command:
                dc_core_sw = "10.123.2.2"
            elif "APAC" in command:
                dc_core_sw = "10.123.3.3"
            else:
                dc_core_sw = "10.123.1.1"

            command = ch.send_command(f'ping {dc_core_sw} size 1500 rep 250')
            destip = re.findall(r"Echos to.*,", command)
            destip = " ".join(destip)
            destip = destip.replace("Echos to ", "").replace(",", "")
            successrate = re.findall(r"[0-100]* percent", command)
            successrate = " ".join(successrate)
            successrate = successrate.replace(" percent", "")
            packetloss = 100 - int(successrate)
            latency = re.findall(r"\d*/\d*/\d*", command)
            latency = " ".join(latency)

        else:
            command = ch.send_command(f'sho run | i ip nhrp nhs')
            nhsip = re.findall("nhs.*", command)
            nhsip = "\n".join(nhsip)
            split = nhsip.split("\n")
            nhsip = split[0]
            nhsip = nhsip.replace("nhs ", "").replace(" ", "")
    
            destip = nhsip
            
            command = ch.send_command(f'ping {nhsip} siz 1400 rep 420')
            successrate = re.findall(r"[0-100]* percent", command)
            successrate = " ".join(successrate)
            successrate = successrate.replace(" percent", "")
            packetloss = 100 - int(successrate)
            latency = re.findall(r"\d*/\d*/\d*", command)
            latency = " ".join(latency)
            
        
        
        command = ch.send_command(f'show ip cef {destip} | i nexthop|attached')
        nexthop = command.strip().replace("nexthop ", "").replace("attached to", "").strip()
        
        command = ch.send_command("show proc cpu | i seconds")
        raw = re.findall(r"seconds.*", command)
        raw = " ".join(raw)
        raw = raw.replace("seconds: ", "").replace("/", "").replace("; one minute: ", "").replace("; five minutes: ", "").replace("%", " ")
        numbers = raw.split()

               
        seperator = "-"*18
        if dc_core_sw:
          dc_core_sw = socket.gethostbyaddr(dc_core_sw)[0]
          dc_core_sw = dc_core_sw.split('.')[0]
          print(f"MODEL: {model}\n{seperator}\nWAN INTERFACE: {wan_int}\nDESCRIPTION: {int_desc}\nCONFIGURED BANDWIDTH: {int(bw)} Mbps\nBW UTILIZATION (TX): {math.ceil(txload*100)}% -> {math.ceil(txload * int(bw))} Mbps\nBW UTILIZATION (RX): {math.ceil(rxload*100)}% -> {math.ceil(rxload * int(bw))} Mbps\n{seperator}\nPING DESTINATION: {dc_core_sw}\nPACKET LOSS: {packetloss}%\nRTT MIN/AVG/MAX: {latency} ms\n{seperator}\n5 SEC CPU LOAD: {numbers[0]}%\n5 SEC CPU LOAD DUE TO INTERRUPTS: {numbers[1]}%\n5 MIN CPU LOAD: {numbers[3]}%\n{seperator}")
        else:
          destip = socket.gethostbyaddr(destip)[0]
          destip = destip.split('.')[0]
          print(f"MODEL: {model}\n{seperator}\nWAN INTERFACE: {wan_int}\nDESCRIPTION: {int_desc}\nCONFIGURED BANDWIDTH: {int(bw)} Mbps\nBW UTILIZATION (TX): {math.ceil(txload*100)}% -> {math.ceil(txload *int(bw))} Mbps\nBW UTILIZATION (RX): {math.ceil(rxload*100)}% -> {math.ceil(rxload * int(bw))} Mbps\n{seperator}\nPING DESTINATION: {destip}\nPACKET LOSS: {packetloss}%\nRTT MIN/AVG/MAX: {latency} ms\n{seperator}\n5 SEC CPU LOAD: {numbers[0]}%\n5 SEC CPU LOAD DUE TO INTERRUPTS: {numbers[1]}%\n5 MIN CPU LOAD: {numbers[3]}%\n{seperator}")
        
        
