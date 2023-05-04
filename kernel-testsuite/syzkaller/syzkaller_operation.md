### Syzkaller测试<br/>
##### 使用镜像安装物理机器，并拷贝物理机安装时的镜像文件至目标机器的/home目录<br/>
##### 准备syzkaller的脚本至/home/syzdelop目录,获取路径:https://gitee.com/openeuler/test-tools/kernel-testsuite<br/>
##### 参照脚本中的usage说明1-5步骤顺序执行，保证每一步都成功执行<br/>
* sh syzdelop.sh deploy<br/>
安装deploy,qemu,syzkaller，yum源配置正确会顺利安装成功<br/>

* sh syzdelop.sh build kasan/ubsan；#编译kasan/ubsan<br/>

* sh syzdelop.sh createvm<br/>
1.启动脚本后，从菜单栏tigervnc view通过ip:31挂载镜像进行安装(安装方法可咨询安装小组)<br/>
2.安装完成后保留安装虚拟机的窗口<br/>

* sh syzdelop.sh config<br/>
1.安装完成后reboot重启虚拟机；使虚拟机配置和安装的内核生效；<br/>
2.shutdown -h now关闭虚拟机；<br/>

* sh syzdelop.sh fuzz <br/>
1.如果出现页面是机器有两个ip，导致ip获取失败，Ctrl+C终止掉后修改ip；生成的/home/fuzz.cfg,如果目标机器会出现两个ip需手工修改对应机器的ip：<br/>
2.再次执行sh syzdelop.sh fuzz启动syzkaller服务(可以运行2-3天): <br/>
3.使用上述提示页面的url，在web页面查看log等信息，正常显示表示虚拟机安装成功<br/>

## 如下步骤可以单步骤调整环境所用：<br/>
1.sh sysdelop.sh startvm；手工启动虚拟机<br/>
2.sh syzdelop.sh uninstall；手工卸载<br/>
3.sh syzdelop.sh h；查看帮助信息<br/>

