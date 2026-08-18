import os
from .colors import Colors

LOGO = f"""{Colors.CYAN}{Colors.BOLD}
███╗   ██╗ ██████╗ ██╗  ██╗    
████╗  ██║██╔═══██╗╚██╗██╔╝    
██╔██╗ ██║██║   ██║ ╚███╔╝     
██║╚██╗██║██║   ██║ ██╔██╗     
██║ ╚████║╚██████╔╝██╔╝ ██╗    
╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝    
{Colors.END}{Colors.WHITE}
    [ NOX WiFi Auditor - v1.0 ]
    [ Automated Pentesting Framework ]
    [ Developer: Abod jamal ]
    [ Telegram: https://t.me/G0C_C ]
{Colors.END}
"""

def clear_screen():
    os.system('clear')
    print(LOGO)

def print_status(message):
    print(f"{Colors.BLUE}[*] {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}[+] {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}[!] {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}[?] {message}{Colors.END}")
