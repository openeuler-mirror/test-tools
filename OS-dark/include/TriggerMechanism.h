// TriggerMechanism.h
#ifndef TRIGGERMECHANISM_H
#define TRIGGERMECHANISM_H

class TriggerMechanism {
public:
    virtual ~TriggerMechanism() = default;
    virtual bool detectSystemRestart() = 0;
    virtual bool detectKernelCrash() = 0;
    virtual bool detectOOM() = 0;
    virtual bool detectDiskSpaceLow() = 0;
    virtual bool detectNetworkIssues() = 0;
};

#endif // TRIGGERMECHANISM_H