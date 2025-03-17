// DiskSpaceDetector.h
#ifndef DISKSPACEDETECTOR_H
#define DISKSPACEDETECTOR_H

#include <string>

class DiskSpaceDetector {
public:
    struct DiskInfo {
        std::string path;
        uint64_t totalSpace;
        uint64_t freeSpace;
        double usagePercentage;
    };

    DiskSpaceDetector(double thresholdPercentage = 90.0);
    
    // 检测磁盘空间是否不足
    bool detect();
    
    // 获取磁盘信息
    DiskInfo getDiskInfo(const std::string& path);
    
    // 设置阈值百分比
    void setThreshold(double thresholdPercentage);
    
private:
    double thresholdPercentage_; // 磁盘使用率阈值，超过此值则认为空间不足
};

#endif // DISKSPACEDETECTOR_H 