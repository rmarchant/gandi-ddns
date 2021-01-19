Python script to update DNS A record of your domain dynamically using gandi.net LiveDNS API:

http://doc.livedns.gandi.net/

The script was developed for those behind a dynamic IP interface (e.g. home server/pi/nas).

The config-template.txt file should be renamed to config.txt, and modified with your gandi.net API key, domain name, and A-record (@, dev, home, pi, etc).

Every time the script runs, it will query an external service to retrieve the external IP of the machine, compare it to the current A record in the zone at gandi.net, and then update the record if the IP has changed.

Requirements: 

  pip install -r requirements.txt

You can then run the script as a cron job :

```
*/15 * * * * python /home/user/gandi_ddns.py
```

But to be nice to the API servers, you should choose a random offset for your job. For example to run at 2 minutes after the hour, and then every 15 minutes :

```
2-59/15 * * * * python /home/user/gandi-ddns.py
```

# macOS

```
cd gandi-ddns
ln -s $(pwd) /usr/local/gandi-ddns
sudo cp gandi.ddns.plist /Library/LaunchDaemons/
sudo launchctl /Library/LaunchDaemons/gandi.ddns.plist
```

# Docker

The docker container is published as [`rmarchant/gandi-ddns`](https://hub.docker.com/r/rmarchant/gandi-ddns). To run,
pass it an argument pointing to the config file. The config file must be mounted into the container's filesystem.

```
docker run -it --rm -v /path/to/config/file.txt:/config.txt rmarchant/gandi-ddns /config.txt
```

If you're on Kubernetes, you can create a
[CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) to run this periodically.
