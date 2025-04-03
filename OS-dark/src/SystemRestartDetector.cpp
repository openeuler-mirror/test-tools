#include "SystemRestartDetector.h"
#include <iostream>
#include <fstream>
#include <string>
#include <ctime>
#include "SystemLogCollector.h"
#include "ProcessStatusCollector.h"
#include "KernelCrashDetector.h"
#include "FileStorage.h"

bool SystemRestartDetector::detect() {
    const std::string statFilePath = "/proc/stat";
    std::ifstream statFile(statFilePath, std::ios::in);
    if (!statFile.is_open()) {
        std::cerr << "Unable to open " << statFilePath << std::endl;
        return false;
    }

    // Get the current modification time of /proc/stat
    struct stat fileStat;
    if (stat(statFilePath.c_str(), &fileStat) != 0) {
        std::cerr << "Unable to get file stats for " << statFilePath << std::endl;
        return false;
    }
    time_t currentModTime = fileStat.st_mtime;

    // Read the last modification time from a file
    std::ifstream lastModTimeFile("last_mod_time.txt", std::ios::in);
    time_t lastModTime = 0;
    if (lastModTimeFile.is_open()) {
        lastModTimeFile >> lastModTime;
        lastModTimeFile.close();
    }

    // Write the current modification time to the file
    std::ofstream outLastModTimeFile("last_mod_time.txt", std::ios::out);
    if (outLastModTimeFile.is_open()) {
        outLastModTimeFile << currentModTime;
        outLastModTimeFile.close();
    }

    // Compare the modification times
    bool systemRestarted = (currentModTime != lastModTime);
    if (systemRestarted) {
        std::cout << "Detected system restart." << std::endl;

        // Trigger system information collection
        SystemLogCollector systemLogCollector;
        std::vector<SystemLog> systemLogs;
        systemLogCollector.collect(systemLogs);

        // Trigger process information collection
        ProcessStatusCollector processStatusCollector;
        std::vector<ProcessStatus> processStatuses;
        processStatusCollector.collect(processStatuses);

        // Trigger kernel crash detection and log collection
        KernelCrashDetector kernelCrashDetector;
        bool kernelCrashDetected = kernelCrashDetector.detect();

        // Write collected data to persistent file
        FileStorage storage;
        std::ostringstream dataStream;
        dataStream << "System Logs:\n";
        for (const auto& log : systemLogs) {
            dataStream << log.timestamp << " - " << log.severity << " - " << log.message << "\n";
        }
        dataStream << "\nProcess Statuses:\n";
        for (const auto& status : processStatuses) {
            dataStream << "PID: " << status.pid << ", Name: " << status.name
                       << ", State: " << status.state << ", Memory Usage: " << status.memoryUsage << " kB\n";
        }
        dataStream << "\nKernel Crash Detected: " << (kernelCrashDetected ? "Yes" : "No") << "\n";
        storage.store(dataStream.str(), "system_data_after_restart.txt", false);
    } else {
        std::cout << "No system restart detected." << std::endl;
    }

    return systemRestarted;
}