#To use this you will need the following libraries. The pyHS100 can be installed through PIP. Alternatively,
# you can obtain it through GadgetReactor's github @ https://github.com/GadgetReactor/pyHS100

from pyHS100 import SmartPlug
import socket
import sched, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Yes this is a global variables
starttime=time.time()


def notifemail(miner):

    #Used for email notification, note.... to get this to work with gmail I needed to enable a setting with
    # to allow for "insecure apps". Do some googling with this, but seriously just setup a miner email to send emails
    # to your regular email.

    fromaddr = "fromemail@gmail.com"
    toaddr = "toemail@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "MINER RESTART INITIATED"

    body = "Blody Hell, " + miner + " had to go and get reset again."
    msg.attach(MIMEText(body, 'plain'))

    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()
    #server.starttls()
    server_ssl.login(fromaddr, "youpasswordhere")
    text = msg.as_string()
    server_ssl.sendmail(fromaddr, toaddr, text)
    server_ssl.close()


def live_check():

    # Please enter the IP of the tplink switches and the host associated to it.
    # example 'miner 01':{'switch':'192.168.1.10','host':'192.168.1.11'
    # The "xx" needs to be removed and replaced with the IP of your devices. If you have less/more
    #  devices, then add or remove to this dataframe as needed, each must be seperated with a comma
    #  and the end must have "}}"
    device = {'miner 01':{'switch':'192.168.1.xx','host':'192.168.1.xx'},
              'miner 02':{'switch':'192.168.1.xx', 'host':'192.168.1.xx'},
              'miner 03':{'switch':'192.168.1.xx', 'host':'192.168.1.xx'},
              'miner 04': {'switch': '192.168.1.xx', 'host': '192.168.1.xx'}}

    for each in device:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print ()
        miners = device[each]
        #print (miners['switch'])
        smartplug = SmartPlug(str(miners['switch']))
        print(smartplug.alias + " -- Host IP: "+ miners['host'] + " -- Smart Plug IP: " + miners['switch'] + " : ")
        print ('Testing SSH on ...' + miners['host'])

        # Change 22 to 3389 for windows, although that is not tested in this script, it should work by theory.
        results = s.connect_ex((miners['host'], 22))

        #print (results)

        if results == 0:
            print ("Port 22 reachable\n")
            #smartplug = SmartPlug(each)
            #print(smartplug.alias)
            #notifemail(str(smartplug.alias))

        else:

            # So the reason this is setup to make the call 3 times is due to how the protocol of a tplink device works.
            # These devices use udp to communicate so only calling ity once can cause the script to fail in it's action

            # also note that this takes advantage of a security flaw in the tplink design. These calls are happening
            # unathenticated, meaning anyone on your network can do this to your devices.

            print("SSH Closed")
            smartplug.state = "OFF"
            time.sleep(1)
            smartplug.state = "OFF"
            time.sleep(1)
            smartplug.state = "OFF"
            time.sleep(10)
            print (smartplug.state)
            smartplug.state = "ON"
            smartplug.state = "ON"
            time.sleep(1)
            smartplug.state = "ON"
            time.sleep(10)
            print(smartplug.state)
            print (smartplug.alias + " NEEDED TO BE RESTARTED\n")

            # sends the email, comment out if you don't want that functionality
            notifemail(str(smartplug.alias))

            #script sleeps for a bit
            time.sleep(30)



        s.close()


if __name__ == "__main__":
    while True:

        #Script goes like this, check the time, check to see if hosts are live, wait 60 seconds and repeat.
        print(time.time())
        live_check()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))



