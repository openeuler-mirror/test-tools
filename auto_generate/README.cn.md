# AI自动生成测试用例使用说明

## 1. 简介

AI自动生成测试用例是一个基于Python的自动化测试工具，它可以根据用户提供的测试用例模板和测试框架命令自动生成软件包的测试脚本、测试用例md。

## 2. 功能

目录结构：

```
mugen
├── auto_generate       # auto_generate必须放在mugen框架下使用
    ├── README.cn.md    # 中文说明文档
    ├── generate_test_cases  # 存放生成的测试用例
    ├── script.py       # 生成测试用例脚本主函数
    ├── config.py       # 配置文件
    ├── llm.py          # 调用大模型接口
    ├── prompt.py       # 大模型prompt
    ├── requirements.txt # 依赖库
    ├── .env            # 配置文件
    ├── tmp             # 存放测试脚本执行时环境中已有的数据
        ├── common      # 测试环境中已有的数据，通常是测试脚本需要的文件
        └── note.md     # 描述环境的信息
```

## 2. 使用方法

### 2.1 配置.env

在auto_gerenate目录下，配置.env文件，其中包括大模型地址：

```
LLM_URL=http://xxx.xxx.xxx.xxx:8008/v1
LLM_KEY=none
LLM_MODEL_NAME=Qwen2.5-14B-Instruct
```
### 2.2 安装ccb
参考以下链接，安装ccb，ccb可以帮助检索软件包的二进制包
https://gitee.com/openeuler/docs/blob/stable2-22.03_LTS_SP2/docs/zh/docs/EulerMaker/EulerMaker%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97.md#5%E5%9F%BA%E4%BA%8E%E5%91%BD%E4%BB%A4%E8%A1%8C%E8%BF%9B%E8%A1%8C%E6%9E%84%E5%BB%BA

安装ccb过程中，可能出现的问题：
报错1：
<internal:/usr/share/rubygems/rubygems/core_ext/kernel_require.rb>:85:in `require': cannot load such file -- rest-client (LoadError)
解决方法1：
gem uninstall securerandom 卸载掉0.4.*版本的securerandom
gem install -f securerandom:0.3.2 安装0.3.2版本的securerandom

报错2：
/usr/libexec/ccb-1.0/sbin/cli/ccb_common.rb:147:in `load_jwt?': undefined method `strip' for nil:NilClass (NoMethodError)
解决方法2：
vi ~/.config/cli/defaults/config.yaml 在以下两个配置随便填写一个账号密码，保证不为空即可
ACCOUNT: 
PASSWORD:
### 2.3 配置tmp

在auto_gerenate目录下，配置tmp目录，其中包括测试脚本执行时环境中已有的数据，common下通常是软件包测试脚本需要的文件，note.md是对环境信息的描述，可以让大模型知道环境中有哪些已准备好的文件，可以改善生成脚本的准确度
例如assimp测试时：

```
tmp
├── common
│   └──  test.obj.tar # assimp软件包所需测试文件
└── note.md # 描述环境的信息
```

note.md

```
环境中已存在common/test.obj.tar,解压后是一个test/1.obj的文件
```

### 2.4 命令

```
python auto_generate/script.py -m=[mode] -n=[package_name]
```

参数说明：

- mode：模式，shell、md
  1. shell模式：根据{package_name}生成测试脚本和测试套到generate_test_cases目录下
  2. md模式：根据generate_test_cases目录下的测试用例脚本转换成md文档，需要将脚本放在generate_test_cases/{package_name}下
- package_name：需要生成的软件包名

示例：
生成脚本：
python auto_generate/script.py -m=shell -n=attr
会在generate_test_cases目录下生成attr目录，attr目录下有attr.sh、attr.json文件

生成md：
在generate_test_cases目录下放好attr目录，attr目录下有attr.sh、attr.json文件
python auto_generate/script.py -m=md -n=attr
会在generate_test_cases目录下生成attr的各个测试脚本的md
