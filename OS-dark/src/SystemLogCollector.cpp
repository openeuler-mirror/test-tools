#include "SystemLogCollector.h"
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>

void SystemLogCollector::collect(std::vector<SystemLog>& logs) {
    // 实际收集系统日志
    collectLogsFromFile("/var/log/messages", logs);
    collectLogsFromCommand("dmesg", logs);
    collectLogsFromCommand("journalctl", logs);
    collectLogsFromCommand("cat /var/log/kern.log", logs); // Example for kern.log
    collectLogsFromCommand("cat /var/log/syslog", logs);  // Example for syslog

    std::cout << "Collected system logs." << std::endl;
}

void SystemLogCollector::collectLogsFromFile(const std::string& filePath, std::vector<SystemLog>& logs) {
    std::ifstream logFile(filePath);
    if (!logFile.is_open()) {
        std::cerr << "Unable to open system log file: " << filePath << std::endl;
        return;
    }

    std::string line;
    while (std::getline(logFile, line)) {
        parseLogLine(line, logs);
    }

    logFile.close();
}

void SystemLogCollector::collectLogsFromCommand(const std::string& command, std::vector<SystemLog>& logs) {
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        std::cerr << "Failed to run command: " << command << std::endl;
        return;
    }

    char buffer[128];
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr) {
            std::string line(buffer);
            line.pop_back(); // Remove newline character
            parseLogLine(line, logs);
        }
    }
    pclose(pipe);
}

void SystemLogCollector::parseLogLine(const std::string& line, std::vector<SystemLog>& logs) {
    SystemLog log;
    // 假设日志格式为 "timestamp severity message"
    size_t firstSpace = line.find(' ');
    size_t secondSpace = line.find(' ', firstSpace + 1);

    if (firstSpace != std::string::npos && secondSpace != std::string::npos) {
        log.timestamp = line.substr(0, firstSpace);
        log.severity = line.substr(firstSpace + 1, secondSpace - firstSpace - 1);
        log.message = line.substr(secondSpace + 1);
        logs.push_back(log);
    }
}