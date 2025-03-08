#include "KernelCrashDetector.h"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

bool KernelCrashDetector::detect() {
    // Check kernel.log file
    const std::string logFilePath = "kernel.log";
    std::ifstream logFile(logFilePath);
    if (!logFile.is_open()) {
        std::cerr << "Unable to open kernel log file: " << logFilePath << std::endl;
        return false;
    }

    std::string line;
    while (std::getline(logFile, line)) {
        if (line.find("Kernel Panic") != std::string::npos ||
            line.find("calltrace") != std::string::npos ||
            line.find("Out of memory") != std::string::npos) {
            std::cout << "Detected kernel crash in log: " << line << std::endl;
            logCrashInfo(line);
            logCrashInfoToPersistentMemory(line);
            return true;
        }
    }
    logFile.close();

    // Check dmesg output
    std::vector<std::string> dmesgOutput = getDmesgOutput();
    for (const auto& dmesgLine : dmesgOutput) {
        if (dmesgLine.find("Kernel Panic") != std::string::npos ||
            dmesgLine.find("calltrace") != std::string::npos ||
            dmesgLine.find("Out of memory") != std::string::npos) {
            std::cout << "Detected kernel crash in dmesg: " << dmesgLine << std::endl;
            logCrashInfo(dmesgLine);
            logCrashInfoToPersistentMemory(dmesgLine);
            return true;
        }
    }

    std::cout << "No kernel crash detected." << std::endl;
    return false;
}

std::vector<std::string> KernelCrashDetector::getDmesgOutput() {
    std::vector<std::string> output;
    FILE* pipe = popen("dmesg", "r");
    if (!pipe) {
        std::cerr << "Failed to run dmesg command" << std::endl;
        return output;
    }

    char buffer[128];
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr) {
            output.emplace_back(buffer);
        }
    }
    pclose(pipe);
    return output;
}

// 新增方法：记录崩溃信息到文件
void KernelCrashDetector::logCrashInfo(const std::string& crashInfo) {
    const std::string logFilePath = "kernel_crash_log.txt";
    std::ofstream logFile(logFilePath, std::ios::app);
    if (logFile.is_open()) {
        logFile << crashInfo << std::endl;
        logFile.close();
    } else {
        std::cerr << "Unable to open crash log file: " << logFilePath << std::endl;
    }
}

// 新增方法：记录崩溃信息到持久化内存
void KernelCrashDetector::logCrashInfoToPersistentMemory(const std::string& crashInfo) {
    const std::string memFilePath = "kernel_crash_mem.log";
    int fd = open(memFilePath.c_str(), O_RDWR | O_CREAT, (mode_t)0600);
    if (fd == -1) {
        std::cerr << "Error opening file for memory mapping" << std::endl;
        return;
    }

    // Stretch the file size to the size of the (mmapped) array of one int
    if (lseek(fd, crashInfo.size() - 1, SEEK_SET) == -1) {
        close(fd);
        std::cerr << "Error calling lseek()" << std::endl;
        return;
    }

    if (write(fd, "", 1) == -1) {
        close(fd);
        std::cerr << "Error writing last byte of the file" << std::endl;
        return;
    }

    // Now the file is ready to be mmapped.
    char* map = (char*)mmap(0, crashInfo.size(), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) {
        close(fd);
        std::cerr << "Error mmapping the file" << std::endl;
        return;
    }

    // Copy the crash info to the mapped memory
    memcpy(map, crashInfo.c_str(), crashInfo.size());

    // Write it now to disk
    if (msync(map, crashInfo.size(), MS_SYNC) == -1) {
        close(fd);
        std::cerr << "Could not sync the file to disk" << std::endl;
    }

    // Don't forget to free the mmapped memory
    if (munmap(map, crashInfo.size()) == -1) {
        close(fd);
        std::cerr << "Error un-mmapping the file" << std::endl;
    }

    // Un-mmaping doesn't close the file, so we still need to do that.
    close(fd);
}