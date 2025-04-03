#include "AlertManager.h"
#include "Configuration.h"
#include <iostream>
#include <chrono>
#include <ctime>
#include <sstream>
#include <iomanip>
#include <fstream>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#endif

AlertManager& AlertManager::getInstance() {
    static AlertManager instance;
    return instance;
}

AlertManager::AlertManager() {
}

void AlertManager::addAlert(const std::string& title, const std::string& message, AlertLevel level) {
    Alert alert;
    alert.title = title;
    alert.message = message;
    alert.level = level;
    alert.timestamp = getCurrentTimestamp();
    
    alerts_.push_back(alert);
    alertSent_.push_back(false);
    
    // 如果配置了自动发送邮件警报，则立即发送
    auto& config = Configuration::getInstance();
    if (config.getBool("enable_email_alerts", false)) {
        sendEmailAlert(alert);
    }
}

bool AlertManager::sendEmailAlert(const Alert& alert) {
    auto& config = Configuration::getInstance();
    
    // 检查是否启用了邮件警报
    if (!config.getBool("enable_email_alerts", false)) {
        std::cout << "Email alerts are disabled in configuration." << std::endl;
        return false;
    }
    
    std::string recipient = config.getString("email_recipient", "admin@example.com");
    std::string sender = config.getString("email_sender", "osdark@example.com");
    std::string smtpServer = config.getString("smtp_server", "smtp.example.com");
    int smtpPort = config.getInt("smtp_port", 587);
    
    // 构建邮件内容
    std::string emailContent = buildEmailContent(alert);
    
    // 在实际应用中，这里应该使用SMTP库发送邮件
    // 为了简化示例，我们将邮件内容写入文件
    std::string filename = "alert_" + 
        std::to_string(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now())) + ".eml";
    
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to create email file: " << filename << std::endl;
        return false;
    }
    
    file << "From: " << sender << std::endl;
    file << "To: " << recipient << std::endl;
    file << "Subject: [OS Dark Alert] " << alert.title << std::endl;
    file << "Date: " << alert.timestamp << std::endl;
    file << "Content-Type: text/plain; charset=UTF-8" << std::endl;
    file << std::endl;
    file << emailContent << std::endl;
    
    file.close();
    
    std::cout << "Alert email saved to file: " << filename << std::endl;
    std::cout << "In a production environment, this would be sent via SMTP to: " << recipient << std::endl;
    
    // 标记警报为已发送
    for (size_t i = 0; i < alerts_.size(); ++i) {
        if (alerts_[i].timestamp == alert.timestamp && 
            alerts_[i].title == alert.title && 
            alerts_[i].message == alert.message) {
            alertSent_[i] = true;
            break;
        }
    }
    
    return true;
}

bool AlertManager::sendAllPendingAlerts() {
    bool allSent = true;
    
    for (size_t i = 0; i < alerts_.size(); ++i) {
        if (!alertSent_[i]) {
            bool sent = sendEmailAlert(alerts_[i]);
            if (!sent) {
                allSent = false;
            }
        }
    }
    
    return allSent;
}

std::vector<AlertManager::Alert> AlertManager::getAllAlerts() const {
    return alerts_;
}

std::vector<AlertManager::Alert> AlertManager::getPendingAlerts() const {
    std::vector<Alert> pendingAlerts;
    
    for (size_t i = 0; i < alerts_.size(); ++i) {
        if (!alertSent_[i]) {
            pendingAlerts.push_back(alerts_[i]);
        }
    }
    
    return pendingAlerts;
}

void AlertManager::clearAlerts() {
    alerts_.clear();
    alertSent_.clear();
}

std::string AlertManager::getCurrentTimestamp() const {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

std::string AlertManager::buildEmailContent(const Alert& alert) const {
    std::stringstream content;
    
    content << "OS Dark Alert: " << alert.title << std::endl;
    content << "==============================================" << std::endl;
    content << std::endl;
    content << "Timestamp: " << alert.timestamp << std::endl;
    content << "Severity: ";
    
    switch (alert.level) {
        case AlertLevel::INFO:
            content << "INFO";
            break;
        case AlertLevel::WARNING:
            content << "WARNING";
            break;
        case AlertLevel::ERROR:
            content << "ERROR";
            break;
        case AlertLevel::CRITICAL:
            content << "CRITICAL";
            break;
    }
    
    content << std::endl << std::endl;
    content << "Message:" << std::endl;
    content << alert.message << std::endl;
    content << std::endl;
    content << "==============================================" << std::endl;
    content << "This is an automated message from OS Dark monitoring system." << std::endl;
    
    return content.str();
} 