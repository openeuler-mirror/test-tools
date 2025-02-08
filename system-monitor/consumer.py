import time  
import random  
import os  
import socket  
import setproctitle  # 用于修改进程名  

def consume_cpu():  
    """模拟CPU消耗，进行浮点运算"""  
    print("模拟CPU消耗中...")  
    while True:  
        # 进行浮点运算  
        for _ in range(10**6):  
            _ = random.random() * random.random()  
        time.sleep(0.1)  # 避免过高CPU占用  

def consume_memory(mb_size):  
    """模拟内存消耗，分配指定大小的内存"""  
    print(f"模拟内存消耗中...分配 {mb_size} MB 内存")  
    data = []  
    chunk_size = 1024 * 1024  # 1 MB  
    for _ in range(mb_size):  
        try:  
            data.append(' ' * chunk_size)  # 分配1MB内存  
        except MemoryError:  
            print("内存分配失败，已达到系统限制")  
            break  
    while True:  
        time.sleep(1)  # 保持内存占用  

def consume_disk(mb_size, file_path="temp_file.txt"):  
    """模拟磁盘存储消耗，生成指定大小的文件"""  
    print(f"模拟磁盘存储消耗中...生成 {mb_size} MB 文件")  
    chunk_size = 1024 * 1024  # 1 MB  
    with open(file_path, "w") as f:  
        for _ in range(mb_size):  
            f.write(' ' * chunk_size)  
    print(f"文件已生成: {file_path}")  
    while True:  
        time.sleep(1)  # 保持文件占用  

def consume_network():  
    """模拟网络流量，不断发送和接收数据"""  
    print("模拟网络流量中...")  
    server_address = ('localhost', 12345)  
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    client_socket.connect(server_address)  
    while True:  
        message = 'A' * 1024  # 1 KB 数据  
        client_socket.sendall(message.encode())  
        data = client_socket.recv(1024)  
        time.sleep(0.1)  # 限制网络流量速度  

def cleanup(file_path="temp_file.txt"):  
    """清理生成的临时文件"""  
    if os.path.exists(file_path):  
        os.remove(file_path)  
        print(f"已清理临时文件: {file_path}")  

def main():  
    try:  
        # 修改进程名为 consumer  
        setproctitle.setproctitle("consumer")  

        # 选择资源消耗类型  
        print("选择要测试的资源消耗类型:")  
        print("1. CPU")  
        print("2. 内存")  
        print("3. 磁盘存储")  
        print("4. 网络")  
        choice = input("请输入数字 (1/2/3/4): ")  

        if choice == "1":  
            consume_cpu()  
        elif choice == "2":  
            mb_size = int(input("请输入要消耗的内存大小 (MB): "))  
            consume_memory(mb_size)  
        elif choice == "3":  
            mb_size = int(input("请输入要消耗的磁盘存储大小 (MB): "))  
            consume_disk(mb_size)  
        elif choice == "4":  
            consume_network()  
        else:  
            print("无效选择！")  
    except KeyboardInterrupt:  
        print("资源消耗测试已停止。")  
        cleanup()  

if __name__ == "__main__":  
    main()

