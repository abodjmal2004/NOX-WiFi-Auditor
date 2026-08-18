import subprocess
import re
import shutil
from ..core.ui import print_status, print_success, print_error

class InterfaceManager:
    def __init__(self):
        self.current_interface = None
        self.is_monitor = False

    def get_interfaces(self):
        try:
            result = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
            return re.findall(r'Interface (\w+)', result.stdout)
        except Exception:
            return []

    def enable_monitor_mode(self, iface):
        print_status(f"Enabling Monitor Mode on {iface}...")
        try:
            # Kill conflicting processes
            subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True)
            
            # Start monitor mode
            subprocess.run(['airmon-ng', 'start', iface], capture_output=True)
            
            # Find the new interface name
            interfaces = self.get_interfaces()
            for ni in interfaces:
                if ni.startswith(iface):
                    self.current_interface = ni
                    self.is_monitor = True
                    print_success(f"Monitor Mode enabled: {ni}")
                    return ni
            return None
        except Exception as e:
            print_error(f"Failed to enable monitor mode: {e}")
            return None

    def disable_monitor_mode(self):
        if self.current_interface and self.is_monitor:
            print_status(f"Disabling Monitor Mode on {self.current_interface}...")
            subprocess.run(['airmon-ng', 'stop', self.current_interface], capture_output=True)
            self.is_monitor = False
            self.current_interface = None
