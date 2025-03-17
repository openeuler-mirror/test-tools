// NetworkDetector.h
#ifndef NETWORKDETECTOR_H
#define NETWORKDETECTOR_H

#include <string>
#include <vector>

class NetworkDetector {
public:
    struct NetworkInterface {
        std::string name;
        std::string ipAddress;
        bool isUp;
        double packetLossRate;
        int latency; // 毫秒
    };

    NetworkDetector(double packetLossThreshold = 5.0, int latencyThreshold = 100);
    
    // 检测网络连接问题
    bool detect();
    
    // 获取所有网络接口信息
    std::vector<NetworkInterface> getAllInterfaces();
    
    // 测试特定接口的连接性
    NetworkInterface testInterface(const std::string& interfaceName);
    
    // 设置阈值
    void setPacketLossThreshold(double threshold);
    void setLatencyThreshold(int threshold);
    
private:
    double packetLossThreshold_; // 丢包率阈值（百分比）
    int latencyThreshold_;       // 延迟阈值（毫秒）
    
    // 执行ping测试
    bool pingTest(const std::string& target, double& packetLoss, int& latency);
};

#endif // NETWORKDETECTOR_H 