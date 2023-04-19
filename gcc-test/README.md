### 目录介绍

gcc-test 存放gcc相关特性单元测试用例、测试套件、自动化测试脚本，可用于对gcc进行功能测试，主要针对优化特性测试以及对常用优化进行组合测试。

### 目录结构：

```
├── README.md 
└── g++_10.3 
    └── mul64

```

### 工具参数

g++_10.3：存放c++前端特性用例，使用deja框架调用自动化运行

### 使用示例：

g++_10.3 :

cp -r ~/gcc-test/g++_10.3/mul64  path_to_gcc_source_code/gcc/testsuite

cd path_to_gcc_source_code/gcc/testsuite

runtest --tools g++