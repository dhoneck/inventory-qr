import os
import time
import tkinter
from tkinter import filedialog

import segno
from PIL import Image, ImageDraw, ImageFont

# Track last created QR code
last_qr = ''
last_job_number = ''


def search_for_file_path():
    """Returns a file path that is selected using a file browser"""
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
    """Adds label to QR code"""
    # Open the desired Image you want to add text on
    i = Image.open(last_qr)

    # To add 2D graphics in an image call draw Method
    font = ImageFont.truetype("arial.ttf", 20)
    img = ImageDraw.Draw(i)

    # Add Text to an image
    img.text((40, 340), last_job_number, font=font)

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

    # Make QR code by encoding file path
    qr_code = segno.make_qr(print_path, version=3)

    # Save QR code using job number
    new_qr_filename = f'qr_{job_number}.png'

    # Track the most recently created QR code
    global last_qr
    last_qr = new_qr_filename

    # Print status to user
    print('\n' + 'QR code created...')
    print(f"Named '{new_qr_filename}' and points to '{print_path}'")
    qr_code.save(new_qr_filename, scale=10)

    # Add label to QR code
    label_qr()


if __name__ == '__main__':
    start_program()
