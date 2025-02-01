import psutil
    
def get_root_disk_usage():
    disk = psutil.disk_usage('/')
    total = disk.total / (1024 ** 3)  # Общий объём диска (ГБ)
    used = disk.used / (1024 ** 3)    # Использовано (ГБ)
    free = disk.free / (1024 ** 3)    # Свободно (ГБ)
    percent = disk.percent            # Заполненность в %

    return total, used, free, percent