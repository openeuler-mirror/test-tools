// DataCollector.h
#ifndef DATACOLLECTOR_H
#define DATACOLLECTOR_H

#include <vector>
#include <string>

struct SystemLog {
    std::string timestamp;
    std::string severity;
    std::string message;
};

struct ProcessStatus {
    int pid;
    std::string name;
    std::string state;
    int memoryUsage;
};

struct MemoryUsage {
    size_t usedMemory;
};

class DataCollector {
public:
    virtual void collectSystemLogs() = 0;
    virtual void collectProcessStatus() = 0;
    virtual void collectMemoryUsage() = 0;
    virtual std::vector<SystemLog> getSystemLogs() const = 0;
    virtual std::vector<ProcessStatus> getProcessStatuses() const = 0;
    virtual MemoryUsage getMemoryUsage() const = 0;
};

#endif // DATACOLLECTOR_H