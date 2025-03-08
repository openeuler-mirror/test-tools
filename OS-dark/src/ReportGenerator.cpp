// ReportGenerator.cpp
#include "ReportGenerator.h"
#include "ConcreteDataCollector.h"
#include "ConcreteTriggerMechanism.h"
#include "ConcreteRecoveryModule.h"
#include "FileStorage.h"
#include <iostream>
#include <sstream>

void ReportGenerator::generate() {
    // 模拟生成报告
    std::cout << "Generating report..." << std::endl;

    ConcreteDataCollector dataCollector;
    dataCollector.collectSystemLogs();
    dataCollector.collectProcessStatus();
    dataCollector.collectMemoryUsage();

    ConcreteTriggerMechanism triggerMechanism;
    bool systemRestart = triggerMechanism.detectSystemRestart();
    bool kernelCrash = triggerMechanism.detectKernelCrash();
    bool oom = triggerMechanism.detectOOM();

    std::ostringstream report;
    report << "System Report\n";
    report << "=================\n";

    // Collect and add system logs to the report
    report << "System Logs:\n";
    for (const auto& log : dataCollector.getSystemLogs()) {
        report << log.timestamp << " - " << log.severity << " - " << log.message << "\n";
    }
    report << "\n";

    // Collect and add process statuses to the report
    report << "Process Statuses:\n";
    for (const auto& status : dataCollector.getProcessStatuses()) {
        report << "PID: " << status.pid << ", Name: " << status.name
               << ", State: " << status.state << ", Memory Usage: " << status.memoryUsage << " kB\n";
    }
    report << "\n";

    // Collect and add memory usage to the report
    report << "Memory Usage:\n";
    report << "Used Memory: " << dataCollector.getMemoryUsage().usedMemory << " bytes\n";
    report << "\n";

    // Add trigger mechanism results to the report
    report << "Trigger Mechanism Results:\n";
    report << "System Restart Detected: " << (systemRestart ? "Yes" : "No") << "\n";
    report << "Kernel Crash Detected: " << (kernelCrash ? "Yes" : "No") << "\n";
    report << "OOM Detected: " << (oom ? "Yes" : "No") << "\n";
    report << "\n";

    // Output the report to the console
    std::cout << report.str();

    // Optionally, store the report to a file
    FileStorage storage;
    storage.store(report.str(), "system_report.txt", false);
}