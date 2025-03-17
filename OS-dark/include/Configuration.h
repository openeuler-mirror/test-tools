// Configuration.h
#ifndef CONFIGURATION_H
#define CONFIGURATION_H

#include <string>
#include <map>
#include <memory>

class Configuration {
public:
    static Configuration& getInstance();
    
    // 从文件加载配置
    bool loadFromFile(const std::string& filename);
    
    // 保存配置到文件
    bool saveToFile(const std::string& filename);
    
    // 获取字符串值
    std::string getString(const std::string& key, const std::string& defaultValue = "") const;
    
    // 获取整数值
    int getInt(const std::string& key, int defaultValue = 0) const;
    
    // 获取浮点值
    double getDouble(const std::string& key, double defaultValue = 0.0) const;
    
    // 获取布尔值
    bool getBool(const std::string& key, bool defaultValue = false) const;
    
    // 设置值
    void setString(const std::string& key, const std::string& value);
    void setInt(const std::string& key, int value);
    void setDouble(const std::string& key, double value);
    void setBool(const std::string& key, bool value);
    
private:
    Configuration();
    ~Configuration() = default;
    Configuration(const Configuration&) = delete;
    Configuration& operator=(const Configuration&) = delete;
    
    std::map<std::string, std::string> configValues_;
};

#endif // CONFIGURATION_H 