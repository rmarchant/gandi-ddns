import gandi_ddns as script
import requests

def test_get_ip():
    assert script.get_ip() == requests.get("http://ipecho.net/plain?").text