// DataAnalyzer.h
#ifndef DATAANALYZER_H
#define DATAANALYZER_H

#include <string>
#include <map>

class DataAnalyzer {
public:
    std::string readFromPersistentMemory(const std::string& memFilePath);
    void analyze(const std::string& data);

private:
    std::map<std::string, int> errorCount;
    std::map<std::string, int> warningCount;
};

#endif // DATAANALYZER_H