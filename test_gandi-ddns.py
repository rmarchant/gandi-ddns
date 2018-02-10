import gandi-ddns as script

def test_get_ip():
    assert script.get_ip() == 'test-toto'