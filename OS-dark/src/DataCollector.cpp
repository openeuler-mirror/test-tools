#include "DataCollector.h"
#include "DistributedMonitor.h"
#include <iostream>

void DataCollector::collectData() {
    // 收集本地数据
    std::string data = "Sample data from DataCollector";
    std::cout << "Collecting data: " << data << std::endl;
    // 发送数据到分布式监控模块
    distributedMonitor->sendData(data);
} 