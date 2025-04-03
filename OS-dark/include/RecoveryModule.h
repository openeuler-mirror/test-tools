// RecoveryModule.h
#ifndef RECOVERYMODULE_H
#define RECOVERYMODULE_H

#include <string>

class RecoveryModule {
public:
    virtual void analyzeData(const std::string& data) = 0;
    virtual void generateReport() = 0;
};

#endif // RECOVERYMODULE_H