import configparser as configparser
import sys
import os
import requests
import json
import ipaddress
from datetime import datetime

config_file = "config.txt"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_ip():
        #Get external IP
        try:
          # Could be any service that just gives us a simple raw ASCII IP address (not HTML etc)
          r = requests.get('https://api.ipify.org', timeout=3)
        except Exception:
          print('Failed to retrieve external IP.')
          sys.exit(2)
        if r.status_code != 200:
          print(('Failed to retrieve external IP. Server responded with status_code: %d' % r.status_code))
          sys.exit(2)

        ip = r.text.rstrip() # strip \n and any trailing whitespace

        if not(ipaddress.IPv4Address(ip)): # check if valid IPv4 address
          sys.exit(2)

        return ip

def read_config(config_path):
        #Read configuration file
        cfg = configparser.ConfigParser()
        cfg.read(config_path)

        return cfg

def get_record(url, headers):
        #Get existing record
        r = requests.get(url, headers=headers)

        return r

def update_record(url, headers, payload):
        #Add record
        r = requests.put(url, headers=headers, json=payload)
        if r.status_code != 201:
          print(('Record update failed with status code: %d' % r.status_code))
          print((r.text))
          sys.exit(2)
        print ('Zone record updated.')

        return r


def main():
  path = config_file
  if not path.startswith('/'):
    path = os.path.join(SCRIPT_DIR, path)
  config = read_config(path)
  if not config:
    sys.exit("Please fill in the 'config.txt' file.")

  for section in config.sections():
    print('%s - section %s' % (str(datetime.now()), section))

    #Retrieve API key
    apikey = config.get(section, 'apikey')

    #Set headers
    headers = { 'Content-Type': 'application/json', 'X-Api-Key': '%s' % config.get(section, 'apikey')}

    #Set URL
    url = '%sdomains/%s/records/%s/A' % (config.get(section, 'api'), config.get(section, 'domain'), config.get(section, 'a_name'))
    print(url)
    #Discover External IP
    external_ip = get_ip()
    print(('External IP is: %s' % external_ip))

    #Prepare record
    payload = {'rrset_ttl': config.get(section, 'ttl'), 'rrset_values': [external_ip]}

    #Check current record
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