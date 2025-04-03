#include "FileStorage.h"
#include <fstream>
#include <iostream>
#include <string>

void FileStorage::store(const std::string& data, const std::string& filePath, bool append) {
    std::ios_base::openmode mode = append ? std::ios::app : std::ios::out;
    std::ofstream file(filePath, mode);
    if (file.is_open()) {
        file << data;
        if (file.fail()) {
            std::cerr << "Failed to write data to file: " << filePath << std::endl;
        } else {
            std::cout << "Stored data to file: " << filePath << std::endl;
        }
        file.close();
    } else {
        std::cerr << "Unable to open file for storing data: " << filePath << std::endl;
    }
}

std::string FileStorage::retrieve(const std::string& filePath) {
    std::ifstream file(filePath);
    std::string data;
    if (file.is_open()) {
        std::getline(file, data, '\0'); // Read the entire file content
        if (file.fail()) {
            std::cerr << "Failed to read data from file: " << filePath << std::endl;
            data.clear();
        } else {
            std::cout << "Retrieved data from file: " << filePath << std::endl;
        }
        file.close();
    } else {
        std::cerr << "Unable to open file for retrieving data: " << filePath << std::endl;
    }
    return data;
}