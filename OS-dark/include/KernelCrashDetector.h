// KernelCrashDetector.h
#ifndef KERNELCRASHDETECTOR_H
#define KERNELCRASHDETECTOR_H

#include <vector>
#include <string>

class KernelCrashDetector {
public:
    bool detect();
    std::vector<std::string> getDmesgOutput();
    void logCrashInfo(const std::string& crashInfo);
    void logCrashInfoToPersistentMemory(const std::string& crashInfo);
};

#endif // KERNELCRASHDETECTOR_H