# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++11 -g

# Source files
SRCS = src/dark.cpp \
       src/DataAnalyzer.cpp \
       src/FileStorage.cpp \
       src/KernelCrashDetector.cpp \
       src/ProcessStatusCollector.cpp \
       src/ReportGenerator.cpp \
       src/SystemLogCollector.cpp

# Test source files
TEST_SRCS = TEST/TriggerMechanismTest.cpp \
            TEST/ReportGeneratorTest.cpp \
            TEST/KernelCrashDetectorTest.cpp \
            TEST/FileStorageTest.cpp \
            TEST/DataAnalyzerTest.cpp

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
	$(CXX) $(CXXFLAGS) -o $@ $^

# Link test object files to create the test executable
$(TEST_EXEC): $(OBJS) $(TEST_OBJS) $(GTEST_LIB) $(GTEST_MAIN_LIB)
	$(CXX) $(CXXFLAGS) -o $@ $^ -lpthread

# Compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up
clean:
	rm -f $(OBJS) $(TEST_OBJS) $(EXEC) $(TEST_EXEC)

.PHONY: all clean