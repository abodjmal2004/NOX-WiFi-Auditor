<p align="center">
  <img src="https://img.shields.io/badge/NOX-WiFi--Auditor-blue?style=for-the-badge&logo=wi-fi&logoColor=white" alt="NOX Logo">
</p>

<h1 align="center">
  ███╗   ██╗ ██████╗ ██╗  ██╗<br>
  ████╗  ██║██╔═══██╗╚██╗██╔╝<br>
  ██╔██╗ ██║██║   ██║ ╚███╔╝ <br>
  ██║╚██╗██║██║   ██║ ██╔██╗ <br>
  ██║ ╚████║╚██████╔╝██╔╝ ██╗<br>
  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝
</h1>

<p align="center">
  <strong>Advanced Modular Wireless Auditing Framework</strong><br>
  <i>Empowering Security Researchers with Automated Intelligence</i>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/abodjmal2004/NOX-WiFi-Auditor?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/stars/abodjmal2004/NOX-WiFi-Auditor?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/github/forks/abodjmal2004/NOX-WiFi-Auditor?style=flat-square" alt="Forks">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey.svg?style=flat-square&logo=linux&logoColor=white" alt="Platform">
</p>

---

## 📖 Overview

**NOX WiFi Auditor** is a professional-grade, modular wireless security framework designed for automated penetration testing. It bridges the gap between classic tools and modern automation, providing a stable, extensible, and high-performance environment for auditing WPA/WPA2/WPA3 networks.

Built with a **Modular Architecture** similar to industry standards, NOX allows for seamless integration of various attack vectors, intelligent interface management, and persistent data logging via SQLite.

---

## 🚀 Key Features

### 🛠 Core Capabilities
- 📡 **Smart Interface Management**: Automatic monitor mode activation, conflict resolution, and multi-interface support.
- 🔍 **Advanced Live Scanning**: Real-time discovery of APs and clients with signal strength tracking.
- 💾 **Persistent Database**: Full SQLite integration to store discovered targets, captured handshakes, and cracked credentials.
- 🕵️ **Hidden SSID Reveal**: Intelligent de-cloaking of hidden networks via active probe request capturing.

### ⚡ Attack Vectors
- 🤝 **WPA/WPA2 Handshake**: Automated capture with smart deauthentication loops.
- 🏗 **Evil Twin (Rogue AP)**: Advanced captive portal with automated DNS hijacking and IPTables routing.
- 🎯 **PMKID Attack**: Silent, clientless hash capturing for modern WPA auditing.
- 🔐 **WPA3 (SAE) Support**: Experimental support for the latest wireless security standards.
- ⌨️ **Instant Cracking**: Prioritized custom wordlists for rapid validation during assessments.

---

## 📂 Project Structure

```text
NOX-WiFi-Auditor/
├── nox/
│   ├── core/       # Configuration, Database, and UI logic
│   ├── interface/  # Wireless hardware management
│   ├── scanner/    # Network discovery and analysis
│   ├── attacks/    # Attack vector implementations (WPA, EvilTwin, etc.)
│   ├── models/     # Data objects and models
│   └── tools/      # External tool wrappers
├── nox-auditor.py  # Main entry point (Launcher)
├── test_wordlist.txt # Fast-track testing dictionary
└── README.md       # Professional Documentation
```

---

## 📥 Installation & Setup

### Requirements
- **OS**: Kali Linux, Parrot Security, or any Debian-based pentesting distro.
- **Hardware**: Wireless adapter supporting **Monitor Mode** and **Packet Injection**.

### Quick Install
```bash
# Clone the repository
git clone https://github.com/abodjmal2004/NOX-WiFi-Auditor.git

# Enter the directory
cd NOX-WiFi-Auditor

# Install dependencies
sudo apt update && sudo apt install aircrack-ng wireless-tools hcxdumptool reaver python3-flask -y
```

---

## 🎮 Usage

Launch the framework with root privileges to grant full hardware access:

```bash
sudo python3 nox-auditor.py
```

1. **Select Interface**: Choose your wireless adapter.
2. **Scan**: Monitor live targets and identify vulnerabilities.
3. **Attack**: Select a target ID and choose your preferred attack vector.
4. **Result**: Check `nox_captures/` or the SQLite database for results.

---

## 🗺 Roadmap

- [ ] Multi-interface simultaneous scanning and attacking.
- [ ] AI-driven attack vector selection based on signal quality.
- [ ] Exportable PDF security audit reports.
- [ ] Integration with Hashcat for GPU-accelerated cracking.

---

## ⚖️ Legal Disclaimer

> **WARNING**: This software is intended for **educational purposes** and **authorized security auditing** only. Unauthorized access to wireless networks is illegal. The developer is not responsible for any misuse of this tool. Use it ethically and legally.

---

## 👤 Developer & Support

<div align="center">
  <p><strong>Developed by Abod jamal</strong></p>
  <a href="https://t.me/G0C_C">
    <img src="https://img.shields.io/badge/Telegram-Join%20Channel-blue?style=for-the-badge&logo=telegram" alt="Telegram">
  </a>
</div>

<p align="center">
  <i>"Automating the art of wireless auditing."</i>
</p>
