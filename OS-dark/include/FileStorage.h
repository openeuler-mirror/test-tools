// FileStorage.h
#ifndef FILESTORAGE_H
#define FILESTORAGE_H

#include <string>

class FileStorage {
public:
    void store(const std::string& data, const std::string& filePath, bool append);
    std::string retrieve(const std::string& filePath);
};

#endif // FILESTORAGE_H