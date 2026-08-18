import sys
import os
from .core.ui import clear_screen, print_error, print_status, Colors
from .core.config import Config
from .interface.manager import InterfaceManager
from .scanner.airodump import AirodumpScanner
from .attacks.wpa import WPAAttack

class NoxApp:
    def __init__(self):
        Config.initialize()
        self.iface_manager = InterfaceManager()

    def check_root(self):
        if os.geteuid() != 0:
            print_error("This tool must be run as root (sudo).")
            sys.exit(1)

    def run(self):
        self.check_root()
        clear_screen()
        
        interfaces = self.iface_manager.get_interfaces()
        if not interfaces:
            print_error("No wireless interfaces found.")
            return

        print(f"{Colors.YELLOW}[?] Select Interface:{Colors.END}")
        for i, iface in enumerate(interfaces):
            print(f" {i+1}) {iface}")
        
        try:
            choice = int(input(f"\n{Colors.CYAN}NOX > {Colors.END}")) - 1
            selected = interfaces[choice]
        except (ValueError, IndexError, KeyboardInterrupt):
            print_error("Exiting.")
            return

        mon_iface = self.iface_manager.enable_monitor_mode(selected)
        if not mon_iface: return

        scanner = AirodumpScanner(mon_iface)
        try:
            scanner.scan()
        except KeyboardInterrupt:
            pass

        if not scanner.targets:
            print_error("No targets found.")
            return

        try:
            target_choice = int(input(f"\n{Colors.CYAN}Select Target ID: {Colors.END}")) - 1
            target = scanner.targets[target_choice]
        except (ValueError, IndexError, KeyboardInterrupt):
            print_error("Exiting.")
            return

        # Attack Menu
        clear_screen()
        print(f"{Colors.GREEN}Target: {target.essid} [{target.bssid}]{Colors.END}")
        print("\n1) WPA Handshake Attack")
        print("2) Exit")
        
        try:
            attack_choice = input(f"\n{Colors.CYAN}NOX > {Colors.END}")
            if attack_choice == '1':
                wpa = WPAAttack(mon_iface, target)
                cap = wpa.capture_handshake()
                if cap:
                    ans = input(f"{Colors.YELLOW}Crack now? (y/n): {Colors.END}")
                    if ans.lower() == 'y':
                        wpa.crack(cap)
        except KeyboardInterrupt:
            pass
        
        self.iface_manager.disable_monitor_mode()

if __name__ == "__main__":
    app = NoxApp()
    app.run()
