// DataCollector.h
#ifndef DATACOLLECTOR_H
#define DATACOLLECTOR_H

#include <string>

class DataCollector {
public:
    virtual void collectSystemLogs() = 0;
    virtual void collectProcessStatus() = 0;
    virtual void collectMemoryUsage() = 0;
};

#endif // DATACOLLECTOR_H