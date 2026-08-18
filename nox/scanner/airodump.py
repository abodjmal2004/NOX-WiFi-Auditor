import subprocess
import os
import time
import csv
from ..core.ui import clear_screen, Colors
from ..models.target import Target
from ..core.config import Config

class AirodumpScanner:
    def __init__(self, interface):
        self.interface = interface
        self.targets = []

    def scan(self):
        csv_prefix = os.path.join(Config.TEMP_DIR, "nox_scan")
        # Cleanup old scan files
        for f in os.listdir(Config.TEMP_DIR):
            if f.startswith("nox_scan"):
                os.remove(os.path.join(Config.TEMP_DIR, f))

        process = subprocess.Popen([
            'airodump-ng', self.interface,
            '--write', csv_prefix,
            '--output-format', 'csv',
            '--write-interval', '1'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            while True:
                time.sleep(2)
                self.parse_csv(csv_prefix + "-01.csv")
                self.display_targets()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()

    def parse_csv(self, csv_path):
        if not os.path.exists(csv_path):
            return

        new_targets = []
        stations = {}
        try:
            with open(csv_path, 'r') as f:
                content = f.read()
                parts = content.split("Station MAC")
                
                if len(parts) > 1:
                    for line in parts[1].strip().split("\n"):
                        cols = line.split(",")
                        if len(cols) > 5:
                            ap_bssid = cols[5].strip()
                            stations[ap_bssid] = stations.get(ap_bssid, 0) + 1

                network_lines = parts[0].strip().split("\n")
                reader = csv.reader(network_lines)
                start = False
                for row in reader:
                    if not row or len(row) < 14: continue
                    if "BSSID" in row[0]:
                        start = True
                        continue
                    if start:
                        bssid = row[0].strip()
                        channel = row[3].strip()
                        power = row[8].strip()
                        enc = row[5].strip()
                        essid = row[13].strip()
                        clients = stations.get(bssid, 0)
                        new_targets.append(Target(bssid, channel, power, enc, essid, clients))
            self.targets = new_targets
        except Exception:
            pass

    def display_targets(self):
        clear_screen()
        print(f"{Colors.BLUE}{'ID':<4} {'BSSID':<20} {'CH':<4} {'PWR':<4} {'ENC':<8} {'CLIENTS':<8} {'ESSID'}{Colors.END}")
        print("-" * 80)
        for idx, t in enumerate(self.targets):
            print(f"{idx+1:<4} {t.bssid:<20} {t.channel:<4} {t.power:<4} {t.encryption:<8} {t.clients:<8} {t.essid}")
