import requests
from bs4 import BeautifulSoup
import json

import sendGmail
from config import(
    PRICES_PATH,
    URL,
    EMAIL_RECIPIENTS,
    PRICES_FILE)

# USAGE: python pullMT.py
# How to Run:
# - Add run the depency installation: `pip install google-auth
#   google-auth-oauthlib google-auth-httplib2 google-api-python-client`
# - Get your credentials (credentials.json) from the Google Cloud Console
# - Get added as a test user in the Google Cloud Console project (or make a new
#   project with the Gmail API enabled)
# - Set Control/Config Vars (below) to your desired settings + potentially
#   `room_types` and `fields`

# * Control Vars + Config
MOCK = False
SENDEMAIL = True
VERBOSE = True
PATH = PRICES_PATH
recipients = EMAIL_RECIPIENTS


###############################################################################

# * API Call
url = URL
response = requests.get(url)

# * Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all('table')

# * Parse Data
room_types = ["A1-1", "A1-2", "B2-1", "B2-3", "B2-2", "B2-4", "C3-1"]
fields = ["Unit", "Rent", "Deposit", "Description", "Avaliability"]
types = {}
curr = []
iter = 0

# * Compile Rooms Available
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        values = [cell.text.replace("\n", "").strip() for cell in cells]

        # Only process if the row has the correct number of fields
        if len(values) == 6:
            cleaned = values
            cleaned[1] = float(cleaned[1].split("$")[0])  # remove dollar sign
            cleaned[4] = cleaned[4][:10]          # only keep date (YYYY-MM-DD)

            # Convert array to dict with fields as keys
            curr_dict = {}
            for i in range(len(fields)):
                curr_dict[fields[i]] = cleaned[i]
            curr.append(curr_dict)

    # Add the current room type to the types dict
    types[room_types[iter]] = curr
    curr = []
    iter += 1

# * Print number of each room type + calculate total avaliable
if VERBOSE:
    total = 0
    print("Units Available:")
    for key in types:
        print(f"\t{key}: {len(types[key])}")
        total += len(types[key])
    print(f"Total: {total}")


# * Open Past Data
try:
    with open(PATH + PRICES_FILE) as f:
        lastTypes = json.load(f)

# * if PRICES_FILE does not exist, create it
except FileNotFoundError:
    lastTypes = {}
    for key in types:
        lastTypes[key] = []
    print("No previous data found, creating file")

# # * Compare Data
changes = False
added = []
removed = []
for key in types:
    # Convert each array of dicts to a set of tuples
    types_set = set([tuple(d.items()) for d in types[key]])

    # Check if the key is in the lastTypes dict (gently reduntent but protects
    # against missing keys/adding new keys)
    if key not in lastTypes:
        lastTypes[key] = []
    lastTypes_set = set([tuple(d.items()) for d in lastTypes[key]])

    # Check if the sets are different, if so print the changes
    if types_set != lastTypes_set:
        changes = True

        # Find the difference between the two sets
        curr_added = [dict(d) for d in types_set - lastTypes_set]
        curr_removed = [dict(d) for d in lastTypes_set - types_set]

        # add "key" to each dict in the set
        for d in curr_added:
            d["Unit Type"] = key
        for d in curr_removed:
            d["Unit Type"] = key
        
        # append the difference to the added/removed lists
        added = added + curr_added
        removed = removed + curr_removed

        print(f"Changes Found in {key} Units!")
        if VERBOSE:
            if len(added) > 0: print("Added:", json.dumps(added, indent=4))
            if len(removed) > 0: print("Removed:", json.dumps(removed, indent=4))

if not changes:
    print("No Changes Found")

# * Update Last Prices
with open(PATH + PRICES_FILE, "w") as f:
    json.dump(types, f, indent=4)

############################################################################################################

# mocked data
if MOCK:
    changes = True
    added = []
    removed = [
        {
            "Unit": "1234",
            "Rent": 1000.0,
            "Deposit": "$0",
            "Description": "filler",
            "Avaliability": "2025-12-01"
        }
    ]


# if changes, send email
if changes:

    # * Send Email
    if SENDEMAIL:
        for recipient in recipients:
            content = sendGmail.send_email(recipient, added, removed)

            if VERBOSE: print(content)
            print("Email sent!")
    else:
        print("Configured to not send email not sent")
        print("To send email, set SENDEMAIL to True in pullMT.py")

        print("Changes Found in Units")
        if VERBOSE:
            if len(added) > 0: print("Added:", json.dumps(added, indent=4))
            if len(removed) > 0: print("Removed:", json.dumps(removed, indent=4))
