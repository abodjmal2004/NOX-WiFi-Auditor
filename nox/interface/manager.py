import subprocess
import re
import shutil
from ..core.ui import print_status, print_success, print_error

class InterfaceManager:
    def __init__(self):
        self.interfaces = {} # {name: {'is_monitor': bool, 'original_name': str}}

    def get_interfaces(self):
        try:
            result = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
            return re.findall(r'Interface (\w+)', result.stdout)
        except Exception:
            return []

    def enable_monitor_mode(self, iface):
        if iface in self.interfaces and self.interfaces[iface]['is_monitor']:
            return iface

        print_status(f"Enabling Monitor Mode on {iface}...")
        try:
            subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True)
            subprocess.run(['airmon-ng', 'start', iface], capture_output=True)
            
            new_ifaces = self.get_interfaces()
            for ni in new_ifaces:
                if ni.startswith(iface):
                    self.interfaces[ni] = {'is_monitor': True, 'original_name': iface}
                    print_success(f"Monitor Mode enabled: {ni}")
                    return ni
            return None
        except Exception as e:
            print_error(f"Failed to enable monitor mode: {e}")
            return None

    def disable_monitor_mode(self, iface):
        if iface in self.interfaces:
            print_status(f"Disabling Monitor Mode on {iface}...")
            subprocess.run(['airmon-ng', 'stop', iface], capture_output=True)
            del self.interfaces[iface]
            
    def disable_all(self):
        for iface in list(self.interfaces.keys()):
            self.disable_monitor_mode(iface)
