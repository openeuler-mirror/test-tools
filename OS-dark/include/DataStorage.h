// DataStorage.h
#ifndef DATASTORAGE_H
#define DATASTORAGE_H

#include <string>

class DataStorage {
public:
    virtual void storeData(const std::string& data) = 0;
    virtual std::string retrieveData() = 0;
};

#endif // DATASTORAGE_H