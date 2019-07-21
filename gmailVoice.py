import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
import mimetypes
import os
from apiclient import errors
import speech_recognition as sr
from gtts import gTTS

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://mail.google.com/']

def main():
    creds = ''
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    #Connect to API
    service = build('gmail', 'v1', credentials=creds)
  
    return service

def senderMailId(service):
  profile = (service.users().getProfile(userId='me').execute())
  senderMail = profile['emailAddress'] 
  
  return senderMail


def CreateMessage(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def SendMessage(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    #API Call
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print( 'Message Id: %s' % message['id'])
    return message
  except errors.HttpError:
    print ('An error occurred:')

def verifyCommon(part,data):
  talkTome('Is the '+part+' '+data+' correct')
  yesORno = ''
  yesORno = myCommand()
  if 'yes' in yesORno:
    return True
  else :
    return False


def talkTome(audio):
    print(audio)
    tts = gTTS(text=audio, lang='en')
    tts.save('GmailAudio.mp3')
    os.system('mpg321 GmailAudio.mp3')

def RecipientEmailDomain():
  domainInfo = 'Choose the recipient mail ID domain,The available options are : gmail.com, outlook.com, hotmail.com, yahoo.com'

  talkTome(domainInfo)

  domainAddress = 'null'
  domainID = ''
  domainID = myCommand()
  
  if  'Gmail' in domainID or 'gmail.com' in domainID:
    domainAddress = '@gmail.com'
    return domainAddress
  elif 'Outlook' in domainID or 'outlook.com' in domainID:
    domainAddress = '@outlook.com' 
    return domainAddress
  elif 'Yahoo' in  domainID or 'yahoo.com' in domainID:
    domainAddress = '@yahoo.com'   
    return domainAddress
  elif 'Hotmail' in domainID or 'hotmail.com' in domainID:
    domainAddress = '@hotmail.com' 
    return domainAddress   
  else:
    return domainAddress
  

def RecipientEmailUsername():
  talkTome('Kindly type the Recipient email Username')
  print('Type now:')
  username = input()
  return username

def CombineEmailID(username,domain):
  return username+domain
  
def myCommand():
    command = ''
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration= 1)
        print("Talk now")
        audio = r.listen(source, timeout=10)
    
    try:
        command = r.recognize_google(audio, language='en')
        print('you said: '+ command + '\n')        
    #loop back to continue 
    except (sr.UnknownValueError):
        print('Error Recognizing the command')
        
    return command

def gAssist(command):
  domain = ''
  usrname = ''
  if command == 'email':
 
    domain = RecipientEmailDomain()
    verify = verifyCommon('Domain', domain)

    while not verify:
      domain = RecipientEmailDomain()
      verify = verifyCommon('Domain', domain)

    usrname = RecipientEmailUsername()
    verify = verifyCommon('Username', usrname)

    while not verify:
      usrname = RecipientEmailUsername()
      verify = verifyCommon('Username', usrname)
  
  return CombineEmailID(usrname, domain)


def getSubject():
  talkTome('Say the subject')
  subject = myCommand()
  verify =  verifyCommon('Subject', subject)
  while not verify:
    talkTome('Say the subject')
    subject = myCommand()
    verify =  verifyCommon('Subject', subject)

  return subject


def getMessage():
  talkTome('Kindly say the message')
  message = myCommand()

  verify = verifyCommon('Message', message)
  while not verify:
    talkTome('Kindly say the message')
    message = myCommand()
    verify = verifyCommon('Message', message)

  return message

if __name__ == '__main__':
    serviceObj = main()
    SenderMailID = senderMailId(serviceObj)
    RecipientMailID =  gAssist(myCommand())
    mailSubject = getSubject()
    mailMessage = getMessage()
    messageObj =  CreateMessage(SenderMailID,RecipientMailID,mailSubject,mailMessage)
    messageSend = SendMessage(serviceObj,'me',messageObj)
