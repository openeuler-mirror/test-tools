#include "NetworkDetector.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <regex>
#include <cstring>

#ifdef _WIN32
#include <winsock2.h>
#include <iphlpapi.h>
#include <ws2tcpip.h>
#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <netdb.h>
#include <unistd.h>
#endif

NetworkDetector::NetworkDetector(double packetLossThreshold, int latencyThreshold)
    : packetLossThreshold_(packetLossThreshold), latencyThreshold_(latencyThreshold) {
}

bool NetworkDetector::detect() {
    std::vector<NetworkInterface> interfaces = getAllInterfaces();
    bool networkIssueDetected = false;
    
    for (const auto& interface : interfaces) {
        if (interface.isUp) {
            std::cout << "Testing network interface: " << interface.name << " (" << interface.ipAddress << ")" << std::endl;
            
            // 测试连接到默认网关和公共DNS服务器
            std::vector<std::string> testTargets = {"8.8.8.8", "1.1.1.1", "208.67.222.222"};
            
            for (const auto& target : testTargets) {
                double packetLoss;
                int latency;
                
                if (pingTest(target, packetLoss, latency)) {
                    std::cout << "  Ping to " << target << ": " 
                              << "Packet loss: " << packetLoss << "%, "
                              << "Latency: " << latency << "ms" << std::endl;
                    
                    if (packetLoss > packetLossThreshold_ || latency > latencyThreshold_) {
                        std::cout << "  Network issue detected on " << interface.name 
                                  << " when connecting to " << target << std::endl;
                        networkIssueDetected = true;
                    }
                } else {
                    std::cout << "  Failed to ping " << target << " from " << interface.name << std::endl;
                    networkIssueDetected = true;
                }
            }
        }
    }
    
    return networkIssueDetected;
}

std::vector<NetworkDetector::NetworkInterface> NetworkDetector::getAllInterfaces() {
    std::vector<NetworkInterface> interfaces;
    
#ifdef _WIN32
    // Windows实现
    ULONG bufferSize = 15000;
    PIP_ADAPTER_ADDRESSES pAddresses = (IP_ADAPTER_ADDRESSES*)malloc(bufferSize);
    
    if (pAddresses == nullptr) {
        std::cerr << "Memory allocation failed for IP_ADAPTER_ADDRESSES struct" << std::endl;
        return interfaces;
    }
    
    DWORD result = GetAdaptersAddresses(AF_INET, GAA_FLAG_INCLUDE_PREFIX, nullptr, pAddresses, &bufferSize);
    
    if (result == ERROR_BUFFER_OVERFLOW) {
        free(pAddresses);
        pAddresses = (IP_ADAPTER_ADDRESSES*)malloc(bufferSize);
        
        if (pAddresses == nullptr) {
            std::cerr << "Memory allocation failed for IP_ADAPTER_ADDRESSES struct" << std::endl;
            return interfaces;
        }
        
        result = GetAdaptersAddresses(AF_INET, GAA_FLAG_INCLUDE_PREFIX, nullptr, pAddresses, &bufferSize);
    }
    
    if (result == NO_ERROR) {
        PIP_ADAPTER_ADDRESSES pCurrent = pAddresses;
        while (pCurrent) {
            if (pCurrent->OperStatus == IfOperStatusUp) {
                PIP_ADAPTER_UNICAST_ADDRESS pUnicast = pCurrent->FirstUnicastAddress;
                while (pUnicast) {
                    if (pUnicast->Address.lpSockaddr->sa_family == AF_INET) {
                        NetworkInterface interface;
                        
                        // 转换宽字符到多字节
                        char name[256];
                        WideCharToMultiByte(CP_ACP, 0, pCurrent->FriendlyName, -1, name, sizeof(name), nullptr, nullptr);
                        interface.name = name;
                        
                        // 获取IP地址
                        sockaddr_in* sockaddr = reinterpret_cast<sockaddr_in*>(pUnicast->Address.lpSockaddr);
                        char ipStr[INET_ADDRSTRLEN];
                        inet_ntop(AF_INET, &(sockaddr->sin_addr), ipStr, INET_ADDRSTRLEN);
                        interface.ipAddress = ipStr;
                        
                        interface.isUp = true;
                        interface.packetLossRate = 0.0;
                        interface.latency = 0;
                        
                        interfaces.push_back(interface);
                    }
                    pUnicast = pUnicast->Next;
                }
            }
            pCurrent = pCurrent->Next;
        }
    } else {
        std::cerr << "GetAdaptersAddresses failed with error code: " << result << std::endl;
    }
    
    if (pAddresses) {
        free(pAddresses);
    }
#else
    // Linux/Unix实现
    struct ifaddrs* ifaddr;
    
    if (getifaddrs(&ifaddr) == -1) {
        std::cerr << "getifaddrs failed: " << strerror(errno) << std::endl;
        return interfaces;
    }
    
    for (struct ifaddrs* ifa = ifaddr; ifa != nullptr; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == nullptr) {
            continue;
        }
        
        // 只处理IPv4地址
        if (ifa->ifa_addr->sa_family == AF_INET) {
            NetworkInterface interface;
            interface.name = ifa->ifa_name;
            
            // 获取IP地址
            char ipStr[INET_ADDRSTRLEN];
            struct sockaddr_in* addr = (struct sockaddr_in*)ifa->ifa_addr;
            inet_ntop(AF_INET, &addr->sin_addr, ipStr, INET_ADDRSTRLEN);
            interface.ipAddress = ipStr;
            
            // 检查接口是否启用
            interface.isUp = (ifa->ifa_flags & IFF_UP) && (ifa->ifa_flags & IFF_RUNNING);
            interface.packetLossRate = 0.0;
            interface.latency = 0;
            
            interfaces.push_back(interface);
        }
    }
    
    freeifaddrs(ifaddr);
#endif
    
    return interfaces;
}

NetworkDetector::NetworkInterface NetworkDetector::testInterface(const std::string& interfaceName) {
    auto interfaces = getAllInterfaces();
    
    for (auto& interface : interfaces) {
        if (interface.name == interfaceName) {
            // 测试连接到默认网关和公共DNS服务器
            std::vector<std::string> testTargets = {"8.8.8.8", "1.1.1.1"};
            double totalPacketLoss = 0.0;
            int totalLatency = 0;
            int successfulTests = 0;
            
            for (const auto& target : testTargets) {
                double packetLoss;
                int latency;
                
                if (pingTest(target, packetLoss, latency)) {
                    totalPacketLoss += packetLoss;
                    totalLatency += latency;
                    successfulTests++;
                }
            }
            
            if (successfulTests > 0) {
                interface.packetLossRate = totalPacketLoss / successfulTests;
                interface.latency = totalLatency / successfulTests;
            } else {
                interface.packetLossRate = 100.0;
                interface.latency = 0;
            }
            
            return interface;
        }
    }
    
    // 如果找不到指定的接口，返回一个空接口
    NetworkInterface emptyInterface;
    emptyInterface.name = interfaceName;
    emptyInterface.isUp = false;
    emptyInterface.packetLossRate = 0.0;
    emptyInterface.latency = 0;
    
    return emptyInterface;
}

bool NetworkDetector::pingTest(const std::string& target, double& packetLoss, int& latency) {
    std::string pingCmd;
    std::string outputFile = "ping_output.txt";
    
#ifdef _WIN32
    // Windows ping命令
    pingCmd = "ping -n 5 " + target + " > " + outputFile + " 2>&1";
#else
    // Linux/Unix ping命令
    pingCmd = "ping -c 5 " + target + " > " + outputFile + " 2>&1";
#endif
    
    int result = std::system(pingCmd.c_str());
    
    if (result != 0) {
        packetLoss = 100.0;
        latency = 0;
        return false;
    }
    
    std::ifstream file(outputFile);
    if (!file.is_open()) {
        std::cerr << "Failed to open ping output file" << std::endl;
        packetLoss = 100.0;
        latency = 0;
        return false;
    }
    
    std::string line;
    packetLoss = 100.0;
    latency = 0;
    
#ifdef _WIN32
    // 解析Windows ping输出
    std::regex lossPattern("\\(([0-9]+)% loss\\)");
    std::regex latencyPattern("Average = ([0-9]+)ms");
    
    while (std::getline(file, line)) {
        std::smatch match;
        
        if (std::regex_search(line, match, lossPattern) && match.size() > 1) {
            packetLoss = std::stod(match[1].str());
        }
        
        if (std::regex_search(line, match, latencyPattern) && match.size() > 1) {
            latency = std::stoi(match[1].str());
        }
    }
#else
    // 解析Linux/Unix ping输出
    std::regex lossPattern("([0-9\\.]+)% packet loss");
    std::regex latencyPattern("rtt min/avg/max/mdev = [0-9\\.]+/([0-9\\.]+)/[0-9\\.]+/[0-9\\.]+ ms");
    
    while (std::getline(file, line)) {
        std::smatch match;
        
        if (std::regex_search(line, match, lossPattern) && match.size() > 1) {
            packetLoss = std::stod(match[1].str());
        }
        
        if (std::regex_search(line, match, latencyPattern) && match.size() > 1) {
            latency = std::stoi(match[1].str());
        }
    }
#endif
    
    file.close();
    
    // 删除临时文件
    std::remove(outputFile.c_str());
    
    return true;
}

void NetworkDetector::setPacketLossThreshold(double threshold) {
    packetLossThreshold_ = threshold;
}

void NetworkDetector::setLatencyThreshold(int threshold) {
    latencyThreshold_ = threshold;
} 