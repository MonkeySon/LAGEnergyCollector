import imaplib
import json
import sys

IMAP: imaplib.IMAP4_SSL
IMAP = None

def _logout():
    global IMAP
    if IMAP is not None:
        IMAP.logout()
        IMAP = None

def resetSeenMails(config):
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
        return
    
    # Selecting INBOX
    resp_code, _ = IMAP.select('INBOX')
    if resp_code != 'OK':
        print('ERROR: Could not open inbox! Response:', resp_code)
        _logout()
        return
    
    # Getting unread messages
    resp_code, msg_nums = IMAP.search(None, 'SEEN')
    if resp_code != 'OK':
        print('ERROR: Could not retrieve seen messages! Response:', resp_code)
        _logout()
        return
    msg_nums = msg_nums[0].split()

    print('Number of seen messages:', len(msg_nums))

    # Loop through read messages
    for msg_num in msg_nums:
        resp_code, _ = IMAP.store(msg_num, '-FLAGS', '\Seen')
        if resp_code != 'OK':
            print(f'ERROR: Could not reset seen status for message {msg_num.decode()}! Response:', resp_code)
            _logout()
            return

    _logout()
    return

if __name__ == '__main__':

    CONFIG_FILE_NAME = '../src/config.json'

    if len(sys.argv) == 2:
        CONFIG_FILE_NAME = sys.argv[1]
    elif len(sys.argv) > 2:
        print(f'Usage: {sys.argv[0]} [ CONFIG_FILE ]')
        exit(1)

    print(f'Using config file: {CONFIG_FILE_NAME}')

    with open('config.json', encoding='UTF-8') as config_file:
            cfg = json.load(config_file)

    resetSeenMails(cfg['imap'])