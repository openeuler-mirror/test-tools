# mugen

## mugen介绍

mugen是openEuler社区开放的测试框架，提供公共配置和方法以便社区开发者进行测试代码的编写和执行

## mugen使用说明

用户对mugen框架的使用是通过执行mugen.sh接口来实现(兼容原有的runoet.sh,并保留)。接口详细说明如下：

- 参数说明：  
\-c: 测试环境配置
\-d: 下载openEuler社区开源的测试脚本
\-a：执行所有的测试用例  
\-f：指定测试套执行  
\-r：指定测试套下测试用例的执行，当前支持单用例  
\-C: 不去检测用例名和测试套映射文件的对应关系
\-x：进入调试模式下执行测试用例  

- 使用示例
  - 配置测试环境  
    `bash mugen.sh -c $ip $user $password`
  - 下载openEuler社区开源测试脚本  
    `bash muge.sh -d`
  - 执行所有用例  
    - 正常模式
      `bash mugen.sh -a`
    - 调试模式
      `bash mugen.sh -xa`
  - 执行指定测试套下所有用例  
    - 正常模式
      `bash mugen.sh -f "xxx"`
    - 调试模式
      `bash mugen.sh -xf "xxx"`
  - 执行指定的用例  
    - 正常模式
      `bash mugen.sh -f "xxx" -Cr "yyy"`
    - 正常模式且不检测映射文件
    - 调试模式
      `bash mugen.sh -xf "xxx" -r "yyy"`
    - 调试模式且不检测映射文件
      `bash mugen.sh -xf "xxx" -Cr "yyy"`

- 使用说明
  - 测试用例执行之前必须先配置环境变量
  - 所有的测试用例存放在testcases目录下
  - 测试套和测试用例的对应关系需要在suite2cases目录中进行定义
  - <font color="#660000">大家可以参考现有的测试模板进行用例开发</font>

- 框架目录  
&#160;&#160;![mugen_tree](data:image/png;base64,)

- mugen框架的生成的环境变量说明
  - 配置文件路径
    - 如果/etc/mugen/不存在,则路径为${OET_PATH}/conf
  - 配置文件内容
    - NODE:　测试环境节点
    - LOCALTION:　测试环境的本地　ＯＲ　远端
    - USER:　测试环境节点的用户
    - PASSWORD:　测试环境节点的用户密码
    - MACHINE:　虚拟机　ＯＲ　物理机
    - FRAME:　系统架构
    - NICS: 网卡名       (变量为数组)
    - MAC: 网卡对应的mac地址(变量为数组)
    - IPV4:　ip v4 地址　(变量为数组)
    - IPV6:　ip v6 地址　(变量为数组)
  - 环境变量名
    - NODE1_LOCATION、NODE2_LOCATION
    - NODE1_USER、NODE2_USER
    - NODE1_PASSWORD、NODE2_PASSWORD
    - NODE1_MACHINE、NODE2_MACHINE
    - NODE1_FRAME、NODE2_FRAME
    - NODE1_NICS、NODE2_NICS
    - NODE1_MAC、NODE2_MAC
    - NODE1_IPV4、NODE2_IPV4
    - NODE1_IPV6、NODE2_IPV6
  - <font color="#660000">PS: 使用者可以根据实际情况在env.conf中定义全局变量</font>

## mugen框架中shell公共方法

- SSH_CMD
  - 对ssh进行封装，远程执行命令时无需进入交互模式
  - 使用方法  
  `SSH_CMD "$cmd" $REMOTEIP $REMOTEPASSWD $REMOTEUSER`

- SSH_SCP
  - 对scp进行封装，执行scp命令时无需进入交互模式
  - 使用方法
    - 本地文件传输到远端  
    `SSH_SCP $local_path/$file $REMOTE_USER@$REMOTE_IP:$remote_path "$REMOTE_PASSWD"`
    - 远端文件传输到本地  
    `SSH_SCP $REMOTE_USER@$REMOTE_IP:$remote_path/$file $local_path "$REMOTE_PASSWD"`

- LOG_INFO
  - 输出INFO级日志  
  `LOG_INFO $log`
  
- LOG_WARN
  - 输出WARN级日志  
  `LOG_WARN $log`

- LOG_ERROR
  - 输出ERROR级日志  
  `LOG_WARN $log`

- DNF_INSTALL
  - 用于安装软件包  
  `DNF_INSTALL "vim bc nettools"`
  - 特别说明：建议需要安装的软件包，在前置处理中一次性安装完成

- DNF_REMOVE
  - 用于卸载软件包
  - 特别说明：依赖于 DNF_INSTALL，为了保证环境恢复的，会将DNF_INSTALL安装的所有包都进行卸载  
  `DNF_REMOVE`
  - 如果不想依赖DNF_INSTALL，单纯想要卸载某个包，需要在方法最后添加参数“1”  
  `DNF_REMOVE "tree" 1`

- REMOTE_REBOOT_WAIT
  - 多节点环境中，当对端进行重启操作，将用于等待对端完全重启  
  `REMOTE_REBOOT_WAIT $REMOTEPASSWD $REMOTEUSER $REMOTEIP`

- SLEEP_WAIT
  - 需要睡眠等待大于1秒的操作，不要直接使用sleep，建议使用SLEEP_WAIT  
  `SLEEP_WAIT 3`

- CHECK_RESULT
  - 对测试点进行检查，mugen框架将会对执行结果进行统计，所以务必使用此方法进行判断
  - 参数说明：
    - 参数1：实际结果  
    - 参数2：预期结果，默认为“0”  
    - 参数3：判断模式，默认为“0”：需要实际结果和预期结果一致；选择“1”：需要实际结果和预期结果不一致  
  `CHECK_RESULT 0 0`

## mugen中python公共方法

- 尽情期待。。。

## mugen的日志说明

所有用例执行结束之后

- 日志将存储到和runoet.sh同层的logs目录下面
- 执行结果将会存放到和runoet.sh同层的results目录下面
- logs和results目录会在用例执行之后自动生成
