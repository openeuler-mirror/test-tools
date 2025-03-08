// TriggerMechanism.h
#ifndef TRIGGERMECHANISM_H
#define TRIGGERMECHANISM_H

class TriggerMechanism {
public:
    virtual bool detectSystemRestart() = 0;
    virtual bool detectKernelCrash() = 0;
    virtual bool detectOOM() = 0;
};

#endif // TRIGGERMECHANISM_H