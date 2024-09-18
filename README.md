# SMTP and POP3 Email App

## Introduction
This project is a custom email application that allows users to send and receive emails using the SMTP and POP3 protocols in Python. It uses a simple graphical interface built with Tkinter to provide functionality for sending emails via SMTP and checking emails via POP3.

## Features
- **Send emails** using SMTP
- **Receive emails** using POP3
- Basic GUI for interaction
- Displays received email messages

## Screenshots

### Sending Email (SMTP)
<img width="625" alt="smtp-1" src="https://github.com/user-attachments/assets/b0e2349d-d272-4c4c-bed9-5e1cbd11273f">
<img width="625" alt="smtp-2" src="https://github.com/user-attachments/assets/5768ece2-5d35-42cb-8f49-abacb674bb32">

### Receiving Email (POP3)
<img width="594" alt="pop3-1" src="https://github.com/user-attachments/assets/a0df45ab-d2bf-454d-8c32-8568a769690a">

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/sorooshaghaei/smtp-pop3-with-python.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    python app.py
    ```

## Email Configuration (Important)

### Enable Gmail to Send and Receive Emails

To use this app for sending and receiving Gmail, you need to configure Gmail settings:

1. **Enable Less Secure App Access**: Google requires you to use app-specific passwords for third-party email applications if two-factor authentication is enabled.
   - Visit [Google Account Security](https://myaccount.google.com/security) and enable **App Passwords**. Generate a one-time app password, which will be used instead of your Gmail password in this app.

2. **Enable POP for Receiving Emails**:
   - Go to your [Gmail settings](https://mail.google.com/mail/u/0/#settings/fwdandpop).
   - Under the **Forwarding and POP/IMAP** tab, enable **POP Download**.
   - Choose to enable POP for all mail or mail that arrives from now on, depending on your preference.

### Usage

1. Open the app.
2. To send an email, fill in your Gmail email address, app password, recipient's email, subject, and message body, then click "Send".
3. To check your inbox, enter your Gmail email and app password, and click "Receive". Ensure that POP is enabled in your Gmail account for this feature to work.

## Requirements

- Python 3.x
- `smtplib` for sending emails
- `poplib` for receiving emails
- `tkinter` for the graphical user interface

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributions
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/sorooshaghaei/smtp-pop3-with-python/issues).
