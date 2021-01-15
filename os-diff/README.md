### 工具介绍

os-diff用来对比两个源里面rpm包的差异，可进行全量，列表，单包对比，结果以html格式进行展示，目前实现以下对比：
- packages add & delete
- base info
- change logs
- provide functions
- require packages

### 目录结构：

```
├── os-diff.sh 
├── README.md 
└── rpmlist 
    ├── common 
    │   ├── index.html 
    │   └── rpm_list.html 
    ├── func 
    │   ├── rpmdiff.py 
    │   ├── rpminfo.sh 
    │   └── venv
    └── rpmlist.sh 
```

### 工具参数

-a: 对比所有包（yum源地址以及本地目录）

-l <list_file>: 对比指定列表文件里的包

-s <old package>: 指定rpm包1，地址或本地完整路径

-S <new package>: 指定rpm包2，地址或本地完整路径

-p <old path>: 包存放的目录1，绝对路径或相对路径

-P <new path>: 包存放的目录2

-r <old url>: repo源１，远端url或本地源

-R <new url>: repo源２

### 使用示例：

对比两个repo源的所有包：sh os-diff.sh -a -r old_url -R new_url

对比两个本地目录内的所有包：sh os-diff.sh -a -p old_dir -P new_dir

对比两个url中指定列表的包：sh os-diff.sh -l list_file -r old_url -R new_url

对比单包：sh os-diff.sh -s old_pkg -S old_pkg

### 需要安装的包
- python文件需要安装　python3-lxml

### 自定义list文件说明
某些源或者目录里存在同一个包的不同版本，在全量对比的时候，默认对比最新的包；
指定的list可以写三列（version为完整版本号）：
pkg_name    version1    version2

version1 指定old_url中的版本
version2 指定new_url中的版本
不指定默认选取最新版本
