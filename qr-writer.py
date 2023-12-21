import os
import time
import tkinter
from datetime import datetime
from tkinter import filedialog

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv

import segno
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# Pull in environment variables
SPREADSHEET_URL = os.getenv('SPREADSHEET_URL')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
READ_RANGE_NAME = os.getenv('READ_RANGE_NAME')
WRITE_RANGE_NAME = os.getenv('WRITE_RANGE_NAME')

# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Track last created QR code
last_qr = ''
last_job_number = ''
last_print_file_path = ''


def search_for_file_path():
    """Returns a file path that is selected using a file browser"""
    # TODO: Find out how to focus the window as it sometimes is hidden behind program
    while True:
        time.sleep(1)
        root = tkinter.Tk()
        root.withdraw()  # Hides tkinter window

        curr_dir = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=root, initialdir=curr_dir, title='Please select a file')
        if len(temp_path) > 0:
            return temp_path
        else:
            while True:
                choice = input('No file selected - try again? (y/n) ')
                if choice.lower() == 'y':
                    break
                elif choice.lower() == 'n':
                    exit_program()
                else:
                    print("Invalid choice" + '\n')


def label_qr():
    """Adds job number label to bottom of QR code"""
    # Open the desired Image you want to add text on
    i = Image.open(last_qr)

    # To add 2D graphics in an image call draw Method
    font = ImageFont.truetype("arial.ttf", 20)
    img = ImageDraw.Draw(i)

    # Add Text to an image
    img.text((28, 375), last_job_number, font=font)

    # Save the image on which we have added the text
    i.save(last_qr)


def open_qr():
    """Opens the last created QR code"""
    global last_qr
    print('\n' + 'Opening QR Code...' + '\n')
    os.startfile(last_qr, 'open')


def exit_program():
    """Exits the program after designated time"""
    seconds_until_exit = 3
    print('\n' + f'Exiting program in {seconds_until_exit} seconds')
    time.sleep(seconds_until_exit)
    exit()


def show_menu():
    """Shows a menu after creating a QR code to allow user to pick next action"""
    time.sleep(1)
    print('\n' + 'What would you like to do?')
    print('1. Open QR and create another')
    print('2. Open QR and exit')
    print('3. Create another')
    print('4. Exit')
    choice = input('\n' + 'Enter your choice: ')

    if choice == '1':
        open_qr()
        start_program()
    elif choice == '2':
        open_qr()
        start_program()
        exit_program()
    elif choice == '3':
        start_program()
    elif choice == '4':
        exit_program()
    else:
        print('\n' + 'Invalid option - please try again')
        show_menu()


def start_program():
    """Creates QR code and displays next step menu"""
    write_qr()
    show_menu()


def add_to_sheet(values):
    """Adds a new QR code to the Google Sheet for tracking"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Append job to spreadsheet
    try:
        service = build('sheets', 'v4', credentials=creds)

        body = {'values': values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range='A1:C2',
                valueInputOption='USER_ENTERED',
                body=body
            )
            .execute()
        )
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def write_qr():
    """Creates and saves a QR code by using user input"""
    print('\x1B[4m' + 'QR Writer' + '\x1B[0m')

    # Get job number (used to name QR file)
    job_number = input('Enter the job number: ')

    # Track the most recently created job number
    global last_job_number
    last_job_number = job_number

    # Get file path (encoded into QR)
    print('\n' + 'Choose your print file...')
    print_path = search_for_file_path()
    global last_print_file_path
    last_print_file_path = print_path

    # Make QR code by encoding file path
    qr_code = segno.make_qr(print_path, version=8)

    # Save QR code using job number
    new_qr_filename = f'qr_{job_number}.png'

    # Track the most recently created QR code
    global last_qr
    last_qr = new_qr_filename

    # Print status to user
    print('\n' + 'QR code created...')
    print(f"Named '{new_qr_filename}' and points to '{print_path}'")
    qr_code.save(new_qr_filename, scale=7)

    # Add label to QR code
    label_qr()

    # Structure QR data for spreadsheet
    values = [
        [
                datetime.today().strftime('%Y-%m-%d'),  # Date as yyyy-mm-dd
                last_job_number,  # Job number
                last_print_file_path,  # Print File Path
                'New',  # Status will be 'New' by default
        ],
    ]

    # Append values to spreadsheet
    add_to_sheet(values)


if __name__ == '__main__':
    start_program()

