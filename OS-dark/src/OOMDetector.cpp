// OOMDetector.cpp
#include "OOMDetector.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <sys/sysinfo.h>

bool OOMDetector::detect() {
    // 模拟检测OOM
    // 这里可以添加实际的检测逻辑，例如检查系统日志中的特定条目
    // 为了示例，我们假设OOM被检测到
    std::cout << "Detected OOM." << std::endl;
    return true;
}

void OOMDetector::collectLogs() {
    if (detect()) {
        collectMemoryUsage();
        collectSystemLogs();
        collectProcessStatus();
    }
}

void OOMDetector::collectMemoryUsage() {
    // 使用 sysinfo 获取内存使用情况
    struct sysinfo sys_info;
    if (sysinfo(&sys_info) != 0) {
        std::cerr << "Failed to get system info." << std::endl;
        return;
    }

    MemoryUsage usage;
    usage.totalMemory = sys_info.totalram;
    usage.freeMemory = sys_info.freeram;
    usage.usedMemory = usage.totalMemory - usage.freeMemory;

    std::cout << "Collected memory usage." << std::endl;

    // 将内存使用情况保存到文件
    std::ofstream memoryFile("memory_usage.log");
    if (memoryFile.is_open()) {
        memoryFile << "Total Memory: " << usage.totalMemory / (1024 * 1024 * 1024) << " GB" << std::endl;
        memoryFile << "Free Memory: " << usage.freeMemory / (1024 * 1024 * 1024) << " GB" << std::endl;
        memoryFile << "Used Memory: " << usage.usedMemory / (1024 * 1024 * 1024) << " GB" << std::endl;
        memoryFile.close();
        std::cout << "Saved memory usage to file." << std::endl;
    } else {
        std::cerr << "Unable to open memory usage file for writing." << std::endl;
    }
}

void OOMDetector::collectSystemLogs() {
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

void OOMDetector::collectProcessStatus() {
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