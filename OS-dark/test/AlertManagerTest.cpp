#include "AlertManager.h"
#include "Configuration.h"
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <vector>
#include <string>

using ::testing::Return;
using ::testing::_;

// Mock Configuration class for testing
class MockConfiguration : public Configuration {
public:
    MOCK_METHOD(bool, getBool, (const std::string&, bool), (const, override));
    MOCK_METHOD(std::string, getString, (const std::string&, const std::string&), (const, override));
    MOCK_METHOD(int, getInt, (const std::string&, int), (const, override));
};

// Test cases for AlertManager
TEST(AlertManagerTest, AddAlert) {
    AlertManager& alertManager = AlertManager::getInstance();
    alertManager.clearAlerts(); // Clear any existing alerts

    alertManager.addAlert("Test Title", "Test Message", AlertLevel::INFO);

    std::vector<AlertManager::Alert> alerts = alertManager.getAllAlerts();
    EXPECT_EQ(alerts.size(), 1);
    EXPECT_EQ(alerts[0].title, "Test Title");
    EXPECT_EQ(alerts[0].message, "Test Message");
    EXPECT_EQ(alerts[0].level, AlertLevel::INFO);
}

TEST(AlertManagerTest, SendEmailAlert) {
    AlertManager& alertManager = AlertManager::getInstance();
    alertManager.clearAlerts(); // Clear any existing alerts

    MockConfiguration mockConfig;
    Configuration::setInstance(&mockConfig);

    EXPECT_CALL(mockConfig, getBool("enable_email_alerts", false)).WillOnce(Return(true));
    EXPECT_CALL(mockConfig, getString("email_recipient", "admin@example.com")).WillOnce(Return("test@example.com"));
    EXPECT_CALL(mockConfig, getString("email_sender", "osdark@example.com")).WillOnce(Return("osdark@example.com"));
    EXPECT_CALL(mockConfig, getString("smtp_server", "smtp.example.com")).WillOnce(Return("smtp.example.com"));
    EXPECT_CALL(mockConfig, getInt("smtp_port", 587)).WillOnce(Return(587));

    Alert alert = {"Test Title", "Test Message", AlertLevel::INFO, alertManager.getCurrentTimestamp()};
    bool sent = alertManager.sendEmailAlert(alert);

    EXPECT_TRUE(sent);
    std::vector<AlertManager::Alert> alerts = alertManager.getAllAlerts();
    EXPECT_EQ(alerts.size(), 1);
    EXPECT_TRUE(alerts[0].alertSent);
}

TEST(AlertManagerTest, SendAllPendingAlerts) {
    AlertManager& alertManager = AlertManager::getInstance();
    alertManager.clearAlerts(); // Clear any existing alerts

    MockConfiguration mockConfig;
    Configuration::setInstance(&mockConfig);

    EXPECT_CALL(mockConfig, getBool("enable_email_alerts", false)).WillOnce(Return(true));
    EXPECT_CALL(mockConfig, getString("email_recipient", "admin@example.com")).WillOnce(Return("test@example.com"));
    EXPECT_CALL(mockConfig, getString("email_sender", "osdark@example.com")).WillOnce(Return("osdark@example.com"));
    EXPECT_CALL(mockConfig, getString("smtp_server", "smtp.example.com")).WillOnce(Return("smtp.example.com"));
    EXPECT_CALL(mockConfig, getInt("smtp_port", 587)).WillOnce(Return(587));

    alertManager.addAlert("Test Title 1", "Test Message 1", AlertLevel::INFO);
    alertManager.addAlert("Test Title 2", "Test Message 2", AlertLevel::WARNING);

    bool allSent = alertManager.sendAllPendingAlerts();

    EXPECT_TRUE(allSent);
    std::vector<AlertManager::Alert> alerts = alertManager.getAllAlerts();
    EXPECT_EQ(alerts.size(), 2);
    EXPECT_TRUE(alerts[0].alertSent);
    EXPECT_TRUE(alerts[1].alertSent);
}

TEST(AlertManagerTest, GetPendingAlerts) {
    AlertManager& alertManager = AlertManager::getInstance();
    alertManager.clearAlerts(); // Clear any existing alerts

    alertManager.addAlert("Test Title 1", "Test Message 1", AlertLevel::INFO);
    alertManager.addAlert("Test Title 2", "Test Message 2", AlertLevel::WARNING);

    std::vector<AlertManager::Alert> pendingAlerts = alertManager.getPendingAlerts();
    EXPECT_EQ(pendingAlerts.size(), 2);

    alertManager.sendAllPendingAlerts();

    pendingAlerts = alertManager.getPendingAlerts();
    EXPECT_EQ(pendingAlerts.size(), 0);
}
