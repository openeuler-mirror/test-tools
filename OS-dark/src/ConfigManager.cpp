#include "ConfigManager.h"
#include <iostream>

void ConfigManager::loadConfig() {
    // 加载分布式监控的配置
    std::cout << "Loading distributed monitoring configuration..." << std::endl;
    // 设置服务器 URL
    serverUrl = "http://example.com/server";
} 