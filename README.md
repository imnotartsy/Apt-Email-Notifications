# Apt-Email-Notifications

This is a tool that sends you an email when it has detected changes between your local state (stored in `lastPrices.json`) and data pulled from a URL.

I have used this to monitor the price/avaliability of apartments at a specific complex. This tool works best when it is set to run on a cron job, so that you can get regular updates.


## USAGE: `python3 pullMT.py`

### How to Run:
- Add run the depency installation: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client` (or `pip install -r requirements.txt`)
- Get your credentials (credentials.json) from the Google Cloud Console (this may involve making a new project with the Gmail API enabled)
- Get added as a test user in the Google Cloud Console project 
- Set Control/Config Vars (below) to your desired settings + potentially `room_types` and `fields`

## Control/Config Vars:
- `MOCK` - If True, the script will prefill 'changes' with a mock response to make testing the email sending easier
- `SENDEMAIL` - If True, the script will send an email if there are changes
- `VERBOSE` - If True, the script will print out the changes it has detected + additional information

## File Structure:
- `pullMT.py` - Main script: pulls + parses data, compares it to the last pulled data, and sends an email if there are changes
- `sendGmail.py` - Script to send an email using the Gmail API
- `lastPrices.json` - File to store the last pulled data
- `credentials.json` - File to store your Google Cloud credentials
- `token.json` - File generated by the Google Cloud API when you run the script for the first time (and everytime you need to reauthenticate)


## References
- [Google Cloud Console](https://console.cloud.google.com/)
- [Gmail API](https://developers.google.com/gmail/api/guides/sending#python)
- [Google Cloud Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)