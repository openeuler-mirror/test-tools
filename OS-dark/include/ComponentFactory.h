// ComponentFactory.h
#ifndef COMPONENTFACTORY_H
#define COMPONENTFACTORY_H

#include <memory>
#include "DataCollector.h"
#include "TriggerMechanism.h"
#include "DataStorage.h"
#include "RecoveryModule.h"

class ComponentFactory {
public:
    virtual ~ComponentFactory() = default;
    
    // 创建数据收集器
    virtual std::shared_ptr<DataCollector> createDataCollector() = 0;
    
    // 创建触发机制
    virtual std::shared_ptr<TriggerMechanism> createTriggerMechanism() = 0;
    
    // 创建数据存储
    virtual std::shared_ptr<DataStorage> createDataStorage() = 0;
    
    // 创建恢复模块
    virtual std::shared_ptr<RecoveryModule> createRecoveryModule() = 0;
};

#endif // COMPONENTFACTORY_H 