#!/usr/bin/python


import sys
import optparse
import getpass
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


# Get Options
parser = optparse.OptionParser()

parser.add_option('-f', '--from',
                  dest="fromaddr",
                  default=None,
                  help='Sending address (optional)',
                 )
parser.add_option('-t', '--to',
                  dest="toaddr",
                  default=None,
                  help='Recipient email address(es)',
                 )
parser.add_option('-s', '--subject',
                  dest="subject",
                  default="",
                  help='Email subject text',
                 )
parser.add_option('-c', '--content',
                  dest="content",
                  default="",
                  help='Email body text',
                 )
parser.add_option('-u', '--username',
                  dest="username",
                  default=None,
                  help='Email server username',
                 )
parser.add_option('-p', '--password',
                  dest="password",
                  default=None,
                  help='Email server password',
                 )
parser.add_option('-P', '--port',
                  dest="port",
                  default='587',
                  help='Email server port (default port 587)',
                 )
parser.add_option('-S', '--server',
                  dest="server",
                  default='127.0.0.1',
                  help='Email server (default server 127.0.0.1)',
                 )
parser.add_option('-a', '--attach',
                  dest="attach",
                  default=None,
                  help='Email attachment(s)',
                 )
parser.set_usage("Usage: ./send_email.py [options]")
options, remainder = parser.parse_args()

fromaddr = options.fromaddr
toaddr = options.toaddr
subject = options.subject
content = options.content
username = options.username
password = options.password
port = options.port
server = options.server
attachments = options.attach


# main mail function
def send_mail(send_from, send_to, subject, content, username, password, port, server="127.0.0.1", files=None):
	assert isinstance(send_to, list)

	msg = MIMEMultipart()
	msg['From'] = send_from
	msg['To'] = COMMASPACE.join(send_to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach(MIMEText(content))

	for f in files or []:
		with open(f, "rb") as fil:
			part = MIMEApplication(
				fil.read(),
				Name=basename(f)
			)
			part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
			msg.attach(part)

	server = smtplib.SMTP('%s:%s' % (server, port))
	server.starttls()
	server.login(username, password)
	server.sendmail(username, send_to, msg.as_string())
	server.quit()

# Yes/No prompt function
def yesno(question, default="yes"):
	valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = raw_input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'y' or 'n'.\n")


# Print options to user before sending email
if not toaddr: toaddr = raw_input('\nEnter recipient (or comma separated list): ')
toaddr = toaddr.split(',') if ',' in toaddr else [toaddr]
for addr in toaddr:
	print("\033[93m[-]\033[0m Set recipient:      %s" % addr)
if fromaddr:
	print("\033[93m[-]\033[0m Set from address:   %s" % fromaddr)
print("\033[93m[-]\033[0m Set email subject:  %s" % subject)
print("\033[93m[-]\033[0m Set email content:  %s" % content)
print("\033[93m[-]\033[0m Set email server:   %s:%s" % (server, port))
if attachments:
	attachments = attachments.split(',')
	for attachment in attachments:
		print("\033[93m[-]\033[0m Set attachment:     %s" % attachment)
if username == None:
	try:
		username = raw_input('\nEnter username for server %s: ' % server)
	except:
		print("\n")
		sys.exit()
print("\033[93m[-]\033[0m Set username:       %s" % username)
if not fromaddr: fromaddr = username
if password == None:
	try:
		password = getpass.getpass('\nEnter password for user %s: ' % username)
	except:
		print("\n")
		sys.exit()

# Send email
if yesno("OK. Send email now?"):
	try:
		send_mail(fromaddr, toaddr, subject, content, username, password, port, server, attachments)
		print("\033[92m[+]\033[0m Message sent successfully.")
	except:
		print("\033[91m[!]\033[0m An error occurred:\n")
		raise
else:
        sys.exit()

