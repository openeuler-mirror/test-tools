# 上游社区issue抓取工具

## 配置yaml
### 参数说明
- issue
  - status: issue的状态（open or closed）
- platforms
  - platform
    - name: 平台名称,当前只支持github和gitlab
    - url:　平台的链接地址
    - object：　平台下项目
      - account: 用户空间名称
      - repository: 仓库名称

### 配置说明
- platforms下可以存在多个平台，同一个平台不需要重复出现
- object下面可以存在多个仓库，但是空间名称和仓库名必须一一对应

## 使用说明

### 环境准备

- 安装python3
- 为了更好的管理项目，建议使用venv:`python3 -m venv venv && source venv/bin/active`
- 执行命令`pip install -r requirements.txt`安装依赖模块

### 执行脚本
    ```
    python3 issue-scouter.py
    ```