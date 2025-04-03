# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++11 -g -pthread

# Include directory
INCLUDES = -I./include

# Source files
SRCS = src/main.cpp \
       src/DataAnalyzer.cpp \
       src/FileStorage.cpp \
       src/KernelCrashDetector.cpp \
       src/ProcessStatusCollector.cpp \
       src/ReportGenerator.cpp \
       src/SystemLogCollector.cpp \
       src/SystemRestartDetector.cpp \
       src/OOMDetector.cpp \
       src/MemoryUsageCollector.cpp \
       src/DiskSpaceDetector.cpp \
       src/NetworkDetector.cpp \
       src/Configuration.cpp \
       src/AsyncProcessor.cpp \
       src/AlertManager.cpp \
       src/DefaultComponentFactory.cpp

# Test source files
TEST_SRCS = TEST/TriggerMechanismTest.cpp \
            TEST/ReportGeneratorTest.cpp \
            TEST/KernelCrashDetectorTest.cpp \
            TEST/FileStorageTest.cpp \
            TEST/DataAnalyzerTest.cpp \
            TEST/DiskSpaceDetectorTest.cpp \
            TEST/NetworkDetectorTest.cpp \
            TEST/ConfigurationTest.cpp \
            TEST/AsyncProcessorTest.cpp \
            TEST/AlertManagerTest.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Test object files
TEST_OBJS = $(TEST_SRCS:.cpp=.o)

# Executable
EXEC = os_dark

# Test executable
TEST_EXEC = os_dark_tests

# Google Test library
GTEST_DIR = /usr/src/gtest
GTEST_LIB = $(GTEST_DIR)/lib/.libs/libgtest.a
GTEST_MAIN_LIB = $(GTEST_DIR)/lib/.libs/libgtest_main.a

# Default target
all: $(EXEC) $(TEST_EXEC)

# Link object files to create the executable
$(EXEC): $(OBJS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $^

# Link test object files to create the test executable
$(TEST_EXEC): $(OBJS) $(TEST_OBJS) $(GTEST_LIB) $(GTEST_MAIN_LIB)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $^ -lpthread

# Compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Clean up
clean:
	rm -f $(OBJS) $(TEST_OBJS) $(EXEC) $(TEST_EXEC)
	rm -f system_report_*.txt
	rm -f alert_*.eml

# Create a sample configuration file
config:
	@echo "# OS Dark Configuration File" > osdark.conf
	@echo "# Disk space settings" >> osdark.conf
	@echo "disk_space_threshold = 85.0" >> osdark.conf
	@echo "" >> osdark.conf
	@echo "# Network settings" >> osdark.conf
	@echo "network_monitoring_enabled = true" >> osdark.conf
	@echo "network_packet_loss_threshold = 5.0" >> osdark.conf
	@echo "network_latency_threshold = 100" >> osdark.conf
	@echo "network_test_targets = 8.8.8.8,1.1.1.1,208.67.222.222" >> osdark.conf
	@echo "" >> osdark.conf
	@echo "# Log settings" >> osdark.conf
	@echo "log_retention_days = 30" >> osdark.conf
	@echo "log_directory = /var/log/osdark" >> osdark.conf
	@echo "" >> osdark.conf
	@echo "# Alert settings" >> osdark.conf
	@echo "enable_email_alerts = false" >> osdark.conf
	@echo "email_recipient = admin@example.com" >> osdark.conf
	@echo "email_sender = osdark@example.com" >> osdark.conf
	@echo "smtp_server = smtp.example.com" >> osdark.conf
	@echo "smtp_port = 587" >> osdark.conf
	@echo "smtp_use_tls = true" >> osdark.conf
	@echo "" >> osdark.conf
	@echo "# General settings" >> osdark.conf
	@echo "monitoring_interval = 15" >> osdark.conf
	@echo "always_save_report = false" >> osdark.conf
	@echo "Created sample configuration file: osdark.conf"

# Run the program with default configuration
run:
	./$(EXEC)

# Run the program with a specific configuration file
run-config:
	./$(EXEC) osdark.conf

.PHONY: all clean config run run-config