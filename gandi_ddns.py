import configparser as configparser
import sys
import os
import requests
import json
import ipaddress
from datetime import datetime
import time

config_file = "config.txt"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_RETRIES = 3
DEFAULT_IPIFY_API = "https://api.ipify.org"


class GandiDdnsError(Exception):
    pass


def get_ip_inner(ipify_api):
    # Get external IP
    try:
        # Could be any service that just gives us a simple raw ASCII IP address (not HTML etc)
        r = requests.get(ipify_api, timeout=3)
    except requests.exceptions.RequestException:
        raise GandiDdnsError('Failed to retrieve external IP.')
    if r.status_code != 200:
        raise GandiDdnsError(
            'Failed to retrieve external IP.'
            ' Server responded with status_code: %d' % r.status_code)

    ip = r.text.rstrip()  # strip \n and any trailing whitespace

    if not(ipaddress.IPv4Address(ip)):  # check if valid IPv4 address
        raise GandiDdnsError('Got invalid IP: ' + ip)

    return ip


def get_ip(ipify_api, retries):
    # Get external IP with retries

    # Start at 5 seconds, double on every retry.
    retry_delay_time = 5
    for attempt in range(retries):
        try:
            return get_ip_inner(ipify_api)
        except GandiDdnsError as e:
            print('Getting external IP failed: %s' % e)
            print('Waiting for %d seconds before trying again' % retry_delay_time)
            time.sleep(retry_delay_time)
            # Double retry time, cap at 60s.
            retry_delay_time = min(60, 2 * retry_delay_time)
        print('Exhausted retry attempts')
        sys.exit(2)


def read_config(config_path):
    # Read configuration file
    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    return cfg


def get_record(url, headers):
    # Get existing record
    r = requests.get(url, headers=headers)

    return r


def update_record(url, headers, payload):
    # Add record
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code != 201:
        print(('Record update failed with status code: %d' % r.status_code))
        print((r.text))
        sys.exit(2)
        print('Zone record updated.')

    return r


def main():
    path = config_file
    if len(sys.argv) > 1:
        path = sys.argv[1]
    if not path.startswith('/'):
        path = os.path.join(SCRIPT_DIR, path)
    config = read_config(path)
    if not config:
        sys.exit("Please fill in the 'config.txt' file.")

    for section in config.sections():
        print('%s - section %s' % (str(datetime.now()), section))

        # Retrieve API key
        apikey = config.get(section, 'apikey')

        # Set headers
        headers = {'Content-Type': 'application/json', 'X-Api-Key': '%s' % apikey}

        # Set URL
        url = '%sdomains/%s/records/%s/A' % (config.get(section, 'gandi_api'),
                                             config.get(section, 'domain'), config.get(section, 'a_name'))
        print(url)
        # Discover External IP
        ipify_api = config.get(section, 'ipify_api', fallback=DEFAULT_IPIFY_API)
        retries = int(config.get(section, 'retries', fallback=DEFAULT_RETRIES))
        external_ip = get_ip(ipify_api, retries)
        print(('External IP is: %s' % external_ip))

        # Prepare record
        payload = {'rrset_ttl': config.get(section, 'ttl'), 'rrset_values': [external_ip]}

        # Check current record
        record = get_record(url, headers)

        if record.status_code == 200:
            print(('Current record value is: %s' % json.loads(record.text)['rrset_values'][0]))
            if(json.loads(record.text)['rrset_values'][0] == external_ip):
                print('No change in IP address. Goodbye.')
                continue
        else:
            print('No existing record. Adding...')

        update_record(url, headers, payload)


if __name__ == "__main__":
    main()
