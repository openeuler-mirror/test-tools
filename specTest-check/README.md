# 检测spec文件中make check

- pro:
  - 工具使用bash语言编写，使用前确保bash grep wget软件包已安装  
    - openEuler: dnf -y install bash grep wget
- usage:  
  - \-c: 检测包的spec文件中，%check是否被使用．  
  - \-d: 对比包的spec文件中％check，在fedora和openEuler中的情况．
- Example:  
  - bash makecheck.sh -c autoconf
  - bash makecheck.sh -d autoconf"
