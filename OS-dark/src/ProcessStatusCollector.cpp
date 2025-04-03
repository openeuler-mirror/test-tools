// ProcessStatusCollector.cpp
#include "ProcessStatusCollector.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <dirent.h>
#include <string>

void ProcessStatusCollector::collect(std::vector<ProcessStatus>& statuses) {
    // 实现进程信息收集逻辑
    DIR* dir = opendir("/proc");
    if (dir == nullptr) {
        std::cerr << "Error opening /proc directory" << std::endl;
        return;
    }

    struct dirent* entry;
    while ((entry = readdir(dir)) != nullptr) {
        if (entry->d_type == DT_DIR) {
            try {
                int pid = std::stoi(entry->d_name);
                std::ifstream statusFile("/proc/" + std::to_string(pid) + "/status");
                if (statusFile.is_open()) {
                    ProcessStatus status;
                    status.pid = pid;
                    std::string line;
                    while (std::getline(statusFile, line)) {
                        std::istringstream iss(line);
                        std::string key;
                        if (std::getline(iss, key, ':')) {
                            std::string value;
                            std::getline(iss, value);
                            value.erase(0, value.find_first_not_of(' ')); // Remove leading spaces
                            if (key == "Name") {
                                status.name = value;
                            } else if (key == "State") {
                                status.state = value;
                            } else if (key == "VmRSS") {
                                status.memoryUsage = std::stoi(value);
                            }
                        }
                    }
                    statuses.push_back(status);
                    std::cout << "Collected process status for PID: " << pid << std::endl;
                }
            } catch (...) {
                // Not a valid PID directory, ignore it
            }
        }
    }
    closedir(dir);
}