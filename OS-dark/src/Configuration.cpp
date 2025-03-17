#include "Configuration.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

Configuration& Configuration::getInstance() {
    static Configuration instance;
    return instance;
}

Configuration::Configuration() {
    // 设置默认配置
    // 磁盘空间相关
    setDouble("disk_space_threshold", 85.0);
    
    // 日志相关
    setInt("log_retention_days", 30);
    setString("log_directory", "/var/log/osdark");
    
    // 网络相关
    setDouble("network_packet_loss_threshold", 5.0);
    setInt("network_latency_threshold", 100);
    setBool("network_monitoring_enabled", true);
    setString("network_test_targets", "8.8.8.8,1.1.1.1,208.67.222.222");
    
    // 警报相关
    setBool("enable_email_alerts", false);
    setString("email_recipient", "admin@example.com");
    setString("email_sender", "osdark@example.com");
    setString("smtp_server", "smtp.example.com");
    setInt("smtp_port", 587);
    setBool("smtp_use_tls", true);
    
    // 监控频率（分钟）
    setInt("monitoring_interval", 15);
}

bool Configuration::loadFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open configuration file: " << filename << std::endl;
        return false;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        // 跳过注释和空行
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        std::istringstream iss(line);
        std::string key, value;
        
        if (std::getline(iss, key, '=') && std::getline(iss, value)) {
            // 去除前后空格
            key.erase(0, key.find_first_not_of(" \t"));
            key.erase(key.find_last_not_of(" \t") + 1);
            
            value.erase(0, value.find_first_not_of(" \t"));
            value.erase(value.find_last_not_of(" \t") + 1);
            
            configValues_[key] = value;
        }
    }
    
    return true;
}

bool Configuration::saveToFile(const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open configuration file for writing: " << filename << std::endl;
        return false;
    }
    
    file << "# OS Dark Configuration File\n";
    file << "# Generated on " << __DATE__ << " " << __TIME__ << "\n\n";
    
    for (const auto& pair : configValues_) {
        file << pair.first << " = " << pair.second << "\n";
    }
    
    return true;
}

std::string Configuration::getString(const std::string& key, const std::string& defaultValue) const {
    auto it = configValues_.find(key);
    if (it != configValues_.end()) {
        return it->second;
    }
    return defaultValue;
}

int Configuration::getInt(const std::string& key, int defaultValue) const {
    auto it = configValues_.find(key);
    if (it != configValues_.end()) {
        try {
            return std::stoi(it->second);
        } catch (const std::exception& e) {
            std::cerr << "Error converting value for key '" << key << "' to int: " << e.what() << std::endl;
        }
    }
    return defaultValue;
}

double Configuration::getDouble(const std::string& key, double defaultValue) const {
    auto it = configValues_.find(key);
    if (it != configValues_.end()) {
        try {
            return std::stod(it->second);
        } catch (const std::exception& e) {
            std::cerr << "Error converting value for key '" << key << "' to double: " << e.what() << std::endl;
        }
    }
    return defaultValue;
}

bool Configuration::getBool(const std::string& key, bool defaultValue) const {
    auto it = configValues_.find(key);
    if (it != configValues_.end()) {
        std::string value = it->second;
        // 转换为小写
        std::transform(value.begin(), value.end(), value.begin(), 
                      [](unsigned char c){ return std::tolower(c); });
        
        if (value == "true" || value == "yes" || value == "1") {
            return true;
        } else if (value == "false" || value == "no" || value == "0") {
            return false;
        }
    }
    return defaultValue;
}

void Configuration::setString(const std::string& key, const std::string& value) {
    configValues_[key] = value;
}

void Configuration::setInt(const std::string& key, int value) {
    configValues_[key] = std::to_string(value);
}

void Configuration::setDouble(const std::string& key, double value) {
    configValues_[key] = std::to_string(value);
}

void Configuration::setBool(const std::string& key, bool value) {
    configValues_[key] = value ? "true" : "false";
} 