import psutil  
import time  
import datetime  

def print_cpu_info():  
    print("=== CPU 信息 ===")  
    print(f"CPU 使用率: {psutil.cpu_percent(interval=1)}%")  
    print(f"CPU 逻辑核心数: {psutil.cpu_count(logical=True)}")  
    print(f"CPU 物理核心数: {psutil.cpu_count(logical=False)}")  
    print(f"CPU 时间: {psutil.cpu_times()}")  
    print(f"CPU 平均负载: {psutil.getloadavg()}")  
    print("=" * 30)  

def print_memory_info():  
    print("=== 内存信息 ===")  
    virtual_memory = psutil.virtual_memory()  
    print(f"总内存: {virtual_memory.total / (1024 ** 2):.2f} MB")  
    print(f"已用内存: {virtual_memory.used / (1024 ** 2):.2f} MB")  
    print(f"可用内存: {virtual_memory.available / (1024 ** 2):.2f} MB")  
    print(f"内存使用率: {virtual_memory.percent}%")  
    
    swap_memory = psutil.swap_memory()  
    print(f"交换内存总量: {swap_memory.total / (1024 ** 2):.2f} MB")  
    print(f"已用交换内存: {swap_memory.used / (1024 ** 2):.2f} MB")  
    print(f"交换内存使用率: {swap_memory.percent}%")  
    print("=" * 30)  

def print_disk_info():  
    print("=== 磁盘信息 ===")  
    disk_usage = psutil.disk_usage('/')  
    print(f"总磁盘容量: {disk_usage.total / (1024 ** 3):.2f} GB")  
    print(f"已用磁盘容量: {disk_usage.used / (1024 ** 3):.2f} GB")  
    print(f"可用磁盘容量: {disk_usage.free / (1024 ** 3):.2f} GB")  
    print(f"磁盘使用率: {disk_usage.percent}%")  
    
    disk_io = psutil.disk_io_counters()  
    print(f"读IO次数: {disk_io.read_count}, 写IO次数: {disk_io.write_count}")  
    print(f"读字节数: {disk_io.read_bytes}, 写字节数: {disk_io.write_bytes}")  
    print("=" * 30)  

def print_network_info():  
    print("=== 网络信息 ===")  
    net_io = psutil.net_io_counters()  
    print(f"发送字节数: {net_io.bytes_sent}")  
    print(f"接收字节数: {net_io.bytes_recv}")  
    
    net_if_addrs = psutil.net_if_addrs()  
    print("网络接口信息:")  
    for interface, addrs in net_if_addrs.items():  
        for addr in addrs:  
            print(f"  接口: {interface}, 地址: {addr.address}, 类型: {addr.family}")  
    print("=" * 30)  

def print_system_info():  
    print("=== 系统信息 ===")  
    boot_time = psutil.boot_time()  
    print(f"系统启动时间: {datetime.datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')}")  
    
    users = psutil.users()  
    print("当前用户:")  
    for user in users:  
        print(f"  用户: {user.name}, 终端: {user.terminal}, 主机: {user.host}, 开始时间: {datetime.datetime.fromtimestamp(user.started)}")  
    print("=" * 30)  

def main():  
    try:  
        while True:  
            print_cpu_info()  
            print_memory_info()  
            print_disk_info()  
            print_network_info()  
            print_system_info()  
            time.sleep(5)  # 每5秒刷新一次  
    except KeyboardInterrupt:  
        print("监控已停止。")  

if __name__ == "__main__":  
    main()

