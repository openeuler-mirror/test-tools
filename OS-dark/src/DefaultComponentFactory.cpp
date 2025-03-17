#include "ComponentFactory.h"
#include "SystemLogCollector.h"
#include "ProcessStatusCollector.h"
#include "MemoryUsageCollector.h"
#include "SystemRestartDetector.h"
#include "KernelCrashDetector.h"
#include "OOMDetector.h"
#include "DiskSpaceDetector.h"
#include "NetworkDetector.h"
#include "FileStorage.h"
#include "DataAnalyzer.h"
#include "ReportGenerator.h"
#include "Configuration.h"
#include <memory>

// 前向声明
class ConcreteDataCollector;
class ConcreteTriggerMechanism;
class ConcreteRecoveryModule;

class DefaultComponentFactory : public ComponentFactory {
public:
    std::shared_ptr<DataCollector> createDataCollector() override {
        auto logCollector = std::make_shared<SystemLogCollector>();
        auto processCollector = std::make_shared<ProcessStatusCollector>();
        auto memoryCollector = std::make_shared<MemoryUsageCollector>();
        
        return std::make_shared<ConcreteDataCollector>(
            logCollector, processCollector, memoryCollector);
    }
    
    std::shared_ptr<TriggerMechanism> createTriggerMechanism() override {
        return std::make_shared<ConcreteTriggerMechanism>();
    }
    
    std::shared_ptr<DataStorage> createDataStorage() override {
        return std::make_shared<FileStorage>();
    }
    
    std::shared_ptr<RecoveryModule> createRecoveryModule() override {
        return std::make_shared<ConcreteRecoveryModule>();
    }
};

// 实现ConcreteDataCollector
class ConcreteDataCollector : public DataCollector {
public:
    ConcreteDataCollector(
        std::shared_ptr<SystemLogCollector> logCollector,
        std::shared_ptr<ProcessStatusCollector> processCollector,
        std::shared_ptr<MemoryUsageCollector> memoryCollector)
        : logCollector_(logCollector),
          processCollector_(processCollector),
          memoryCollector_(memoryCollector) {}

    void collectSystemLogs() override {
        logCollector_->collect(systemLogs);
        std::cout << "Collected " << systemLogs.size() << " system logs." << std::endl;
    }

    void collectProcessStatus() override {
        processCollector_->collect(processStatuses);
        std::cout << "Collected " << processStatuses.size() << " process statuses." << std::endl;
    }

    void collectMemoryUsage() override {
        memoryCollector_->collect(memoryUsage);
        std::cout << "Collected memory usage: " << memoryUsage.usedMemory << " bytes used." << std::endl;
    }

    std::vector<SystemLog> getSystemLogs() const override {
        return systemLogs;
    }

    std::vector<ProcessStatus> getProcessStatuses() const override {
        return processStatuses;
    }

    MemoryUsage getMemoryUsage() const override {
        return memoryUsage;
    }

private:
    std::shared_ptr<SystemLogCollector> logCollector_;
    std::shared_ptr<ProcessStatusCollector> processCollector_;
    std::shared_ptr<MemoryUsageCollector> memoryCollector_;
    std::vector<SystemLog> systemLogs;
    std::vector<ProcessStatus> processStatuses;
    MemoryUsage memoryUsage;
};

// 实现ConcreteTriggerMechanism
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
    
    bool detectDiskSpaceLow() override {
        // 从配置中获取磁盘空间阈值
        auto& config = Configuration::getInstance();
        double threshold = config.getDouble("disk_space_threshold", 85.0);
        
        DiskSpaceDetector detector(threshold);
        bool result = detector.detect();
        std::cout << "Disk space low detected: " << (result ? "Yes" : "No") << std::endl;
        return result;
    }
    
    bool detectNetworkIssues() override {
        // 从配置中获取网络参数
        auto& config = Configuration::getInstance();
        double packetLossThreshold = config.getDouble("network_packet_loss_threshold", 5.0);
        int latencyThreshold = config.getInt("network_latency_threshold", 100);
        
        NetworkDetector detector(packetLossThreshold, latencyThreshold);
        bool result = detector.detect();
        std::cout << "Network issues detected: " << (result ? "Yes" : "No") << std::endl;
        return result;
    }
};

// 实现ConcreteRecoveryModule
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