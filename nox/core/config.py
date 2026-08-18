import os

class Config:
    VERSION = "1.0.0"
    AUTHOR = "Manus AI & User"
    OUTPUT_DIR = "nox_captures"
    DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
    LOG_FILE = os.path.join(OUTPUT_DIR, "nox.log")
    TEMP_DIR = "/tmp/nox"
    
    # Tool settings
    AIRODUMP_SCAN_TIME = 0 # 0 means infinite until Ctrl+C
    DEAUTH_PACKETS = 10
    
    @staticmethod
    def initialize():
        if not os.path.exists(Config.OUTPUT_DIR):
            os.makedirs(Config.OUTPUT_DIR)
        if not os.path.exists(Config.TEMP_DIR):
            os.makedirs(Config.TEMP_DIR)
