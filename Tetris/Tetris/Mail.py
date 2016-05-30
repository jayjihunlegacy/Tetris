import mimetypes
import smtplib
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

host = "smtp.snu.ac.kr"
port = "587"
senderAddr = "t080205@snu.ac.kr"
jayAddr = "t080205@gmail.com"

sub = "Genetic Algorithm Notification"
body = "Genome found!"

def makeMessege(subject, body, senderAddr, recAddr):#sender and receiver meaningless
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = senderAddr
    msg['To'] = recAddr
    return msg

def send(msg, senderAddr, recAddr):#real sender and receiver
    s = smtplib.SMTP(host,port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("t080205", "dlwlgns777")
    s.sendmail(senderAddr,[recAddr], msg.as_string())
    s.close()
    print("Mail to",recAddr,"sent successfully.")

def sendEmail(subject, body):
	try:
		msg = makeMessege(subject,body,senderAddr, jayAddr)
		send(msg,senderAddr,jayAddr)
	except:
		pass
