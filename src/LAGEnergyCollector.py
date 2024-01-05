import json
import sys
import traceback

import MailifierUtil
import ImapConnector
import InfluxDBConnector

CONFIG_FILE_NAME = 'config.json'

if len(sys.argv) == 2:
    CONFIG_FILE_NAME = sys.argv[1]
elif len(sys.argv) > 2:
    print(f'Usage: {sys.argv[0]} [ CONFIG_FILE ]')
    exit(1)

print(f'Using config file: {CONFIG_FILE_NAME}')

try:
    with open(CONFIG_FILE_NAME, encoding='UTF-8') as config_file:
        cfg = json.load(config_file)
except Exception as e:
    print('Exception while opening config file:', e)
    print(traceback.format_exc())

imapCfg     = cfg['imap']
influxDBCfg = cfg['influxDB']

data_points = None

try:
    print('Parsing mails ...')
    data_points = ImapConnector.parseMails(imapCfg)
except Exception as e:
    print('Exception while parsing mails:', e)
    print(traceback.format_exc())
    MailifierUtil.mailify_exception('Exception parsing mails')

if data_points == None:
    print('ERROR while parsing mails!')
    exit()

try:
    if influxDBCfg['enabled'] == True:
        print("Writing to InfluxDB ...")
        if len(data_points) > 0:
            InfluxDBConnector.write_points(influxDBCfg, data_points)
        else:
            print('WARNING: No energy data points collected!')
    else:
        print("Skipping InfluxDB ...")
except Exception as e:
    print('Exception while writing points to InfluxDB:', e)
    print(traceback.format_exc())
    MailifierUtil.mailify_exception('Exception InfluxDB writing')

print('Done!')