// MemoryUsageCollector.cpp
#include "MemoryUsageCollector.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <sys/sysinfo.h>

void MemoryUsageCollector::collect(MemoryUsage& usage) {
    // 使用 sysinfo 获取内存使用情况
    struct sysinfo sys_info;
    if (sysinfo(&sys_info) != 0) {
        std::cerr << "Failed to get system info." << std::endl;
        return;
    }

    usage.totalMemory = sys_info.totalram;
    usage.freeMemory = sys_info.freeram;
    usage.usedMemory = usage.totalMemory - usage.freeMemory;

    std::cout << "Collected memory usage." << std::endl;

    // 检测内存异常
    if (usage.usedMemory > 0.8 * usage.totalMemory) {
        std::cout << "Memory usage is above 80%. Collecting system information and logs." << std::endl;
        collectSystemLogs();
        collectProcessStatus();
    }
}

void MemoryUsageCollector::collectSystemLogs() {
    // 使用系统命令获取系统日志
    std::string command = "journalctl -xe";
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        std::cerr << "Failed to run journalctl command." << std::endl;
        return;
    }

    std::string logOutput;
    char buffer[128];
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr) {
            logOutput += buffer;
        }
    }
    pclose(pipe);

    // 将系统日志保存到文件
    std::ofstream logFile("system_logs.log");
    if (logFile.is_open()) {
        logFile << logOutput;
        logFile.close();
        std::cout << "Collected system logs." << std::endl;
    } else {
        std::cerr << "Unable to open system logs file for writing." << std::endl;
    }
}

void MemoryUsageCollector::collectProcessStatus() {
    // 使用系统命令获取进程状态
    std::string command = "ps aux";
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        std::cerr << "Failed to run ps command." << std::endl;
        return;
    }

    std::string processOutput;
    char buffer[128];
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr) {
            processOutput += buffer;
        }
    }
    pclose(pipe);

    // 将进程状态保存到文件
    std::ofstream processFile("process_status.log");
    if (processFile.is_open()) {
        processFile << processOutput;
        processFile.close();
        std::cout << "Collected process status." << std::endl;
    } else {
        std::cerr << "Unable to open process status file for writing." << std::endl;
    }
}