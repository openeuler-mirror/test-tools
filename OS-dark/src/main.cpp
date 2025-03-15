#include "ComponentFactory.h"
#include "Configuration.h"
#include "AsyncProcessor.h"
#include "AlertManager.h"
#include "WebServer.h"
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>

// 前向声明
class DefaultComponentFactory;

// 生成系统报告
std::string generateSystemReport(
    const std::shared_ptr<DataCollector>& dataCollector,
    bool systemRestart,
    bool kernelCrash,
    bool oom,
    bool diskSpaceLow,
    bool networkIssues) {
    
    std::stringstream report;
    
    report << "System Report\n";
    report << "-------------\n";
    report << "Timestamp: " << std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()) << "\n";
    report << "System Logs: " << dataCollector->getSystemLogs().size() << "\n";
    report << "Process Statuses: " << dataCollector->getProcessStatuses().size() << "\n";
    report << "Memory Usage: " << dataCollector->getMemoryUsage().usedMemory << " bytes\n";
    report << "Issues Detected:\n";
    
    if (systemRestart) report << "- System Restart\n";
    if (kernelCrash) report << "- Kernel Crash\n";
    if (oom) report << "- Out of Memory\n";
    if (diskSpaceLow) report << "- Disk Space Low\n";
    if (networkIssues) report << "- Network Connectivity Issues\n";
    
    if (!systemRestart && !kernelCrash && !oom && !diskSpaceLow && !networkIssues) {
        report << "- No issues detected\n";
    }
    
    return report.str();
}

// 创建警报
void createAlerts(
    bool systemRestart,
    bool kernelCrash,
    bool oom,
    bool diskSpaceLow,
    bool networkIssues) {
    
    auto& alertManager = AlertManager::getInstance();
    
    if (systemRestart) {
        alertManager.addAlert(
            "System Restart Detected",
            "The system has been restarted unexpectedly. Please check system logs for details.",
            AlertManager::AlertLevel::WARNING
        );
    }
    
    if (kernelCrash) {
        alertManager.addAlert(
            "Kernel Crash Detected",
            "A kernel crash has been detected. This may indicate hardware issues or driver problems.",
            AlertManager::AlertLevel::CRITICAL
        );
    }
    
    if (oom) {
        alertManager.addAlert(
            "Out of Memory Condition Detected",
            "The system has experienced an out of memory condition. Some processes may have been terminated.",
            AlertManager::AlertLevel::ERROR
        );
    }
    
    if (diskSpaceLow) {
        alertManager.addAlert(
            "Disk Space Low",
            "Available disk space is below the configured threshold. Please free up space to avoid system issues.",
            AlertManager::AlertLevel::WARNING
        );
    }
    
    if (networkIssues) {
        alertManager.addAlert(
            "Network Connectivity Issues",
            "Network connectivity problems have been detected. This may affect system services that rely on network access.",
            AlertManager::AlertLevel::WARNING
        );
    }
}

int main(int argc, char* argv[]) {
    std::cout << "OS Dark - System Monitoring Tool" << std::endl;
    std::cout << "--------------------------------" << std::endl;
    
    // 加载配置
    auto& config = Configuration::getInstance();
    if (argc > 1) {
        std::string configFile = argv[1];
        std::cout << "Loading configuration from: " << configFile << std::endl;
        if (!config.loadFromFile(configFile)) {
            std::cout << "Failed to load configuration, using defaults." << std::endl;
        }
    } else {
        std::cout << "No configuration file specified, using defaults." << std::endl;
    }
    
    // 创建组件工厂
    std::shared_ptr<ComponentFactory> factory = std::make_shared<DefaultComponentFactory>();
    
    // 启动异步处理器
    auto& asyncProcessor = AsyncProcessor::getInstance();
    asyncProcessor.start();
    
    // 创建组件
    auto dataCollector = factory->createDataCollector();
    auto triggerMechanism = factory->createTriggerMechanism();
    auto dataStorage = factory->createDataStorage();
    auto recoveryModule = factory->createRecoveryModule();
    
    // 异步收集数据
    auto collectFuture = asyncProcessor.submit([&dataCollector]() {
        dataCollector->collectSystemLogs();
        dataCollector->collectProcessStatus();
        dataCollector->collectMemoryUsage();
        return true;
    });
    
    // 等待数据收集完成
    collectFuture.wait();
    
    // 检测系统问题
    bool systemRestart = triggerMechanism->detectSystemRestart();
    bool kernelCrash = triggerMechanism->detectKernelCrash();
    bool oom = triggerMechanism->detectOOM();
    bool diskSpaceLow = triggerMechanism->detectDiskSpaceLow();
    
    // 检查是否启用了网络监控
    bool networkIssues = false;
    if (config.getBool("network_monitoring_enabled", true)) {
        networkIssues = triggerMechanism->detectNetworkIssues();
    }
    
    // 生成系统报告
    std::string reportData = generateSystemReport(
        dataCollector, systemRestart, kernelCrash, oom, diskSpaceLow, networkIssues);
    
    // 如果检测到任何问题，则生成警报和报告
    bool issuesDetected = systemRestart || kernelCrash || oom || diskSpaceLow || networkIssues;
    
    if (issuesDetected) {
        std::cout << "\nDetected system issues, generating report and alerts..." << std::endl;
        
        // 创建警报
        createAlerts(systemRestart, kernelCrash, oom, diskSpaceLow, networkIssues);
        
        // 存储数据
        std::string filename = "system_report_" + 
            std::to_string(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now())) + ".txt";
        
        // 异步存储数据
        auto storageFuture = asyncProcessor.submit([&dataStorage, reportData, filename]() {
            return dataStorage->store(reportData, filename, false);
        });
        
        // 等待存储完成
        bool storageSuccess = storageFuture.get();
        
        if (storageSuccess) {
            std::cout << "Report saved to: " << filename << std::endl;
            
            // 异步分析数据和生成报告
            auto analysisFuture = asyncProcessor.submit([&recoveryModule, reportData]() {
                recoveryModule->analyzeData(reportData);
                recoveryModule->generateReport();
                return true;
            });
            
            // 等待分析完成
            analysisFuture.wait();
            
            // 发送所有未发送的警报
            auto& alertManager = AlertManager::getInstance();
            if (alertManager.getPendingAlerts().size() > 0) {
                std::cout << "Sending alerts..." << std::endl;
                alertManager.sendAllPendingAlerts();
            }
        } else {
            std::cerr << "Failed to save report." << std::endl;
        }
    } else {
        std::cout << "\nNo system issues detected." << std::endl;
        
        // 即使没有问题，也保存一个状态正常的报告
        if (config.getBool("always_save_report", false)) {
            std::string filename = "system_report_" + 
                std::to_string(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now())) + ".txt";
            
            dataStorage->store(reportData, filename, false);
            std::cout << "Normal status report saved to: " << filename << std::endl;
        }
    }
    
    // 停止异步处理器
    asyncProcessor.stop();
    
    std::cout << "\nOS Dark monitoring completed." << std::endl;
    
    WebServer server;
    server.start();
    
    return 0;
} 