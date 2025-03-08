#include "DataCollector.h"
#include "SystemLogCollector.h"
#include "ProcessStatusCollector.h"
#include "MemoryUsageCollector.h"
#include "DataStorage.h"
#include "FileStorage.h"
#include "TriggerMechanism.h"
#include "SystemRestartDetector.h"
#include "KernelCrashDetector.h"
#include "OOMDetector.h"
#include "RecoveryModule.h"
#include "DataAnalyzer.h"
#include "ReportGenerator.h"
#include <vector>
#include <string>

class ConcreteDataCollector : public DataCollector {
public:
    void collectSystemLogs() override {
        SystemLogCollector collector;
        collector.collect(systemLogs);
        std::cout << "Collected " << systemLogs.size() << " system logs." << std::endl;
    }

    void collectProcessStatus() override {
        ProcessStatusCollector collector;
        collector.collect(processStatuses);
        std::cout << "Collected " << processStatuses.size() << " process statuses." << std::endl;
    }

    void collectMemoryUsage() override {
        MemoryUsageCollector collector;
        collector.collect(memoryUsage);
        std::cout << "Collected memory usage: " << memoryUsage.usedMemory << " bytes used." << std::endl;
    }

    std::vector<SystemLog> getSystemLogs() const {
        return systemLogs;
    }

    std::vector<ProcessStatus> getProcessStatuses() const {
        return processStatuses;
    }

    MemoryUsage getMemoryUsage() const {
        return memoryUsage;
    }

private:
    std::vector<SystemLog> systemLogs;
    std::vector<ProcessStatus> processStatuses;
    MemoryUsage memoryUsage;
};

class ConcreteTriggerMechanism : public TriggerMechanism {
public:
    bool detectSystemRestart() override {
        SystemRestartDetector detector;
        bool result = detector.detect();
        std::cout << "System restart detected: " << (result ? "Yes" : "No") << std::endl;
        return result;
    }

    bool detectKernelCrash() override {
        KernelCrashDetector detector;
        bool result = detector.detect();
        std::cout << "Kernel crash detected: " << (result ? "Yes" : "No") << std::endl;
        return result;
    }

    bool detectOOM() override {
        OOMDetector detector;
        bool result = detector.detect();
        std::cout << "OOM detected: " << (result ? "Yes" : "No") << std::endl;
        return result;
    }
};

class ConcreteRecoveryModule : public RecoveryModule {
public:
    void analyzeData(const std::string& data) override {
        DataAnalyzer analyzer;
        analyzer.analyze(data);
    }

    void generateReport() override {
        ReportGenerator generator;
        generator.generate();
    }
};

int main() {
    ConcreteDataCollector dataCollector;
    dataCollector.collectSystemLogs();
    dataCollector.collectProcessStatus();
    dataCollector.collectMemoryUsage();

    ConcreteTriggerMechanism triggerMechanism;
    bool systemRestart = triggerMechanism.detectSystemRestart();
    bool kernelCrash = triggerMechanism.detectKernelCrash();
    bool oom = triggerMechanism.detectOOM();

    if (systemRestart || kernelCrash || oom) {
        FileStorage storage;
        std::string data = "System Logs: " + std::to_string(dataCollector.getSystemLogs().size()) +
                           "\nProcess Statuses: " + std::to_string(dataCollector.getProcessStatuses().size()) +
                           "\nMemory Usage: " + std::to_string(dataCollector.getMemoryUsage().usedMemory);
        storage.store(data, "system_data.txt", false); // Store data to a file

        std::string retrievedData = storage.retrieve("system_data.txt"); // Retrieve data from the file

        ConcreteRecoveryModule recoveryModule;
        recoveryModule.analyzeData(retrievedData);
        recoveryModule.generateReport();
    }

    return 0;
}