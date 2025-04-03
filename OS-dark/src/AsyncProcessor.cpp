#include "AsyncProcessor.h"
#include <iostream>

AsyncProcessor& AsyncProcessor::getInstance() {
    static AsyncProcessor instance;
    return instance;
}

AsyncProcessor::AsyncProcessor() : stop_(false), activeThreads_(0) {
}

AsyncProcessor::~AsyncProcessor() {
    stop();
}

void AsyncProcessor::start(size_t numThreads) {
    // 如果已经有工作线程，则不重复启动
    if (!workers_.empty()) {
        return;
    }
    
    // 创建工作线程
    for (size_t i = 0; i < numThreads; ++i) {
        workers_.emplace_back(&AsyncProcessor::workerThread, this);
    }
}

void AsyncProcessor::stop() {
    {
        std::unique_lock<std::mutex> lock(queueMutex_);
        stop_ = true;
    }
    
    // 通知所有等待的线程
    condition_.notify_all();
    
    // 等待所有工作线程结束
    for (auto& worker : workers_) {
        if (worker.joinable()) {
            worker.join();
        }
    }
    
    // 清空工作线程列表
    workers_.clear();
}

void AsyncProcessor::waitForAll() {
    // 等待队列为空且没有活动线程
    while (true) {
        std::unique_lock<std::mutex> lock(queueMutex_);
        if (tasks_.empty() && activeThreads_ == 0) {
            break;
        }
        
        // 释放锁并等待一段时间
        lock.unlock();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

size_t AsyncProcessor::getQueueSize() const {
    std::unique_lock<std::mutex> lock(queueMutex_);
    return tasks_.size();
}

size_t AsyncProcessor::getActiveThreadCount() const {
    return activeThreads_;
}

void AsyncProcessor::workerThread() {
    while (true) {
        std::unique_ptr<TaskBase> task;
        
        {
            std::unique_lock<std::mutex> lock(queueMutex_);
            
            // 等待任务或停止信号
            condition_.wait(lock, [this] {
                return stop_ || !tasks_.empty();
            });
            
            // 如果收到停止信号且队列为空，则退出
            if (stop_ && tasks_.empty()) {
                return;
            }
            
            // 获取任务
            task = std::move(tasks_.front());
            tasks_.pop();
        }
        
        // 执行任务
        ++activeThreads_;
        try {
            task->execute();
        } catch (const std::exception& e) {
            std::cerr << "Exception in worker thread: " << e.what() << std::endl;
        } catch (...) {
            std::cerr << "Unknown exception in worker thread" << std::endl;
        }
        --activeThreads_;
    }
} 