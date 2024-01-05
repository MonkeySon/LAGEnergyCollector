import os
import traceback

MAILIFIER_TAG = 'EnergyCollector'

def mailify(subject, body):
    MAIL_SUBJECT = f'[{MAILIFIER_TAG}] {subject}'
    MAIL_BODY = body.replace("\\", "\\\\").replace("\"", "\\\"")
    CMD = f'mailifier_notify -s "{MAIL_SUBJECT}" -b "{MAIL_BODY}" > /dev/null'
    os.system(CMD)

def mailify_exception(subject):
    body = traceback.format_exc()
    mailify(subject, body)
