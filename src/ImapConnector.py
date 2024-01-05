import imaplib
import email
from lxml import etree
from datetime import datetime

import MailifierUtil
from EnergyPoint import EnergyPoint

IMAP: imaplib.IMAP4_SSL
IMAP = None

def _logout():
    global IMAP
    if IMAP is not None:
        IMAP.logout()
        IMAP = None

def parseMails(config):
    global IMAP

    # Establish IMAP connection
    if config['ssl'] == True:
        IMAP = imaplib.IMAP4_SSL(config['server'], config['port'])
    else:
        IMAP = imaplib.IMAP4(config['server'], config['port'])

    # Login to mailbox
    resp_code, _ = IMAP.login(config['username'], config['password'])
    if resp_code != 'OK':
        print('ERROR: Could not log in to mail server! Response:', resp_code)
        MailifierUtil.mailify('IMAP login error', f'Could not log in to mail server! Response: {resp_code}')
        return None
    
    # Selecting INBOX
    resp_code, _ = IMAP.select('INBOX')
    if resp_code != 'OK':
        print('ERROR: Could not open inbox! Response:', resp_code)
        MailifierUtil.mailify('IMAP inbox error', f'Could not open inbox! Response: {resp_code}')
        _logout()
        return None
    
    # Getting unread messages
    resp_code, msg_nums = IMAP.search(None, 'UNSEEN')
    if resp_code != 'OK':
        print('ERROR: Could not retrieve unseen messages! Response:', resp_code)
        MailifierUtil.mailify('IMAP search error', f'Could not retrieve unseen messages! Response: {resp_code}')
        _logout()
        return None
    msg_nums = msg_nums[0].split()

    data_points = []

    # Loop through unread messages
    for msg_num in msg_nums:
        # Fetch message (which marks it as read)        
        resp_code, data = IMAP.fetch(msg_num, '(RFC822)')
        if resp_code != 'OK':
            print(f'ERROR: Could not retrieve unseen message {msg_num.decode()}! Response:', resp_code)
            MailifierUtil.mailify('IMAP fetch error', f'Could not retrieve unseen message {msg_num.decode()}! Response: {resp_code}')
            _logout()
            return data_points

        # Get body from raw data
        body = data[0][1].decode()

        # Get mail from raw body
        mail = email.message_from_string(body)

        # Skip mails without attachments
        if mail.get_content_maintype() != 'multipart':
            continue

        # Decode subject
        subject_data = email.header.decode_header(mail['Subject'])
        subject_text = subject_data[0][0]
        subject_encoding = subject_data[0][1]
        subject = subject_text.decode(subject_encoding)

        # Filter by subject
        if 'Tagesbericht' not in subject:
            continue

        # Loop through parts of mail
        for part in mail.walk():
            # multipart are just containers, so we skip them
            if part.get_content_maintype() == 'multipart':
                continue

            # is this part an attachment ?
            if part.get('Content-Disposition') is None:
                continue

            # Filter for XML file type
            filename = part.get_filename()
            if not filename.endswith('.xml'):
                continue

            # Retrieve XML payload in Bytes (decode=True)
            xml_payload = part.get_payload(decode=True)

            # Load XML
            xml_root = etree.fromstring(xml_payload)
            
            # Parse Consumption Points from XML
            consumption_positions = xml_root.xpath(".//*[local-name() = 'ConsumptionPosition']")

            for cp in consumption_positions:
                ep = EnergyPoint()
                for elem in cp:
                    if 'DateTimeTo' in elem.tag:
                        # Get timestamp
                        ep.set_timestamp(datetime.strptime(elem.text, '%Y-%m-%dT%H:%M:%S%z'))
                    elif 'BillingQuantity' in elem.tag:
                        # Get kWh amount
                        ep.set_energy(float(elem.text))
                    else:
                        # Skip other tags
                        continue
                data_points.append(ep)

            # Break if mail part was the correct attachment
            break

    _logout()
    return data_points