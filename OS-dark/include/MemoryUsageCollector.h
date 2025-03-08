
// MemoryUsageCollector.h
#ifndef MEMORYUSAGECOLLECTOR_H
#define MEMORYUSAGECOLLECTOR_H

#include <vector>

struct MemoryUsage {
    size_t totalMemory;
    size_t freeMemory;
    size_t usedMemory;
};

class MemoryUsageCollector {
public:
    void collect(MemoryUsage& usage);
};

#endif // MEMORYUSAGECOLLECTOR_H
