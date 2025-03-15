#ifndef DISTRIBUTED_MONITOR_H
#define DISTRIBUTED_MONITOR_H

#include <string>
#include <vector>
#include <functional>

class DistributedMonitor {
public:
    DistributedMonitor(const std::string& serverUrl);
    void startNode();
    void stopNode();
    void sendData(const std::string& data);
    void receiveData(const std::string& data);
    void processData();
    void generateReport();

private:
    std::string serverUrl;
    bool isRunning;
    std::vector<std::string> collectedData;
};

#endif // DISTRIBUTED_MONITOR_H 