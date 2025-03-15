// AlertManager.h
#ifndef ALERTMANAGER_H
#define ALERTMANAGER_H

#include <string>
#include <vector>

class AlertManager {
public:
    enum class AlertLevel {
        INFO,
        WARNING,
        ERROR,
        CRITICAL
    };
    
    struct Alert {
        std::string title;
        std::string message;
        AlertLevel level;
        std::string timestamp;
    };
    
    static AlertManager& getInstance();
    
    // 添加警报
    void addAlert(const std::string& title, const std::string& message, AlertLevel level);
    
    // 发送邮件警报
    bool sendEmailAlert(const Alert& alert);
    
    // 发送所有未发送的警报
    bool sendAllPendingAlerts();
    
    // 获取所有警报
    std::vector<Alert> getAllAlerts() const;
    
    // 获取未发送的警报
    std::vector<Alert> getPendingAlerts() const;
    
    // 清除所有警报
    void clearAlerts();
    
private:
    AlertManager();
    ~AlertManager() = default;
    AlertManager(const AlertManager&) = delete;
    AlertManager& operator=(const AlertManager&) = delete;
    
    // 获取当前时间戳
    std::string getCurrentTimestamp() const;
    
    // 构建邮件内容
    std::string buildEmailContent(const Alert& alert) const;
    
    std::vector<Alert> alerts_;
    std::vector<bool> alertSent_;
};

#endif // ALERTMANAGER_H 