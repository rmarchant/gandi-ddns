import gandi_ddns as script
import socket

def test_get_ip():
    assert script.get_ip() == socket.gethostbyname(socket.gethostname())