# OS Dark 系统设计文档

## 1. 系统概述

OS Dark 是一个用于监控和分析操作系统状态的工具，能够检测系统重启、内核崩溃、内存不足、磁盘空间不足、网络连接问题等事件，并生成详细的系统报告和警报。该工具采用模块化设计，支持跨平台（Windows 和 Linux/Unix），并提供异步处理和可配置的警报系统。

## 2. 系统架构

### 2.1 整体架构

OS Dark 采用组件化架构，主要由以下几个核心模块组成：

1. **数据收集模块**：负责收集系统日志、进程状态和内存使用情况
2. **问题检测模块**：负责检测系统重启、内核崩溃、内存不足、磁盘空间不足和网络连接问题
3. **数据存储模块**：负责将收集的数据和生成的报告存储到文件系统
4. **警报管理模块**：负责生成和发送警报
5. **配置管理模块**：负责加载和管理系统配置
6. **异步处理模块**：提供线程池，支持异步任务执行

### 2.2 模块关系图

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
| 数据收集模块    |---->| 问题检测模块    |---->| 数据存储模块    |
|                |     |                |     |                |
+----------------+     +----------------+     +----------------+
                              |
                              v
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
| 配置管理模块    |<----| 警报管理模块    |<----| 异步处理模块    |
|                |     |                |     |                |
+----------------+     +----------------+     +----------------+
```

### 2.3 设计模式

OS Dark 采用了多种设计模式：

1. **工厂模式**：通过 `ComponentFactory` 创建各种组件
2. **单例模式**：`Configuration`、`AlertManager` 和 `AsyncProcessor` 采用单例模式
3. **策略模式**：不同的检测器实现不同的检测策略
4. **观察者模式**：警报系统实现了观察者模式，当检测到问题时通知观察者
5. **依赖注入**：通过构造函数注入依赖，提高代码的可测试性和灵活性

## 3. 核心模块详细设计

### 3.1 数据收集模块

#### 3.1.1 接口定义

```cpp
class DataCollector {
public:
    virtual ~DataCollector() = default;
    virtual void collectSystemLogs() = 0;
    virtual void collectProcessStatus() = 0;
    virtual void collectMemoryUsage() = 0;
    virtual std::vector<SystemLog> getSystemLogs() const = 0;
    virtual std::vector<ProcessStatus> getProcessStatuses() const = 0;
    virtual MemoryUsage getMemoryUsage() const = 0;
};
```

#### 3.1.2 主要实现类

- `ConcreteDataCollector`：实现 `DataCollector` 接口
- `SystemLogCollector`：收集系统日志
- `ProcessStatusCollector`：收集进程状态
- `MemoryUsageCollector`：收集内存使用情况

#### 3.1.3 数据结构

```cpp
struct SystemLog {
    std::string timestamp;
    std::string severity;
    std::string message;
};

struct ProcessStatus {
    int pid;
    std::string name;
    std::string state;
    int memoryUsage;
};

struct MemoryUsage {
    size_t usedMemory;
};
```

### 3.2 问题检测模块

#### 3.2.1 接口定义

```cpp
class TriggerMechanism {
public:
    virtual ~TriggerMechanism() = default;
    virtual bool detectSystemRestart() = 0;
    virtual bool detectKernelCrash() = 0;
    virtual bool detectOOM() = 0;
    virtual bool detectDiskSpaceLow() = 0;
    virtual bool detectNetworkIssues() = 0;
};
```

#### 3.2.2 主要实现类

- `ConcreteTriggerMechanism`：实现 `TriggerMechanism` 接口
- `SystemRestartDetector`：检测系统重启
- `KernelCrashDetector`：检测内核崩溃
- `OOMDetector`：检测内存不足
- `DiskSpaceDetector`：检测磁盘空间不足
- `NetworkDetector`：检测网络连接问题

#### 3.2.3 网络检测器设计

`NetworkDetector` 类负责检测网络连接问题，支持 Windows 和 Linux/Unix 平台：

```cpp
class NetworkDetector {
public:
    struct NetworkInterface {
        std::string name;
        std::string ipAddress;
        bool isUp;
        double packetLossRate;
        int latency; // 毫秒
    };

    NetworkDetector(double packetLossThreshold = 5.0, int latencyThreshold = 100);
    
    // 检测网络连接问题
    bool detect();
    
    // 获取所有网络接口信息
    std::vector<NetworkInterface> getAllInterfaces();
    
    // 测试特定接口的连接性
    NetworkInterface testInterface(const std::string& interfaceName);
    
    // 设置阈值
    void setPacketLossThreshold(double threshold);
    void setLatencyThreshold(int threshold);
    
private:
    double packetLossThreshold_; // 丢包率阈值（百分比）
    int latencyThreshold_;       // 延迟阈值（毫秒）
    
    // 执行ping测试
    bool pingTest(const std::string& target, double& packetLoss, int& latency);
};
```

### 3.3 数据存储模块

#### 3.3.1 接口定义

```cpp
class DataStorage {
public:
    virtual void storeData(const std::string& data) = 0;
    virtual std::string retrieveData() = 0;
};
```

#### 3.3.2 主要实现类

- `FileStorage`：将数据存储到文件系统

### 3.4 警报管理模块

#### 3.4.1 接口定义

```cpp
class AlertManager {
public:
    enum class AlertLevel {
        INFO,
        WARNING,
        ERROR,
        CRITICAL
    };
    
    struct Alert {
        std::string title;
        std::string message;
        AlertLevel level;
        std::string timestamp;
    };
    
    static AlertManager& getInstance();
    
    // 添加警报
    void addAlert(const std::string& title, const std::string& message, AlertLevel level);
    
    // 发送邮件警报
    bool sendEmailAlert(const Alert& alert);
    
    // 发送所有未发送的警报
    bool sendAllPendingAlerts();
    
    // 获取所有警报
    std::vector<Alert> getAllAlerts() const;
    
    // 获取未发送的警报
    std::vector<Alert> getPendingAlerts() const;
    
    // 清除所有警报
    void clearAlerts();
};
```

#### 3.4.2 警报级别

- `INFO`：信息级别，一般性通知
- `WARNING`：警告级别，需要注意但不紧急
- `ERROR`：错误级别，需要及时处理
- `CRITICAL`：严重级别，需要立即处理

### 3.5 配置管理模块

#### 3.5.1 接口定义

```cpp
class Configuration {
public:
    static Configuration& getInstance();
    
    // 从文件加载配置
    bool loadFromFile(const std::string& filename);
    
    // 保存配置到文件
    bool saveToFile(const std::string& filename);
    
    // 获取配置值
    std::string getString(const std::string& key, const std::string& defaultValue = "") const;
    int getInt(const std::string& key, int defaultValue = 0) const;
    double getDouble(const std::string& key, double defaultValue = 0.0) const;
    bool getBool(const std::string& key, bool defaultValue = false) const;
    
    // 设置配置值
    void setString(const std::string& key, const std::string& value);
    void setInt(const std::string& key, int value);
    void setDouble(const std::string& key, double value);
    void setBool(const std::string& key, bool value);
};
```

#### 3.5.2 配置项分类

1. **磁盘空间设置**：磁盘空间阈值
2. **网络设置**：网络监控开关、丢包率阈值、延迟阈值、测试目标
3. **日志设置**：日志保留天数、日志目录
4. **警报设置**：邮件警报开关、邮件接收者、邮件发送者、SMTP服务器、SMTP端口、TLS开关
5. **通用设置**：监控间隔、报告保存策略

### 3.6 异步处理模块

#### 3.6.1 接口定义

```cpp
class AsyncProcessor {
public:
    static AsyncProcessor& getInstance();
    
    // 提交任务并获取future
    template<typename Func, typename... Args>
    auto submit(Func&& func, Args&&... args) 
        -> std::future<typename std::result_of<Func(Args...)>::type>;
    
    // 启动工作线程
    void start(size_t numThreads = std::thread::hardware_concurrency());
    
    // 停止所有工作线程
    void stop();
    
    // 等待所有任务完成
    void waitForAll();
    
    // 获取队列中的任务数量
    size_t getQueueSize() const;
    
    // 获取活动线程数量
    size_t getActiveThreadCount() const;
};
```

#### 3.6.2 线程池设计

- 使用 `std::thread` 创建工作线程
- 使用 `std::queue` 存储任务
- 使用 `std::mutex` 和 `std::condition_variable` 实现线程同步
- 使用 `std::future` 获取任务执行结果

## 4. 工作流程

### 4.1 主程序流程

1. 加载配置文件
2. 创建组件工厂
3. 启动异步处理器
4. 创建数据收集器、触发机制、数据存储和恢复模块
5. 异步收集系统数据
6. 检测系统问题
7. 生成系统报告
8. 如果检测到问题，创建警报并存储报告
9. 发送警报
10. 停止异步处理器

### 4.2 数据收集流程

1. 收集系统日志
2. 收集进程状态
3. 收集内存使用情况

### 4.3 问题检测流程

1. 检测系统重启
2. 检测内核崩溃
3. 检测内存不足
4. 检测磁盘空间不足
5. 检测网络连接问题

### 4.4 警报生成和发送流程

1. 根据检测到的问题创建警报
2. 设置警报级别和消息
3. 如果配置了自动发送，立即发送警报
4. 否则，将警报添加到待发送队列
5. 在主程序结束前发送所有未发送的警报

## 5. 跨平台支持

### 5.1 Windows 平台支持

- 使用 Windows API 获取网络接口信息
- 使用 Windows 命令行工具执行 ping 测试
- 使用 Windows 特定的文件系统 API

### 5.2 Linux/Unix 平台支持

- 使用 POSIX API 获取网络接口信息
- 使用 Linux/Unix 命令行工具执行 ping 测试
- 使用 POSIX 文件系统 API

## 6. 扩展性设计

### 6.1 添加新的检测器

1. 创建新的检测器类（如 `CPULoadDetector`）
2. 在 `TriggerMechanism` 接口中添加新的检测方法
3. 在 `ConcreteTriggerMechanism` 中实现该方法
4. 在 `main.cpp` 中调用新的检测方法
5. 在 `Configuration` 中添加相关配置项
6. 在 `AlertManager` 中添加相应的警报类型

### 6.2 添加新的数据收集器

1. 创建新的收集器类（如 `NetworkTrafficCollector`）
2. 在 `DataCollector` 接口中添加新的收集方法
3. 在 `ConcreteDataCollector` 中实现该方法

### 6.3 添加新的警报类型

1. 在 `AlertManager` 中添加新的警报级别或类型
2. 在 `createAlerts` 函数中添加新的警报创建逻辑
3. 如果需要，添加新的警报发送方式（如SMS、Slack等）

## 7. 性能考虑

### 7.1 异步处理

- 使用线程池进行异步数据收集和处理
- 避免阻塞主线程
- 提高系统响应性

### 7.2 资源使用

- 使用智能指针管理内存
- 避免不必要的数据复制
- 使用流式处理大量数据

### 7.3 配置优化

- 可配置的监控间隔
- 可配置的警报阈值
- 可配置的报告保存策略

## 8. 安全性考虑

### 8.1 数据安全

- 敏感数据加密存储
- 安全的文件操作
- 错误处理和异常捕获

### 8.2 网络安全

- 支持 TLS 加密的邮件发送
- 安全的网络连接测试
- 防止命令注入

## 9. 未来扩展方向

1. **Web 界面**：开发 Web 界面，实时显示系统状态
2. **分布式监控**：支持监控多台服务器
3. **机器学习**：使用机器学习预测系统问题
4. **更多警报渠道**：添加 SMS、Slack、Teams 等警报渠道
5. **插件系统**：支持通过插件扩展功能
6. **数据可视化**：提供数据可视化和趋势分析

## 10. 总结

OS Dark 是一个功能强大、可扩展的操作系统监控工具，采用模块化设计和多种设计模式，支持跨平台，提供异步处理和可配置的警报系统。通过持续改进和扩展，OS Dark 可以成为一个全面的系统监控解决方案。 