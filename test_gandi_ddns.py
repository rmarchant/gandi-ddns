import gandi_ddns as script
import requests


def test_get_ip():
    assert script.get_ip("https://api.ipify.org", 3) == requests.get("http://ipecho.net/plain?").text
