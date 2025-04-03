# OS Dark

## 项目描述
OS Dark 是一个用于监控和分析操作系统状态的工具。它可以检测系统重启、内核崩溃、内存不足、磁盘空间不足、网络连接问题等事件，并生成详细的系统报告和警报。

## 功能特点

- **系统状态监控**：收集系统日志、进程状态和内存使用情况
- **多种问题检测**：
  - 系统重启检测
  - 内核崩溃检测
  - 内存不足（OOM）检测
  - 磁盘空间不足检测
  - 网络连接问题检测
- **警报系统**：
  - 邮件警报通知
  - 多级警报（信息、警告、错误、严重）
  - 可配置的警报阈值
- **异步处理**：使用线程池进行异步数据收集和处理
- **可配置**：通过配置文件自定义检测参数和行为
- **模块化设计**：使用工厂模式和依赖注入，便于扩展
- **跨平台支持**：支持Windows和Linux/Unix系统

## 编译和运行

### 依赖项
- C++11 兼容的编译器（如 g++ 5.0+）
- pthread 库
- Google Test 库（仅用于测试）

### 编译
确保你已经安装了所需的依赖项，然后运行以下命令来编译项目：

```bash
make
```

编译测试：

```bash
make test
```

### 生成配置文件
生成默认配置文件：

```bash
make config
```

这将创建一个名为 `osdark.conf` 的配置文件。

### 运行
不使用配置文件运行（使用默认配置）：

```bash
make run
# 或者直接运行
./os_dark
```

使用配置文件运行：

```bash
make run-config
# 或者直接运行
./os_dark osdark.conf
```

## 配置选项

配置文件使用简单的键值对格式，分为以下几个部分：

### 磁盘空间设置
```
# 磁盘空间阈值（百分比）
disk_space_threshold = 85.0
```

### 网络设置
```
# 是否启用网络监控
network_monitoring_enabled = true
# 丢包率阈值（百分比）
network_packet_loss_threshold = 5.0
# 延迟阈值（毫秒）
network_latency_threshold = 100
# 测试目标（逗号分隔的IP地址列表）
network_test_targets = 8.8.8.8,1.1.1.1,208.67.222.222
```

### 日志设置
```
# 日志保留天数
log_retention_days = 30
# 日志目录
log_directory = /var/log/osdark
```

### 警报设置
```
# 是否启用邮件警报
enable_email_alerts = false
# 邮件接收者
email_recipient = admin@example.com
# 邮件发送者
email_sender = osdark@example.com
# SMTP服务器
smtp_server = smtp.example.com
# SMTP端口
smtp_port = 587
# 是否使用TLS
smtp_use_tls = true
```

### 通用设置
```
# 监控间隔（分钟）
monitoring_interval = 15
# 是否总是保存报告（即使没有检测到问题）
always_save_report = false
```

## 项目结构

- **include/**：头文件目录
  - 接口定义和数据结构
- **src/**：源代码目录
  - 具体实现
- **TEST/**：测试代码目录

## 扩展指南

### 添加新的检测器
1. 创建新的检测器类（如 `NetworkDetector.h` 和 `NetworkDetector.cpp`）
2. 在 `TriggerMechanism` 接口中添加新的检测方法
3. 在 `ConcreteTriggerMechanism` 中实现该方法
4. 在 `main.cpp` 中调用新的检测方法
5. 在 `Configuration` 中添加相关配置项
6. 在 `AlertManager` 中添加相应的警报类型

### 添加新的数据收集器
1. 创建新的收集器类
2. 在 `DataCollector` 接口中添加新的收集方法
3. 在 `ConcreteDataCollector` 中实现该方法

### 添加新的警报类型
1. 在 `AlertManager` 中添加新的警报级别或类型
2. 在 `createAlerts` 函数中添加新的警报创建逻辑
3. 如果需要，添加新的警报发送方式（如SMS、Slack等）

## 许可证
[MIT License](LICENSE)