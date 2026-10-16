### 软件包对比思路：
#### 1. 软件包列表获取

1、增加source、epol_source本地repo源
2、导出repo源中的源码包列表：everything_source_list、epol_source_list
    
    dnf list --repo="source" | grep ".src" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0,1,length($0)-1)}' | sort >everything_source_list

    dnf list --repo="EPOL_source" | grep ".src" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0,1,length($0)-1)}' | sort >epol_source_list
    
3、获取release-management仓库公告中的发布软件包列表：baseos_source、everything_source、epol_source

#### 2. 数据检查与对比分析
1、数据检查：确认baseos_source、everything_source无重复软件包;

    cat baseos/baseos_source everything-exclude-baseos/everything_source |sort |uniq -d

2、汇总baseos_source、everything_source中的软件包

    cat baseos/baseos_source everything-exclude-baseos/everything_source |sort >huizong_everthing_source

3、进行对比分析：

**独有软件包分两种情况：公告独有、repo独有，基本都是仓库名称和软件包名不一致导致的，逐个分析即可。**


#### 概览

    vimdiff huizong_everthing_source everything_source_list 
    vimdiff epol_source epol_source_list

##### everything共有软件包：
    cat everything_source_list huizong_everthing_source |sort |uniq -d >everything_d
##### everything所有独有软件包：
    cat everything_source_list huizong_everthing_source |sort |uniq -u >everything_u
##### everything 公告独有:
    cat huizong_everthing_source everything_u |sort |uniq -d >huizong_everthing_source_u
##### everything repo独有:
    cat everything_source_list everything_u |sort |uniq -d >everything_source_list_u


##### epol共有软件包：
    cat epol_source_list epol_source |sort |uniq -d >epol_d
##### epol所有独有软件包： 
    cat epol_source_list epol_source |sort |uniq -u >epol_u
##### epol 公告独有:
    cat epol_source epol_u |sort |uniq -d >epol_source_u
##### epol repo独有:
    cat epol_source_list epol_u |sort |uniq -d >epol_source_list_u
