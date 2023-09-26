import re
import os
import time
import subprocess
import sys
import os
import subprocess
import shutil
import pathlib
import time
import csv


'''
Part 1: compilation option detection
'''

def PIE_check(filename:str)->str:
    ''' PIE check function
        parm: str type filename
        This function check for PIE support.
    '''
    pie_check_sh = '''
        if readelf -h "%s" 2> /dev/null | grep -q 'Type:[[:space:]]*EXEC'; then
            echo "No"
        elif readelf -h "%s" 2> /dev/null | grep -q 'Type:[[:space:]]*DYN'; then
            if readelf -d "%s" 2> /dev/null | grep -q 'DEBUG'; then
                echo "PIE enabled"
            else
                echo "PIC enabled"
            fi
        elif readelf -h "%s" 2> /dev/null | grep -q 'Type:[[:space:]]*REL'; then
            echo "PIE enabled"
        fi
        ''' 
    pie_check_sh = pie_check_sh % (filename, filename, filename, filename)
    subp = subprocess.Popen(pie_check_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    # print(outs, errs)
    return outs

def StackProteck_check(filename:str)->str:
    ''' Stack Protect check function
        parm: str type filename
        The function check for stack canary support.
    '''

    StackProteck_check_sh = '''
        if readelf -s "%s" 2> /dev/null | grep " UND " | grep -Eq '__stack_chk_fail|__stack_chk_guard|__intel_security_cookie'; then
            echo "YES Canary found"
        else
            echo "No canary found"
        fi
        '''
    StackProteck_check_sh = StackProteck_check_sh % (filename)
    subp = subprocess.Popen(StackProteck_check_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    return outs

def NX_check(filename:str)->str:
    ''' NX check function
        parm: str type filename
        The function will check for Non-Executable Memory(NX) support. 
    '''
   
    NX_check_sh = '''
        #!/usr/bin/bash
        if [[ $(readelf -l "%s") =~ "no program headers"  2> /dev/null ]]; then
            echo "N/A"
        elif readelf -l "%s" 2> /dev/null | grep -q 'GNU_STACK'; then
	        rwe=$(readelf -l "%s" 2> /dev/null | grep -A 1 'GNU_STACK' | sed 's/0x0000000000000000//g' )
            RWE="RWE"
            case $rwe in
                *$RWE*) echo 'NX disabled' ;;
                *) echo 'NX enabled' ;;
            esac
        else
            echo "NX disabled"
        fi
        '''
    NX_check_sh = NX_check_sh % (filename, filename, filename)
    subp = subprocess.Popen( NX_check_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')   # {"PATH":"/usr/bin/grep", "PATH":"/bin/bash"}
    outs, errs = subp.communicate(None)
    return outs

def RELRO_check(filename:str)->str:
    ''' RELRO check function: 
        parm: str type filename
        The function will check for RELRO support.
    '''
    RELRO_check_sh = '''
        if [[ $(readelf -l "%s") =~ "no program headers" 2> /dev/null ]]; then
            echo 'N/A'     
        elif readelf -l "%s" 2> /dev/null | grep -q 'GNU_RELRO'; then
            if readelf -d "%s" 2> /dev/null | grep -q 'BIND_NOW' || ! readelf -l "%s" 2> /dev/null | grep -q '\.got\.plt'; then
                echo "Full"
            else
                echo "Partial"
            fi
        else
            echo "No RELRO"
        fi
    '''
    # replace the filename in the shell script.
    RELRO_check_sh = RELRO_check_sh % (filename, filename, filename, filename)
    subp = subprocess.Popen(RELRO_check_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    # print(outs, errs)
    return outs

def BIND_NOW_check(filename:str)->str:
    ''' BIND_NOW check function
    '''
    BIND_NOW_check_shell = '''
        if readelf -d "%s" 2> /dev/null | grep -q 'BIND_NOW'; then
            if readelf -d "%s" 2> /dev/null | grep -q 'NOW' ; then
                echo "BIND NOW"
            else
                echo "BIND NOW"
            fi
        else
            echo "NO BIND"
        fi   
    '''
    BIND_NOW_check_shell = BIND_NOW_check_shell % (filename, filename)
    subp = subprocess.Popen(BIND_NOW_check_shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    # print(outs, errs)
    return outs

def Strip_check(filename:str)->str:
    ''' Strip check function
        parm: str type filename
        The function check for stripped symbols
    '''
    # 3 ways to check
    # use 'file' to check
    Strip_check_sh = '''
        file %s
    '''

    # use 'nm' to check, another way.
    Strip_check_sh = '''
        nm %s
    '''

    # use readelf
    Strip_check_sh = '''
        if readelf --symbols "%s" 2> /dev/null | grep -q '\.symtab'; then
            echo "No"
        else
            echo 'Yes'
        fi
    '''

    Strip_check_sh = Strip_check_sh % (filename)
    subp = subprocess.Popen(Strip_check_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    strip = outs

    # get symbol num
    symbol_num = '''
        readelf --symbols %s 2> /dev/null | grep -i symtab
    '''
    symbol_num = symbol_num % (filename)
    subp = subprocess.Popen(symbol_num, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    if(outs == ''):
        num = 0
    else:
        # outs like: Symbol table '.symtab' contains 65 entries
        # so we get the num in the string
        num = ''.join(re.findall("\d+", outs))
        # print(num + ' symbols')
    
    return strip, num

def FortitySource_check(filename:str)->str:
    FortitySource_check_sh = '''
        FS_func="$(readelf --dyn-syms '%s' 2> /dev/null | awk '{ print $8 }' | sed -e 's/_*//' -e 's/@.*//' -e '/^$/d')"
        chk="_chk"
        case $FS_func in
            *$chk*) echo 'YES' ;;
            *) echo 'NO' ;;
        esac
    '''
    FortitySource_check_sh = FortitySource_check_sh % (filename)
    subp = subprocess.Popen(FortitySource_check_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    # print(outs, errs)
    return outs

def IntegerOverflow_check(filename:str)->str:
    IntegerOverflow_sh = '''
        IO_func="$(readelf --dyn-syms '%s' 2> /dev/null | awk '{ print $8 }' | sed -e 's/_*//' -e 's/@.*//' -e '/^$/d')"
        # echo $IO_func
        add="addv"
        sub="subv"
        mul="mulv"
        case $IO_func in
            *$add*) echo 'YES' ;;
            *$sub*) echo 'YES' ;;
            *$mul*) echo 'YES' ;;
            *) echo 'NO' ;;
        esac
    '''
    IntegerOverflow_sh = IntegerOverflow_sh % (filename)
    subp = subprocess.Popen(IntegerOverflow_sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    # print(outs, errs)
    return outs

def RUNPATH_check(filename:str)->str:
    path_check = '''
    if [[ $(readelf -d "%s" 2> /dev/null ) =~ "no dynamic section" ]]; then
        echo 'N/A'
    else
        if readelf -d "%s"  2> /dev/null | grep -q "(RUNPATH)" ; then
            echo "RUNPATH"
        elif readelf -d "%s"  2> /dev/null | grep -q "(RPATH)" ; then
            echo "RPATH"
        else 
            echo "NO R/RUN PATH"
        fi
    fi
    '''
    path_check = path_check % (filename, filename, filename)
    subp = subprocess.Popen(path_check, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    # print(outs, errs)
    return outs

nowpath = os.path.dirname(os.path.realpath('__file__'))

def elflog(msg:str)->None:
    logfile = nowpath + "/Log/elflog.txt"
    logtime = time.strftime("%Y-%m-%d %H:%M:%S\t", time.localtime()) 
    if('/tmp/rpm' in msg):
        msg = msg.replace('/tmp/rpm', '')
    with open(logfile, 'a+') as fd:
        fd.write(logtime + msg + "\n")

def CheckELF(filename:str)->dict:
    elflog("\nChecking " + filename)

    yes =  { 'PIC' : 0, 'PIE'  : 0, 'SP': 0, 'NX' : 0, 'RELRO': 0, 
            'BIND_NOW': 0, 'Strip': 0, 'FS': 0, 'Ftrpv': 0, 'NO Rpath/Runpath': 0 }
    no = { 'PIC' : 0, 'PIE'  : 0, 'SP': 0, 'NX' : 0, 'RELRO': 0, 
            'BIND_NOW': 0, 'Strip': 0, 'FS': 0, 'Ftrpv': 0, 'NO Rpath/Runpath': 0 }
    
    listfilename = filename.split('/')
    del(listfilename[0])
    objectName = listfilename.pop()
    filePath = "/".join(listfilename) + '/'
    detail = [filePath, objectName]
    y = 'YES'
    n = 'NO'
    na = 'N/A'
    # Log and for log...
    pie = PIE_check(filename)
    if('PIC' in pie):
        elflog("PIC: YES")
        yes['PIC'] += 1
        detail.append(y)
        detail.append('')
        # for PIE
        detail.append('')
        detail.append('')
    elif('PIE' in pie):
        elflog("PIE: YES")
        yes['PIE'] += 1
        # for PIC
        detail.append('')
        detail.append('')
        detail.append(y)
        detail.append('')
        
    else:
        elflog('PIC/PIE: NO')
        no['PIC'] += 1
        no['PIE'] += 1
        detail.append(n)
        detail.append('')
        detail.append(n)
        detail.append('')

    stack = StackProteck_check(filename)
    if('YES' in stack):
        elflog("Stack Protect: YES")
        yes['SP'] += 1
        detail.append(y)
    else:
        elflog("Stack Protect: NO")
        no['SP'] += 1
        detail.append(n)
    detail.append('')
    
    nx = NX_check(filename)
    if('enabled' in nx):
        elflog("NX: YES")
        yes['NX'] += 1
        detail.append(y)
    elif('N/A' in nx):
        elflog("NX: N/A")
        detail.append(na)
    else:
        elflog("NX: NO")
        no['NX'] += 1
        detail.append(n)
    detail.append('')
    
    relro = RELRO_check(filename)
    relro = relro.replace("\n", "")
    if('N/A' in relro):
        elflog("RELRO: N/A")
        detail.append(na)
    elif('No' in relro):
        elflog("RELRO: NO")
        no['RELRO'] += 1
        detail.append(n)
    else:
        elflog("RELRO: " + relro)
        yes['RELRO'] += 1
        detail.append(y)
    detail.append('')

    bindnow = BIND_NOW_check(filename)
    if('NOW' in bindnow):
        elflog("BIND_NOW: YES")
        yes['BIND_NOW'] += 1
        detail.append(y)
    else:
        elflog("BIND_NOW: NO")
        no['BIND_NOW'] += 1
        detail.append(n)
    detail.append('')
    

    strip, num = Strip_check(filename)
    if('Yes' in strip):
        elflog("Stripped: YES")
        yes['Strip'] += 1
        detail.append(y)
    else:
        elflog("Stripped: NO, %s symbols." % num)
        no['Strip'] += 1
        detail.append(n)
    detail.append('')

    fsource = FortitySource_check(filename)
    if('YES' in fsource):
        elflog("Fortity Source: YES")
        yes['FS'] += 1
        detail.append(y)
    else:
        elflog("Fortity Source: NO")
        no['FS'] += 1
        detail.append(n)
    detail.append('')

    intoverflow = IntegerOverflow_check(filename)
    if('N/A' in intoverflow):
        elflog("Int Overflow: N/A")
        detail.append(na)
    elif('YES' in intoverflow):
        elflog("Int Overflow: YES")
        yes['Ftrpv'] += 1
        detail.append(y)
    else:
        elflog("Int Overflow: NO")
        no['Ftrpv'] += 1
        detail.append(n)
    detail.append('')

    rpath = RUNPATH_check(filename)
    if('NO' in rpath):
        elflog("No RUN PATH: YES")
        yes['NO Rpath/Runpath'] += 1
        detail.append(y)
    elif('N/A' in rpath):
        elflog("RUN PATH: N/A")
        detail.append(na)
    else:
        elflog("No RUN PATH: No")
        no['NO Rpath/Runpath'] += 1
        detail.append(n)
    detail.append('')

    return yes, no, detail

'''
Part 2: comprehensive processing.
'''

# global variable could reduce calling function now_path
nowpath = ''
def now_path()->str:
    global nowpath
    nowpath = os.path.dirname(os.path.realpath('__file__'))
    return nowpath

def file_exist_check(filename:str)->bool:
    path = pathlib.Path(filename)
    return path.exists()

def readable(filename:str)->bool:
    # check whether can we read the file
    if(file_exist_check(filename)):
        return (os.access(filename, os.R_OK))
    return False

def python_version_check()->None:
    # I am not very confirmed which version of python3 is min.
    if( sys.version_info < (3, 5)):
        rpmlog("Python Version is too low.")
        exit()
    else:
        rpmlog("python version is ok.")

def shell_check(cmd:str)->bool:
    # check whether shell cmd exists
    checksh = '''
		if type %s >/dev/null 2>&1 ; then
			echo 1
		else
			echo 0
		fi
	'''
    checksh = checksh % (cmd)
    subp = subprocess.Popen( checksh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    if ('1' in outs):
        return True
    return False

def readlink(filename:str)->str:
    # get abs path of the file
    sh = '''
        readlink -f %s
        '''
    sh = sh % (filename)
    subp = subprocess.Popen( sh,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    return outs

def rpm2cpio_tmp(filename:str)->str:
    # rmp2cpio the rmp file into /tmp
    filename = readlink(filename)
    filename = filename.replace("\n", "")

    tmpfilename = filename.split("/")
    tmpname = tmpfilename[len(tmpfilename) -1 ]

    filedir = filename.replace(tmpname, "")
    filedir = filedir.replace("\n", "")
    
    if(tmp_stat(filename) == False):
        rpmlog("/tmp space is full.")
        return None

    os.chdir(filedir)
    if(not readable(tmpname)):
        rpmlog("Sorry, can't read the file.")
        return None
    
    dirname = "/tmp/rpm/" + tmpname
    if(not os.path.exists(dirname)):
        os.makedirs(dirname)
    shutil.move(tmpname, dirname)
    if(not readable(dirname + "/" + tmpname)):
        rpmlog("Something wrong.")
        return None
    # there is a problem:
    # what if when cpio rpm file, the space is not enough?
    # how to check before cpio? and what should we do?
    rpmsh = '''
        cd %s
        rpm2cpio %s | cpio -idm 
    '''
    rpmsh = rpmsh % (dirname, tmpname)
    # run the shell code to cpio rpm file.
    subprocess.Popen(rpmsh,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=None, shell=True, env=None, encoding='utf-8')
    msg = "cpio the %s RPM file" % tmpname
    rpmlog(msg)
    return dirname

def cleantmp()->None:
    # clean up /tmp/rmp
    if(file_exist_check("/tmp/rpm")):
        shutil.rmtree("/tmp/rpm")
    rpmlog("clean the '/rpm' file in /tmp.")

def tmp_stat(filename:str)->bool:
    # judge /tmp space is enough or not.
    disk = os.statvfs("/tmp")
    tmp_avi = disk.f_bavail * disk.f_bsize
    st_sizes = os.stat(filename).st_size
    # print(tmp_avi)
    # print(st_sizes)
    # print(os.path.getsize('/tmp'))
    # print(os.path.getsize(filename))
    if(tmp_avi < st_sizes):
        return False
    return True

def rpmlog(msg:str, filerpm = 'run')->None:
    logfile = nowpath + "/Log/%s-log.txt" % (filerpm)
    logtime = time.strftime("%Y-%m-%d %H:%M:%S\t", time.localtime()) 
    if('/tmp/rpm' in msg):
        msg = msg.replace('/tmp/rpm', '')
    with open(logfile, 'a+') as fd:
        fd.write(logtime + msg + "\n")
        # print( logtime + msg)

def findAllFile(base = '/tmp/rpm/'):
    # find all files in the /tmp/rpm.
    for dirpath, dirnames, filenames in os.walk(base):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

def isELF(filename:str)->bool:
    # judge a file is or not a ELF file
    sh = '''
        if file %s | grep -q 'ELF' ; then
            echo 1
        else
            echo 0
        fi
    '''
    sh = sh % (filename)
    subp = subprocess.Popen(sh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            ,preexec_fn=None, shell=True, env=None, encoding='utf-8')
    outs, errs = subp.communicate(None)
    if('1' in outs):
        return True
    return False

def createLogDir()->None:
    logDir = nowpath + "/Log"
    if(not readable(logDir)):
        os.makedirs(logDir)

def produce(rpm:str):
    
    filename = readlink(rpm)
    filename = filename.replace("\n", "")

    if(not file_exist_check(filename)):
        rpmlog("No such file or directory: " + filename)
        return None, None

    # 3.cpio the rpm file
    dirname = rpm2cpio_tmp(rpm)
    if(dirname == None):
        return None, None
    # print(now_path())   # for test
    # 4.list all file in rpm
    elffile = []
    notelf = []
    allFile = []
    # cuz function 'findAllFile' is recursion
    time.sleep(1)
    for f in findAllFile(base = dirname):
        # 5.check whether file in rpm is ELF
        if(isELF(f)):
            elffile.append(f)
        else:
            notelf.append(f)
        allFile.append(f)
    
    # 5.check & log
    for nelf in notelf:
        # pass    # for test
        rpmlog("N/A: " + nelf)

    # for csv record all files
    yes =  { 'PIC' : 0, 'PIE'  : 0, 'SP': 0, 'NX' : 0, 'RELRO': 0, 
            'BIND_NOW': 0, 'Strip': 0, 'FS': 0, 'Ftrpv': 0, 'NO Rpath/Runpath': 0 }
    no = { 'PIC' : 0, 'PIE'  : 0, 'SP': 0, 'NX' : 0, 'RELRO': 0, 
            'BIND_NOW': 0, 'Strip': 0, 'FS': 0, 'Ftrpv': 0, 'NO Rpath/Runpath': 0 }   
    details = []
    for elf in elffile:
        tmpyes, tmpno, detail = CheckELF(elf)
        details.append(detail)
        for key in tmpyes:
            yes[key] += tmpyes[key]
            no[key] += tmpno[key]  
    # all records in A RPM
    return yes, no, details

def summary(yes:dict, no:dict)->None:
    rows = [ ['Item', 'Level', 'Result', 'Unqualified', 'Total' ] ]
    high = 'high'
    medium = 'medium'
    for key in yes:
        level = high
        if(key == 'FS' or key == 'Ftrpv'):
            level = medium
        arow = []
        arow.append(key)
        arow.append(level)
        num = yes[key] + no[key]
        if(num == 0):
            num = 100000000
        resul= round( yes[key] / num , 4) * 100
        resu = str(resul) + '%'
        arow.append(resu)
        arow.append(no[key])
        if(num == 100000000):
            num = 0
        arow.append(num)
        rows.append(arow)   

    with open('./Log/Summary.csv', 'a+') as fd:
        writer = csv.writer(fd)
        writer.writerows(rows)


if __name__ == '__main__' :
    print("Welcome to use the tool.")
    print("plz input the RPM file name, include abspath better:")
    rpm = input()
    now_path()
    createLogDir()
    # 1.python version & shell check: read, readelf, nm, file, 
    python_version_check()
    needed_cmd = ['readelf', 'nm', 'file', 'grep', 'sed', 'awk']
    for cmd in needed_cmd:
        if(shell_check(cmd) == False):
            rpmlog("command " + cmd + " doesn't exist.")
            exit()
    # clean /tmp/rpm and create the dir
    cleantmp()
    if(not os.path.exists("/tmp/rpm")):
        os.makedirs("/tmp/rpm")

    # for csv record all files
    yes =  { 'PIC' : 0, 'PIE'  : 0, 'SP': 0, 'NX' : 0, 'RELRO': 0, 
            'BIND_NOW': 0, 'Strip': 0, 'FS': 0, 'Ftrpv': 0, 'NO Rpath/Runpath': 0 }
    no = { 'PIC' : 0, 'PIE'  : 0, 'SP': 0, 'NX' : 0, 'RELRO': 0, 
            'BIND_NOW': 0, 'Strip': 0, 'FS': 0, 'Ftrpv': 0, 'NO Rpath/Runpath': 0 }
    detail_line0 = ['FilePath', 'Object', 'PIC', 'PIC_CONFIRM', 'PIE', 'PIE_CONFIRM',
            'SP', 'SP_CONFIRM', 'NX', 'NX_CONFIRM', 'RELRO', 'RELRO_CONFIRM',
            'BIND_NOW', 'BINW_NOW_CONFIRM', 'Strip', 'Strip_CONFIRM', 'FS', 
            'FS_CONFIRM', 'Ftrapv', 'Ftrapv_CONFIRM', 'NO Rpath/Runpath', 
            'NO Rpath/Runpath_CONFIRM', 'Confirmer', 'Remark' ]
    # We need to get the detail CSV file.
    with open('./Log/Detail.csv', 'a+') as detailFD:
        d_writer = csv.writer(detailFD)
        d_writer.writerow(detail_line0)
    
        # extract all rpm file in the dir
        if(os.path.isdir(rpm)):
            for f in findAllFile(base = rpm):
                # procedure every RPM file
                if('.rpm' in f):
                    tmpyes, tmpno, detail = produce(f)
                if(tmpyes == None):
                    print("Something is wrong! Check the log.")
                    exit()
                d_writer.writerows(detail)
                # all records in A Dir
                for key in tmpyes:
                    yes[key] += tmpyes[key]
                    no[key] += tmpno[key] 
        # if input a file
        elif(os.path.isfile(rpm)):            
            if('.rpm' not in rpm):
                print("This file is not RPM!")
                rpmlog("Wrong file type.")
                exit()
            tmpyes, tmpno, detail = produce(rpm)
            if(tmpyes == None):
                print("Something is wrong! Check the log.")
                exit()
            d_writer.writerows(detail)
            for key in tmpyes:
                yes[key] += tmpyes[key]
                no[key] += tmpno[key] 
        else:
            print("No RPM!")
            rpmlog("No rpm file.")
    
    summary(yes, no)
    print("Check finished, look up the logs.")
