// SystemLogCollector.h
#ifndef SYSTEMLOGCOLLECTOR_H
#define SYSTEMLOGCOLLECTOR_H

#include <vector>
#include <string>

struct SystemLog {
    std::string timestamp;
    std::string severity;
    std::string message;
};

class SystemLogCollector {
public:
    void collect(std::vector<SystemLog>& logs);
    void collectLogsFromFile(const std::string& filePath, std::vector<SystemLog>& logs);
    void collectLogsFromCommand(const std::string& command, std::vector<SystemLog>& logs);
    void parseLogLine(const std::string& line, std::vector<SystemLog>& logs);
};

#endif // SYSTEMLOGCOLLECTOR_H