import platform
import sys
import subprocess

def get_system_info():
    """
    Сбор информации об операционной системе
    используя только встроенные библиотеки
    """
    try:
        # Основная информация об ОС через platform
        os_name = platform.system()
        os_version = platform.version()
        os_release = platform.release()
        
        # Сервис-пак для Windows
        service_pack = get_service_pack()
        
        # Информация о памяти
        memory_info = get_memory_info()
        
        # Дополнительная информация
        architecture = platform.architecture()[0]
        machine = platform.machine()
        processor = platform.processor() or get_processor_info()
        
        # Сборка полной информации
        full_os_name = f"{os_name} {os_release} (Версия: {os_version})"
        
        return {
            "os_name": full_os_name,
            "os_version": os_version,
            "service_pack": service_pack,
            "total_memory_gb": memory_info['total'],
            "available_memory_gb": memory_info['available'],
            "architecture": architecture,
            "processor": processor,
            "machine": machine,
            "error": None
        }
        
    except Exception as e:
        return {
            "os_name": "Ошибка получения данных",
            "os_version": "Ошибка",
            "service_pack": "Ошибка",
            "total_memory_gb": 0,
            "available_memory_gb": 0,
            "architecture": "Ошибка",
            "processor": "Ошибка",
            "machine": "Ошибка",
            "error": f"Ошибка получения данных: {str(e)}"
        }

def get_service_pack():
    """Получение информации о сервис-паке"""
    try:
        if hasattr(platform, 'win32_ver'):
            win_info = platform.win32_ver()
            service_pack = win_info[3] if len(win_info) > 3 else "Не установлен"
            return service_pack
        return "Не применимо для данной ОС"
    except:
        return "Не удалось определить"

def get_memory_info():
    """Получение информации о памяти (кроссплатформенный способ)"""
    try:
        if platform.system() == "Windows":
            return get_windows_memory()
        elif platform.system() == "Linux":
            return get_linux_memory()
        elif platform.system() == "Darwin":  # macOS
            return get_macos_memory()
        else:
            return {"total": 0, "available": 0}
    except:
        return {"total": 0, "available": 0}

def get_windows_memory():
    """Получение информации о памяти в Windows"""
    try:
        import ctypes
        from ctypes import wintypes
        
        kernel32 = ctypes.windll.kernel32
        kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(wintypes.MEMORYSTATUSEX)]
        kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
        
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", wintypes.DWORD),
                ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        
        memory_status = MEMORYSTATUSEX()
        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        
        if kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status)):
            total_gb = round(memory_status.ullTotalPhys / (1024**3), 2)
            available_gb = round(memory_status.ullAvailPhys / (1024**3), 2)
            return {"total": total_gb, "available": available_gb}
    except:
        pass
    return {"total": 0, "available": 0}

def get_linux_memory():
    """Получение информации о памяти в Linux"""
    try:
        with open('/proc/meminfo', 'r') as meminfo:
            lines = meminfo.readlines()
            mem_dict = {}
            for line in lines:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().split(' ')[0]
                    mem_dict[key] = int(value) * 1024  # Convert kB to bytes
            
            total_gb = round(mem_dict.get('MemTotal', 0) / (1024**3), 2)
            available_gb = round(mem_dict.get('MemAvailable', 0) / (1024**3), 2)
            return {"total": total_gb, "available": available_gb}
    except:
        pass
    return {"total": 0, "available": 0}

def get_macos_memory():
    """Получение информации о памяти в macOS"""
    try:
        result = subprocess.run(['sysctl', '-n', 'hw.memsize'], 
                              capture_output=True, text=True)
        total_bytes = int(result.stdout.strip())
        total_gb = round(total_bytes / (1024**3), 2)
        
        # Для доступной памяти используем vm_stat
        result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        page_size = 4096  # Standard page size
        
        free_pages = 0
        for line in lines:
            if 'free' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    free_pages = int(parts[1].strip().split('.')[0])
                    break
        
        available_gb = round((free_pages * page_size) / (1024**3), 2)
        return {"total": total_gb, "available": available_gb}
    except:
        pass
    return {"total": 0, "available": 0}

def get_processor_info():
    """Получение информации о процессоре"""
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            processor, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            winreg.CloseKey(key)
            return processor.strip()
        elif platform.system() == "Linux":
            with open('/proc/cpuinfo', 'r') as cpuinfo:
                for line in cpuinfo:
                    if 'model name' in line:
                        return line.split(':')[1].strip()
        elif platform.system() == "Darwin":
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
    except:
        pass
    return "Не удалось определить"
