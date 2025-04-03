#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include "DataAnalyzer.h"
#include <fstream>
#include <sstream>

using ::testing::_;
using ::testing::Return;
using ::testing::SetArgPointee;
using ::testing::DoAll;

class MockDataAnalyzer : public DataAnalyzer {
public:
    MOCK_METHOD(std::string, readFromPersistentMemory, (const std::string&), (override));
};

TEST(DataAnalyzerTest, ReadFromPersistentMemory_FileOpenFailed) {
    DataAnalyzer analyzer;
    std::string result = analyzer.readFromPersistentMemory("nonexistent_file.log");
    EXPECT_EQ(result, "");
}

TEST(DataAnalyzerTest, ReadFromPersistentMemory_FileSizeFailed) {
    // Mock the file open to succeed but fstat to fail
    // This requires mocking system calls, which is complex and not shown here
    // For simplicity// DataAnalyzer_test.cpp
#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include "DataAnalyzer.h"
#include <fstream>
#include <sstream>
#include <cstdio>

using ::testing::_;
using ::testing::Return;

class MockDataAnalyzer : public DataAnalyzer {
public:
    MOCK_METHOD(std::string, readFromPersistentMemory, (const std::string&), (override));
};

// 测试读取持久化内存的基础场景
TEST(DataAnalyzerTest, ReadValidPersistentMemory) {
    // 创建临时测试文件
    const std::string test_file = "test_mem.log";
    std::ofstream ofs(test_file);
    ofs << "Sample data line with ERROR\nAnother WARNING line";
    ofs.close();

    DataAnalyzer analyzer;
    std::string result = analyzer.readFromPersistentMemory(test_file);
    
    EXPECT_FALSE(result.empty());
    EXPECT_EQ(result, "Sample data line with ERROR\nAnother WARNING line");
    
    // 清理测试文件
    std::remove(test_file.c_str());
}

// 测试analyze方法的基础功能
TEST(DataAnalyzerTest, AnalyzeBasicFunction) {
    MockDataAnalyzer analyzer;
    
    // 设置持久化内存模拟数据
    std::string mock_persistent_data = 
        "ERROR: Disk failure\n"
        "WARNING: High temperature\n"
        "ERROR: Network timeout";
    
    // 设置模拟返回
    EXPECT_CALL(analyzer, readFromPersistentMemory(_))
        .WillOnce(Return(mock_persistent_data));

    // 测试输入数据
    std::string input_data = 
        "WARNING: CPU overload\n"
        "ERROR: Memory leak";
    
    testing::internal::CaptureStdout();
    analyzer.analyze(input_data);
    std::string output = testing::internal::GetCapturedStdout();

    // 验证统计结果
    EXPECT_TRUE(output.find("Disk failure - Count: 1") != std::string::npos);
    EXPECT_TRUE(output.find("Network timeout - Count: 1") != std::string::npos);
    EXPECT_TRUE(output.find("High temperature - Count: 1") != std::string::npos);
    EXPECT_TRUE(output.find("CPU overload - Count: 1") != std::string::npos);
    EXPECT_TRUE(output.find("Memory leak - Count: 1") != std::string::npos);
}

// 测试空数据场景
TEST(DataAnalyzerTest, HandleEmptyData) {
    MockDataAnalyzer analyzer;
    EXPECT_CALL(analyzer, readFromPersistentMemory(_))
        .WillOnce(Return(""));
    
    testing::internal::CaptureStdout();
    analyzer.analyze("");
    std::string output = testing::internal::GetCapturedStdout();
    
    EXPECT_TRUE(output.find("No data to analyze") != std::string::npos);
}

// 测试文件操作失败场景
TEST(DataAnalyzerTest, HandleFileOperationsFailure) {
    DataAnalyzer analyzer;
    
    // 测试不存在的文件
    std::string result = analyzer.readFromPersistentMemory("non_existent_file.mem");
    EXPECT_TRUE(result.empty());
    
    // 测试无权限文件（需要提前创建）
    // std::ofstream("no_permission.log").close();
    // chmod("no_permission.log", 0000);
    // EXPECT_TRUE(analyzer.readFromPersistentMemory("no_permission.log").empty());
    // chmod("no_permission.log", 0644); // 恢复权限
}

// 测试错误/警告消息边界情况
TEST(DataAnalyzerTest, HandleEdgeCases) {
    MockDataAnalyzer analyzer;
    EXPECT_CALL(analyzer, readFromPersistentMemory(_))
        .WillOnce(Return("PARTIAL_ERROR"));
    
    testing::internal::CaptureStdout();
    analyzer.analyze("ERROR\nWARNING");
    std::string output = testing::internal::GetCapturedStdout();
    
    // 验证部分匹配
    EXPECT_TRUE(output.find("PARTIAL_ERROR - Count: 1") != std::string::npos);
    EXPECT_TRUE(output.find("ERROR - Count: 1") != std::string::npos);
    EXPECT_TRUE(output.find("WARNING - Count: 1") != std::string::npos);
}
