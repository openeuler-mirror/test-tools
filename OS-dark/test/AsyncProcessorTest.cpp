#include "AsyncProcessor.h"
#include "TaskBase.h"
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <memory>
#include <vector>

using ::testing::Return;
using ::testing::_;

// Mock Task for testing AsyncProcessor
class MockTask : public TaskBase {
public:
    MOCK_METHOD(void, execute, (), (override));
};

// Test cases for AsyncProcessor
TEST(AsyncProcessorTest, AddMultipleTasks) {
    AsyncProcessor& processor = AsyncProcessor::getInstance();
    processor.stop(); // Ensure processor is stopped before starting

    processor.start(2);
    MockTask mockTask1, mockTask2;
    EXPECT_CALL(mockTask1, execute()).Times(1);
    EXPECT_CALL(mockTask2, execute()).Times(1);

    processor.addTask(std::make_unique<MockTask>(mockTask1));
    processor.addTask(std::make_unique<MockTask>(mockTask2));

    EXPECT_EQ(processor.getQueueSize(), 2);

    processor.waitForAll();
    processor.stop();
}

TEST(AsyncProcessorTest, StopWithPendingTasks) {
    AsyncProcessor& processor = AsyncProcessor::getInstance();
    processor.stop(); // Ensure processor is stopped before starting

    processor.start(1);
    MockTask mockTask;
    EXPECT_CALL(mockTask, execute()).Times(0); // Expect task not to be executed

    processor.addTask(std::make_unique<MockTask>(mockTask));
    processor.stop();

    EXPECT_EQ(processor.getQueueSize(), 1);
}

TEST(AsyncProcessorTest, StartWithZeroThreads) {
    AsyncProcessor& processor = AsyncProcessor::getInstance();
    processor.stop(); // Ensure processor is stopped before starting

    processor.start(0);
    EXPECT_EQ(processor.getActiveThreadCount(), 0);

    MockTask mockTask;
    processor.addTask(std::make_unique<MockTask>(mockTask));

    EXPECT_EQ(processor.getQueueSize(), 1);

    processor.stop();
}

TEST(AsyncProcessorTest, RestartProcessor) {
    AsyncProcessor& processor = AsyncProcessor::getInstance();
    processor.stop(); // Ensure processor is stopped before starting

    processor.start(2);
    EXPECT_EQ(processor.getActiveThreadCount(), 2);

    processor.stop();
    EXPECT_EQ(processor.getActiveThreadCount(), 0);

    processor.start(2);
    EXPECT_EQ(processor.getActiveThreadCount(), 2);

    MockTask mockTask;
    EXPECT_CALL(mockTask, execute()).Times(1);

    processor.addTask(std::make_unique<MockTask>(mockTask));
    processor.waitForAll();

    processor.stop();
}
