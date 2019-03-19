from __future__ import print_function

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1gjePnef_HnYIWNXMkb9uZ1vp9O90MZiOUHFeJNQgkJM'
RANGE_NAME = 'Sheet1!B3:L'

USER_AGENT = 'fidelix-version-fetcher/0.1'


def update(sheet, row, state):
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                   range='Sheet1!L{}:L'.format(row),
                                   valueInputOption='RAW', body={'values': [[state]]}
                                   ).execute()
    return result


def get_version(ip):
    try:
        response = requests.get("http://{}/".format(ip), headers={'user-agent': USER_AGENT}, timeout=30)
    except requests.exceptions.Timeout:
        return "timeout"
    server = response.headers.get("Server", "")
    server = server.lower()
    version = "-"
    if 'fidelix' in server:
        idx = server.find('fidelix')
        version = server[idx+8:]
    return version


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
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

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('IP, Tilanne:')
        i = 2
        with open("status-{}.txt".format(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")), 'w') as f:
            for row in values:
                i += 1
                print('%s' % (row,))
                version = get_version(row[0])
                update(sheet, i, version)
                f.write("{},{}".format(row[0], version))
                if i > 5:
                    break


if __name__ == '__main__':
    main()
