// ProcessStatusCollector.h
#ifndef PROCESSSTATUSCOLLECTOR_H
#define PROCESSSTATUSCOLLECTOR_H

#include <vector>

struct ProcessStatus {
    int pid;
    std::string name;
    std::string state;
    int memoryUsage;
};

class ProcessStatusCollector {
public:
    void collect(std::vector<ProcessStatus>& statuses);
};

#endif // PROCESSSTATUSCOLLECTOR_H