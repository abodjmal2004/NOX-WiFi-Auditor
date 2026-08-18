```text
███╗   ██╗ ██████╗ ██╗  ██╗    
████╗  ██║██╔═══██╗╚██╗██╔╝    
██╔██╗ ██║██║   ██║ ╚███╔╝     
██║╚██╗██║██║   ██║ ██╔██╗     
██║ ╚████║╚██████╔╝██╔╝ ██╗    
╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝    
```

# NOX WiFi Auditor

**NOX** is an advanced, automated wireless network security auditing and penetration testing framework written in Python. It combines the core intelligence and automation features of industry-standard tools like **Wifite**, **Airgeddon**, and **Bettercap** into a unified, stable, and easy-to-use interface.

---

## Features

- **Smart Interface Management**: Automatically detects wireless adapters, kills conflicting background processes (NetworkManager, wpa_supplicant), and enables Monitor Mode instantly.
- **Live Network Scanning**: Displays a structured real-time table of surrounding networks including:
  - `ID`, `BSSID`, `Channel`, `Signal Power (PWR)`, `Encryption Type (ENC)`, `Connected Clients`, and `ESSID`.
- **Multi-Vector Attack Suite**:
  - **WPA/WPA2 Handshake Capture**: Automated target capture with continuous `Deauthentication` packet injection.
  - **PMKID Attack**: Clientless attack vector support.
  - **WPS Pixie-Dust / Reaver**: Vulnerability auditing for WPS-enabled routers.
- **Automated Cracking Integration**: Seamlessly saves captured handshakes (`.cap`) and integrates with dictionary wordlists (e.g., `rockyou.txt`) for immediate offline cracking using `aircrack-ng`.
- **Professional Terminal UI**: Styled with custom ANSI shadows and color-coded logging.

---

## Prerequisites & Dependencies

Ensure you are running a compatible Linux distribution (such as **Kali Linux**, **Parrot OS**, or **Arch Linux**) with a wireless adapter capable of monitor mode and packet injection.

```bash
sudo apt update
sudo apt install aircrack-ng wireless-tools hcxdumptool reaver python3
```

---

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/YOUR_USERNAME/NOX-WiFi-Auditor.git
cd NOX-WiFi-Auditor
```

---

## Usage

Run the script with root privileges (`sudo` is required for raw socket access and wireless card manipulation):

```bash
sudo python3 nox.py
```

---

## Legal Disclaimer

> This tool is developed strictly for educational purposes, authorized security auditing, and network hardening. Unauthorized network penetration or accessing wireless networks without explicit prior permission from the system owner is illegal. The author assumes no liability for any misuse or damage caused by this program.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
