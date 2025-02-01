import subprocess

import psutil


def _get_root_disk_usage():
    try:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            return parts[1], parts[2], parts[3], parts[4]  # total, used, available, percent
    except Exception as e:
        return "Ошибка", str(e), "", ""
    
def get_root_disk_usage():
    disk = psutil.disk_usage('/')
    free_disk_gb = disk.free / (1024 ** 3)  # Свободное место на диске в ГБ
    total_disk_gb = disk.total / (1024 ** 3)  # Общий объём диска
    disk_used = disk.used
    parts = []
    parts.append(total_disk_gb)
    parts.append(disk_used)
    parts.append(free_disk_gb)
    parts.append((free_disk_gb / total_disk_gb) * 100)
    return parts[0], parts[1], parts[2], parts[3]