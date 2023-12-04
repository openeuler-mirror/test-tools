# EBS_Web_test

#### 介绍
Test for EBS Web
- Config目录项存放的是web相关的基础配置项
- Lib目录存放的是公共函数
- Page目录存放的是对应网页的基础元素
- TestCase目录存放的是测试用例



### 使用教程
1.在Config/config.json文件中配置相应的URL地址、登录所需的账号密码，以及相关配置项(全局变量)
```
{
    "basic_url": "xxxxxx",
    "user_name": "xxx",
    "password": "xxxx",
}
```
2.运行run.py文件
