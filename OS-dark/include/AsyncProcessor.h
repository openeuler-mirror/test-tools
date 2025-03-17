// AsyncProcessor.h
#ifndef ASYNCPROCESSOR_H
#define ASYNCPROCESSOR_H

#include <future>
#include <functional>
#include <vector>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>

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
    
private:
    AsyncProcessor();
    ~AsyncProcessor();
    AsyncProcessor(const AsyncProcessor&) = delete;
    AsyncProcessor& operator=(const AsyncProcessor&) = delete;
    
    // 工作线程函数
    void workerThread();
    
    // 任务基类
    class TaskBase {
    public:
        virtual ~TaskBase() = default;
        virtual void execute() = 0;
    };
    
    // 具体任务类型
    template<typename Func>
    class Task : public TaskBase {
    public:
        Task(Func&& func) : func_(std::forward<Func>(func)) {}
        
        void execute() override {
            func_();
        }
        
    private:
        Func func_;
    };
    
    std::vector<std::thread> workers_;
    std::queue<std::unique_ptr<TaskBase>> tasks_;
    
    mutable std::mutex queueMutex_;
    std::condition_variable condition_;
    std::atomic<bool> stop_;
    std::atomic<size_t> activeThreads_;
};

// 模板方法实现
template<typename Func, typename... Args>
auto AsyncProcessor::submit(Func&& func, Args&&... args) 
    -> std::future<typename std::result_of<Func(Args...)>::type> {
    
    using ReturnType = typename std::result_of<Func(Args...)>::type;
    
    // 创建一个packaged_task，它将在执行时调用func
    auto task = std::make_shared<std::packaged_task<ReturnType()>>(
        std::bind(std::forward<Func>(func), std::forward<Args>(args)...)
    );
    
    // 获取future
    std::future<ReturnType> result = task->get_future();
    
    {
        std::unique_lock<std::mutex> lock(queueMutex_);
        
        // 将任务添加到队列
        tasks_.emplace(new Task<std::function<void()>>([task]() {
            (*task)();
        }));
    }
    
    // 通知一个等待的线程
    condition_.notify_one();
    
    return result;
}

#endif // ASYNCPROCESSOR_H 