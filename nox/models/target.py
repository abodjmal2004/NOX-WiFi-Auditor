class Target:
    def __init__(self, bssid, channel, power, encryption, essid, clients=0):
        self.bssid = bssid
        self.channel = channel
        self.power = power
        self.encryption = encryption
        self.essid = essid if essid and essid.strip() else "<Hidden>"
        self.clients = clients

    def __str__(self):
        return f"{self.essid} ({self.bssid}) - Ch: {self.channel}, Pwr: {self.power}, Enc: {self.encryption}, Clients: {self.clients}"
