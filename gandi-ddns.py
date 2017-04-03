import ConfigParser as configparser
import sys
import os
import requests
import json

config_file = "config.txt"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_ip():
        #Get external IP
        try:
          # Could be any service that just gives us a simple raw ASCII IP address (not HTML etc)
          r = requests.get("http://ipv4.myexternalip.com/raw", timeout=3)
        except Exception:
          print('Unable to retrieve external IP address.')
          sys.exit(2)
	if r.status_code != 200:
          print('Failed to retrieve external IP. Server responded with status_code: %d' % result.status_code)
          sys.exit(2)

        return r.text

def read_config(config_path):
        #Read configuration file
        cfg = configparser.ConfigParser()
        cfg.read(config_path)

        return cfg

def get_record(url, headers):
        #Get existing record
        r = requests.get(url, headers=headers)

        return r

def add_record(url, headers, payload):
        #Add record
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 201:
          print('Record update failed with status code: %d' % r.status_code)
          print(r.text)
          sys.exit(2)
        print r.text

        return r


def del_record(url, headers):
        #Delete record
        r = requests.delete(url, headers=headers)
        if r.status_code != 204:
          print('Record delete failed with status code: %d' % r.status_code)
          print(r.text)
          sys.exit(2)
        print('Record delete succeeded')

        return r


def main():
  global api, zone_uuid
  path = config_file
  if not path.startswith('/'):
    path = os.path.join(SCRIPT_DIR, path)
  config = read_config(path)
  if not config:
    sys.exit("please fill in the 'config.txt' file")

  for section in config.sections():
  
    #Retrieve API key
    apikey = config.get(section, "apikey")

    #Set headers
    headers = { 'Content-Type': 'application/json', 'X-Api-Key': '%s' % config.get(section, "apikey")}

    #Set URL
    url = '%sdomains/%s/records/%s/A' % (config.get(section, "api"), config.get(section, "domain"), config.get(section, "a_name"))
    print(url)
    #Discover External IP
    external_ip = get_ip()[0:-1]
    print("external IP is: %s" % external_ip)

    #Prepare record
    payload = {'rrset_ttl': 900, 'rrset_values': [external_ip]}

    #Check if record already exists. If not, add record. If it does, delete then add record.
    record = get_record(url, headers)

    if record.status_code == 404:
      add_record(url, headers, payload)
    elif record.status_code == 200:
      print("current record is: %s" % json.loads(record.text)['rrset_values'][0])
      if(json.loads(record.text)['rrset_values'][0] == external_ip):
        print("no change in IP address")
        sys.exit(2)
      del_record(url, headers)
      add_record(url, headers, payload)

if __name__ == "__main__":
  main()
