import base64
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

from email.message import EmailMessage

from config import GOOGLE_CRED_PATH

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]
CRED_PATH = GOOGLE_CRED_PATH


def send_email(receiver_email: str, additions: list,
               removals: list) -> str:
    """ function: Sends Email to receiver_email with the
    changes in unit availability
    """

    # Auth + Build Service
    creds = None
    if os.path.exists(CRED_PATH + "token.json"):
        creds = Credentials.from_authorized_user_file(CRED_PATH + "token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CRED_PATH + "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(CRED_PATH + "token.json", "w") as token:
            token.write(creds.to_json())

    # Email configuration
    service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message["To"] = receiver_email
    message["Subject"] = "Changes in Unit Availability"

    m = "Changes have been found in unit availability!\n\n"

    if additions:
        m += "Added:\n"
        for change in additions:
            m += F"Unit Type: {change['Unit Type']}\n"
            m += F"\tUnit: {change['Unit']}\n"
            m += F"\tRent: {change['Rent']}\n"
            m += F"\tDeposit: {change['Deposit']}\n"
            m += F"\tDescription: {change['Description']}\n"
            m += F"\tAvaliability: {change['Avaliability']}\n\n"

    if removals:
        m += "Removed:\n"
        for change in removals:
            m += F"Unit Type: {change['Unit Type']}\n"
            m += F"\tUnit: {change['Unit']}\n"
            m += F"\tRent: {change['Rent']}\n"
            m += F"\tDeposit: {change['Deposit']}\n"
            m += F"\tDescription: {change['Description']}\n"
            m += F"\tAvaliability: {change['Avaliability']}\n\n"

    message.set_content(m)
    create_message = {'raw': base64.urlsafe_b64encode(
        message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(
            userId="", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
        message = None

    return m
