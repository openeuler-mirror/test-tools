#include "DistributedMonitor.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <curl/curl.h>

DistributedMonitor::DistributedMonitor(const std::string& serverUrl) : serverUrl(serverUrl), isRunning(false) {
    curl_global_init(CURL_GLOBAL_DEFAULT);
}

void DistributedMonitor::startNode() {
    isRunning = true;
    std::cout << "Node started." << std::endl;
    // 模拟数据收集和发送
    while (isRunning) {
        std::this_thread::sleep_for(std::chrono::seconds(5));
        sendData("Sample data from node");
    }
}

void DistributedMonitor::stopNode() {
    isRunning = false;
    std::cout << "Node stopped." << std::endl;
    curl_global_cleanup();
}

void DistributedMonitor::sendData(const std::string& data) {
    CURL *curl = curl_easy_init();
    if (curl) {
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_URL, serverUrl.c_str());
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            std::cerr << "Failed to send data: " << curl_easy_strerror(res) << std::endl;
        }
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }
}

void DistributedMonitor::receiveData(const std::string& data) {
    collectedData.push_back(data);
    std::cout << "Received data: " << data << std::endl;
}

void DistributedMonitor::processData() {
    std::cout << "Processing collected data..." << std::endl;
    // 处理收集到的数据
    for (const auto& data : collectedData) {
        std::cout << "Processing: " << data << std::endl;
    }
}

void DistributedMonitor::generateReport() {
    std::cout << "Generating report from collected data..." << std::endl;
    // 生成报告
    for (const auto& data : collectedData) {
        std::cout << "Report data: " << data << std::endl;
    }
} 