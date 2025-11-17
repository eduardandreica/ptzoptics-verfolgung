import requests

class PtzCommands:
    def __init__(self, camera_ip):
        self.camera_ip = camera_ip

    def rechts(self, panspeed):
        print("rechts")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&right&{panspeed}&1')

    def links(self, panspeed):
        print("links")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&left&{panspeed}&1')

    def oben(self, panspeed):
        print("oben")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&up&{panspeed}&1')

    def unten(self, panspeed):
        print("unten")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&down&{panspeed}&1')

    def rechtsoben(self, panspeed):
        print("rechtsoben")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&rightup&{panspeed}&1')

    def linksoben(self, panspeed):
        print("linksoben")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&leftup&{panspeed}&1')

    def rechtsunten(self, panspeed):
        print("rechtsunten")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&rightdown&{panspeed}&1')

    def linksunten(self, panspeed):
        print("linksunten")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&leftdown&{panspeed}&1')

    def stop(self):
        print("stop")
        requests.get(f'http://admin:admin@{self.camera_ip}/cgi-bin/ptzctrl.cgi?ptzcmd&ptzstop&1&1')