"""
CISCO SPA(112) ATA Line registration status mailer
Copyright 2024 M.F. Wieland
"""

import requests
import xml.etree.ElementTree as et
import sys, smtplib, ssl

######################################################################################################################
# Server information
######################################################################################################################

spa_host = "192.168.1.100"
spa_user = "admin"
spa_pass = "password"

email_active = True # Set to False to test status parsing
email_smtp_server = "smtp.mailserver.com"
email_smtp_port = 25
email_smtp_auth = False # set False or True, I created a send connector on office365
email_smtp_user = "" # username for auth
email_smtp_pass = "" # password for auth
email_subject_suffix = "ALARM ATA" # for example ata description
email_sender = "alarm@domain.com"
email_receivers = ["info@domain.com", "second@receiver.com"] # multiple receivers: ["a@bb.cc","b@bb.cc"]

######################################################################################################################
# Get status xml data from cisco spa
######################################################################################################################

response = requests.get('http://{}/admin/status.xml&xuser={}&xpassword={}'.format(spa_host, spa_user, spa_pass))

if response.status_code!=200:

    print("Connection error to CISCO SPA.\n")
    print("Status code: " + str(response.status_code) + "\n\n")
    
    exit(response.status_code)


######################################################################################################################
# Process returned xml data 
######################################################################################################################

tree = et.fromstring(response.content)

line_cnt = 0
out = ""

for child in tree:
    if child.tag=='Registration_State':
        line_cnt+=1
        out += "Line" + str(line_cnt) + " registration state   : " + str(child.text) + "\n"
    if child.tag=='Last_Registration_At':
        out += "Line" + str(line_cnt) + " last registration at : " + str(child.text) + "\n"
        out += "\n"

response.close()


######################################################################################################################
# E-mail
######################################################################################################################

# Print output if email_active is False
if not email_active:
    print(out)
    exit(0)


# send email if email_active is True
message = """\
Subject: CISCO SPA Line registration status - {}

{}""".format(email_subject_suffix,out)

context = ssl.create_default_context()
with smtplib.SMTP(email_smtp_server, email_smtp_port) as server:
    
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    
    if email_smtp_auth:
        server.login(email_smtp_user, email_smtp_pass)
    
    server.sendmail(email_sender, email_receivers, message)
    
