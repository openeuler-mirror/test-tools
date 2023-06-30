#!/bin/bash -e

# 多版本源安装
# add-apt-repository ppa:ubuntu-toolchain-r/test
# apt-get update
# apt-get install gcc-4.9
# apt-get install g++-4.9
# update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 20
# update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.9 20
#
# usage:
# $1: input gcc version
# $2: input install path
# bash install_gcc.sh gcc-9.3.0 /root
# bash install_gcc.sh gcc-9.3.0 /root gmp-6.1.0 mpc-1.0.3 mpfr-3.1.4

gcc_name=$1
install_path=$2
gmp_name=${$3-"gmp-6.1.0"}
mpc_name=${$4-"mpc-1.0.3"}
mpfr_name=${$5-"mpfr-3.1.4"}


#
# usage:
# $1: input gcc version
# $2: input install path
# bash install_gcc.sh gcc-9.3.0 /root
# bash install_gcc.sh gcc-9.3.0 /root gmp-6.1.0 mpc-1.0.3 mpfr-3.1.4

gcc_name=$1
install_path=$2
gmp_name=${$3-"gmp-6.1.0"}
mpc_name=${$4-"mpc-1.0.3"}
mpfr_name=${$5-"mpfr-3.1.4"}

source /etc/os-release
case $ID in
debian|ubuntu|devuan)
    apt-get install -y gcc make libncurses5-dev openssl libssl-dev build-essential pkg-config libc6-dev bison flex libelf-dev  texinfo
    ;;
openEuler|centos|fedora|rhel|anolis)
    yum install -y gcc-c++ gcc gmp  gmp-devel  mpfr  mpfr-devel  libmpc  libmpc-devel  zlib-devel wget tar make flex
    ;;
*)
    exit 1
    ;;
esac

now_dir=`pwd`;

src_dir="$install_path/install/gcc_install/src"        # 源码生成目录，最后会进行删除gcc源码
bin_dir="$install_path/install/gcc_install/bin"        # 安装目录，最终gcc可执行文件安装目录
mirror_site="https://repo.huaweicloud.com/gnu"

if [ ! -f "$gcc_name.tar.gz" ];then
wget --no-check-certificate $mirror_site/gcc/$gcc_name/$gcc_name.tar.gz;
fi

if [ ! -f "$gmp_name.tar.bz2" ];then
wget --no-check-certificate $mirror_site/gmp/$gmp_name.tar.bz2;
fi

if [ ! -f "$mpc_name.tar.gz" ];then
wget --no-check-certificate $mirror_site/mpc/$mpc_name.tar.gz;
fi

if [ ! -f "$mpfr_name.tar.bz2" ];then
wget --no-check-certificate $mirror_site/mpfr/$mpfr_name.tar.bz2;
fi

mkdir -p $src_dir;
cd $src_dir;

if [ ! -d "$gcc_name" ]; then
  tar -zxvf $now_dir/$gcc_name.tar.gz
else
  echo "$gcc_name file already exists"
  exit 1;
fi

cd $gcc_name

if [ ! -d "mpc" ]; then
  tar -zxvf $now_dir/$mpc_name.tar.gz
  mv $mpc_name mpc
else
  echo "mpc file already exists"
  exit 1;
fi

if [ ! -d "gmp" ]; then
  tar -jxvf $now_dir/$gmp_name.tar.bz2
  mv $gmp_name gmp
else
  echo "gmp file already exists"
  exit 1;
fi

if [ ! -d "mpfr" ]; then
  tar -jxvf $now_dir/$mpfr_name.tar.bz2;
  mv $mpfr_name mpfr
else
  echo "mpfr file already exists"
  exit 1;
fi

mkdir -p $bin_dir
./configure --prefix=$install_path/install/gcc_install/bin/$gcc_name --enable-shared --enable-threads=posix --enable-checking=release --with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions --enable-gnu-unique-object --enable-linker-build-id --with-linker-hash-style=gnu --enable-languages=c,c++,objc,obj-c++,fortran,lto --enable-plugin --enable-initfini-array --disable-libgcj --without-isl --without-cloog --enable-gnu-indirect-function --with-stage1-ldflags=' -Wl,-z,relro,-z,now' --with-boot-ldflags=' -Wl,-z,relro,-z,now' --disable-multilib --disable-bootstrap

make -j$(getconf _NPROCESSORS_ONLN) 

# 打包deb
# checkinstall -D make install -j$(getconf _NPROCESSORS_ONLN) 

make install -j$(getconf _NPROCESSORS_ONLN) 

if [ ! -d "$bin_dir/$gcc_name/bin" ]; then
  echo "$bin_dir/$gcc_name/bin file does not exist, $gcc_name installation failed. Please try again"
  exit 1;
fi

rm -rf $src_dir/$gcc_name       # 删除gcc源码及编译过程文件

echo "test ..."
now_dir=`pwd`; 
$bin_dir/$gcc_name/bin/gcc --version;

echo "export PATH=$now_dir:\$PATH" >> ~/.bashrc
echo "please run \`source ~/.bashrc\` to use $gcc_name"
