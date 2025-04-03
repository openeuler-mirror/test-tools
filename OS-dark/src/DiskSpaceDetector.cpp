#include "DiskSpaceDetector.h"
#include <iostream>
#include <vector>
#include <string>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/statvfs.h>
#include <unistd.h>
#endif

DiskSpaceDetector::DiskSpaceDetector(double thresholdPercentage)
    : thresholdPercentage_(thresholdPercentage) {
}

bool DiskSpaceDetector::detect() {
    std::vector<std::string> paths;
    
#ifdef _WIN32
    // Windows: 检查所有驱动器
    DWORD drives = GetLogicalDrives();
    char driveLetter = 'A';
    
    for (int i = 0; i < 26; i++) {
        if (drives & (1 << i)) {
            std::string path = std::string(1, driveLetter + i) + ":\\";
            paths.push_back(path);
        }
    }
#else
    // Linux/Unix: 检查根目录和/home
    paths.push_back("/");
    paths.push_back("/home");
#endif

    bool diskSpaceLow = false;
    
    for (const auto& path : paths) {
        DiskInfo info = getDiskInfo(path);
        
        if (info.usagePercentage > thresholdPercentage_) {
            std::cout << "Disk space low on " << path 
                      << ": " << info.usagePercentage << "% used ("
                      << info.freeSpace / (1024 * 1024) << " MB free)" << std::endl;
            diskSpaceLow = true;
        }
    }
    
    return diskSpaceLow;
}

DiskSpaceDetector::DiskInfo DiskSpaceDetector::getDiskInfo(const std::string& path) {
    DiskInfo info;
    info.path = path;
    
#ifdef _WIN32
    // Windows实现
    ULARGE_INTEGER freeBytesAvailable;
    ULARGE_INTEGER totalNumberOfBytes;
    ULARGE_INTEGER totalNumberOfFreeBytes;
    
    if (GetDiskFreeSpaceExA(
            path.c_str(),
            &freeBytesAvailable,
            &totalNumberOfBytes,
            &totalNumberOfFreeBytes)) {
        
        info.totalSpace = totalNumberOfBytes.QuadPart;
        info.freeSpace = freeBytesAvailable.QuadPart;
        
        if (info.totalSpace > 0) {
            info.usagePercentage = 100.0 * (1.0 - static_cast<double>(info.freeSpace) / info.totalSpace);
        } else {
            info.usagePercentage = 0.0;
        }
    } else {
        std::cerr << "Error getting disk space for " << path << std::endl;
        info.totalSpace = 0;
        info.freeSpace = 0;
        info.usagePercentage = 0.0;
    }
#else
    // Linux/Unix实现
    struct statvfs stat;
    
    if (statvfs(path.c_str(), &stat) == 0) {
        info.totalSpace = stat.f_blocks * stat.f_frsize;
        info.freeSpace = stat.f_bfree * stat.f_frsize;
        
        if (info.totalSpace > 0) {
            info.usagePercentage = 100.0 * (1.0 - static_cast<double>(info.freeSpace) / info.totalSpace);
        } else {
            info.usagePercentage = 0.0;
        }
    } else {
        std::cerr << "Error getting disk space for " << path << std::endl;
        info.totalSpace = 0;
        info.freeSpace = 0;
        info.usagePercentage = 0.0;
    }
#endif
    
    return info;
}

void DiskSpaceDetector::setThreshold(double thresholdPercentage) {
    thresholdPercentage_ = thresholdPercentage;
} 