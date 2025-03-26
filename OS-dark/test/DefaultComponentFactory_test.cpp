#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include "ComponentFactory.h"
#include "SystemLogCollector.h"
#include "Configuration.h"

// Mock classes
class MockSystemLogCollector : public SystemLogCollector {
public:
    MOCK_METHOD(void, collect, (std::vector<SystemLog>&), (override));
};

class MockSystemRestartDetector : public SystemRestartDetector {
public:
    MOCK_METHOD(bool, detect, (), (override));
};

class TestConfiguration : public Configuration {
public:
    static TestConfiguration& getTestInstance() {
        static TestConfiguration instance;
        return instance;
    }
    
    void setDouble(const std::string& key, double value) { doubles_[key] = value; }
    double getDouble(const std::string& key, double def) override {
        return doubles_.count(key) ? doubles_[key] : def;
    }

private:
    std::map<std::string, double> doubles_;
};

// Tests for DefaultComponentFactory
TEST(ComponentFactoryTest, CreateDataCollector) {
    DefaultComponentFactory factory;
    auto collector = factory.createDataCollector();
    ASSERT_NE(dynamic_cast<ConcreteDataCollector*>(collector.get()), nullptr);
}

// Tests for ConcreteDataCollector
class DataCollectorTest : public ::testing::Test {
protected:
    void SetUp() override {
        mockLogCollector_ = std::make_shared<MockSystemLogCollector>();
        mockProcessCollector_ = std::make_shared<MockProcessStatusCollector>();
        mockMemoryCollector_ = std::make_shared<MockMemoryUsageCollector>();
        
        dataCollector_ = std::make_shared<ConcreteDataCollector>(
            mockLogCollector_, mockProcessCollector_, mockMemoryCollector_);
    }

    std::shared_ptr<MockSystemLogCollector> mockLogCollector_;
    std::shared_ptr<MockProcessStatusCollector> mockProcessCollector_;
    std::shared_ptr<MockMemoryUsageCollector> mockMemoryCollector_;
    std::shared_ptr<ConcreteDataCollector> dataCollector_;
};

TEST_F(DataCollectorTest, CollectSystemLogs) {
    std::vector<SystemLog> dummyLogs{{"2023-01-01", "System OK"}};
    
    EXPECT_CALL(*mockLogCollector_, collect(testing::_))
        .WillOnce(testing::SetArgReferee<0>(dummyLogs));
    
    dataCollector_->collectSystemLogs();
    ASSERT_EQ(dataCollector_->getSystemLogs().size(), 1);
}

// Tests for ConcreteTriggerMechanism
class TriggerMechanismTest : public ::testing::Test {
protected:
    void TearDown() override {
        TestConfiguration::getTestInstance().clear();
    }
};

TEST_F(TriggerMechanismTest, DetectDiskSpaceWithCustomThreshold) {
    auto& config = TestConfiguration::getTestInstance();
    config.setDouble("disk_space_threshold", 90.0);

    ConcreteTriggerMechanism trigger;
    testing::NiceMock<MockDiskSpaceDetector> mockDetector(90.0);
    
    EXPECT_CALL(mockDetector, detect())
        .WillOnce(testing::Return(true));
    
    ASSERT_TRUE(trigger.detectDiskSpaceLow());
}

// Tests for ConcreteRecoveryModule
TEST(RecoveryModuleTest, GenerateReport) {
    MockReportGenerator mockGenerator;
    ConcreteRecoveryModule recovery;
    
    EXPECT_CALL(mockGenerator, generate())
        .Times(1);
    
    recovery.generateReport();
}
