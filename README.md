Simple Python script to update DNS A record of your domain dynamically using gandi.net LiveDNS API:

http://doc.livedns.gandi.net/

The config-template.txt file should be renamed to config.txt, and modified with your gandi.net API key, domain name, and A-record (@, dev, home, pi, etc).

Every time the script runs, it will query an external service to retrieve the external IP of the machine, compare it to the current record (if any) in the zone at gandi.net, and then add a new record (if none currently exists), or delete then add a new record (if a record already exists).

Requirements:
  - Python 2.7
  - ipaddress module (pip install ipaddress)
