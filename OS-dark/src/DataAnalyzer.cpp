#include "DataAnalyzer.h"
#include <iostream>
#include <sstream>
#include <map>
#include <string>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

// 新增方法：从持久化内存中读取数据
std::string DataAnalyzer::readFromPersistentMemory(const std::string& memFilePath) {
    int fd = open(memFilePath.c_str(), O_RDONLY);
    if (fd == -1) {
        std::cerr << "Error opening file for reading from memory mapping" << std::endl;
        return "";
    }

    // Get the size of the file
    struct stat sb;
    if (fstat(fd, &sb) == -1) {
        close(fd);
        std::cerr << "Error getting file size" << std::endl;
        return "";
    }

    // Map the file into memory
    char* map = (char*)mmap(0, sb.st_size, PROT_READ, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) {
        close(fd);
        std::cerr << "Error mmapping the file" << std::endl;
        return "";
    }

    // Read the data from the mapped memory
    std::string data(map, sb.st_size);

    // Unmap the memory
    if (munmap(map, sb.st_size) == -1) {
        close(fd);
        std::cerr << "Error un-mmapping the file" << std::endl;
        return "";
    }

    // Close the file
    close(fd);

    return data;
}

void DataAnalyzer::analyze(const std::string& data) {
    if (data.empty()) {
        std::cerr << "No data to analyze." << std::endl;
        return;
    }

    // Read data from persistent memory
    std::string persistentData = readFromPersistentMemory("kernel_crash_mem.log");
    if (!persistentData.empty()) {
        std::istringstream persistentStream(persistentData);
        std::string line;
        while (std::getline(persistentStream, line)) {
            if (line.find("ERROR") != std::string::npos) {
                std::string errorMessage = line.substr(line.find("ERROR"));
                errorCount[errorMessage]++;
            } else if (line.find("WARNING") != std::string::npos) {
                std::string warningMessage = line.substr(line.find("WARNING"));
                warningCount[warningMessage]++;
            }
        }
    }

    std::istringstream stream(data);
    std::string line;

    while (std::getline(stream, line)) {
        if (line.find("ERROR") != std::string::npos) {
            std::string errorMessage = line.substr(line.find("ERROR"));
            errorCount[errorMessage]++;
        } else if (line.find("WARNING") != std::string::npos) {
            std::string warningMessage = line.substr(line.find("WARNING"));
            warningCount[warningMessage]++;
        }
    }

    std::cout << "Error Analysis Report:" << std::endl;
    for (const auto& entry : errorCount) {
        std::cout << entry.first << " - Count: " << entry.second << std::endl;
    }

    std::cout << "\nWarning Analysis Report:" << std::endl;
    for (const auto& entry : warningCount) {
        std::cout << entry.first << " - Count: " << entry.second << std::endl;
    }
}