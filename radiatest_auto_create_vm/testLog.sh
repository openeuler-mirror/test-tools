node{

    def ip_num = ['172.168.108.147': ['2', '2203sp1-x86-2-172.168.108.147'],
                '172.168.117.164': ['2', '2203sp4-x86-2-172.168.117.164'],
                '172.168.129.223': ['1', '2203sp1-x86-1-172.168.129.223'],
                '172.168.146.95': ['2', '2403lts-x86-2-172.168.146.95'],
                '172.168.153.220': ['1', '2403lts-arm-1-172.168.153.220'],
                '172.168.158.116': ['2', '2203sp3-arm-2-172.168.158.116'],
                '172.168.158.136': ['1', '2403lts-x86-1-172.168.158.136'],
                '172.168.199.17': ['1', '2003sp4-x86-1-172.168.199.17'],
                '172.168.164.128': ['1', '2203sp1-arm-1-172.168.164.128'],
                '172.168.164.135': ['1', '2203sp3-arm-1-172.168.164.135'],
                '172.168.186.155': ['1', '2203sp3-x86-1-172.168.186.155'],
                '172.168.210.100': ['2', '2003sp4-arm-2-172.168.210.100'],
                '172.168.237.68': ['1', '2203sp4-arm-1-172.168.237.68'],
                '172.168.240.188': ['1', '2003sp4-arm-1-172.168.240.188'],
                '172.168.3.199': ['2', '2203sp4-arm-2-172.168.3.199'],
                '172.168.32.162': ['2', '2403lts-arm-2-172.168.32.162'],
                '172.168.32.99': ['2', '2203sp3-x86-2-172.168.32.99'],
                '172.168.104.98': ['2', '2003sp4-x86-2-172.168.104.98'],
                '172.168.89.107': ['1', '2203sp4-x86-1-172.168.89.107'],
                '172.168.9.106': ['2', '2203sp1-arm-2-172.168.9.106'],
                '172.168.234.159': ['1', '2403sp1-arm-1-172.168.234.159'],
                '172.168.159.185': ['2', '2403sp1-arm-2-172.168.159.185'],
                '172.168.28.221': ['1', '2403sp1-x86-1-172.168.28.221'],
                '172.168.69.202': ['2', '2403sp1-x86-2-172.168.69.202'],
                '172.168.89.57': ['1', '2403sp2-arm-1-172.168.89.57'],
                '172.168.21.27': ['2', '2403sp2-arm-2-172.168.21.27'],
                '172.168.191.50': ['1', '2403sp2-x86-1-172.168.191.50'],
                '172.168.188.61': ['2', '2403sp2-x86-2-172.168.188.61']
                ]
    
    def remote = [:]
    remote.name = 'test'
    remote.host = '172.168.108.56'
    remote.user = 'root'
    remote.password = 'openEuler12#$'
    remote.allowAnyHosts = true
    stage('stage01') {
        def result = '\n\n\n-----------------------------------------------------------------\n'
        
        for (host in params.hosts.strip().readLines()){
            // echo host
            host = host.strip()
            if(host == ''){
                continue
            }
            echo host
            remote.host = host
            echo ip_num[host][0]
            
            result += ip_num[host][1] + ': \n'
            
            def log_file = sshCommand remote: remote, command: "ls -t /root/mugen/logs/pkgmanager-test/oe_test_pkg_manager0${ip_num[host][0]}/ | head -1"
            
            log_file = log_file.strip()
            if(log_file == ''){
                result += "** /root/mugen/logs/pkgmanager-test/oe_test_pkg_manager0${ip_num[host][0]}/ \n** Warning: log file empty\n-----------------------------------------------------------------\n\n"
                continue
                // error 'log file is empty'
            }
            
            def testn = sshCommand remote: remote, command: "grep 'test -n' /root/mugen/logs/pkgmanager-test/oe_test_pkg_manager0${ip_num[host][0]}/${log_file} || true" 
            testn = testn.strip()
            if(testn == ''){
                echo 'log file no test -n . ok ok ok'
                result += "** /root/mugen/logs/pkgmanager-test/oe_test_pkg_manager0${ip_num[host][0]}/${log_file} \n** log file no test -n\n-----------------------------------------------------------------\n\n"
                continue
            }
            
            if(testn.contains("two architectures are not equal in number")){
                result += "  == two architectures are not equal in number\n\n"
            }
            
            // ls /home/pkg_manager_folder/*_fail_list
            def fail_list = sshCommand remote: remote, command: "find /home/pkg_manager_folder/ -type f -name '*_fail_list'"
            fail_list = fail_list.strip()
            echo fail_list
            if (fail_list == ''){
                echo 'no *_fail_list, exit with ok'
                result += "** /home/pkg_manager_folder/ no fail_list \n-----------------------------------------------------------------\n"
                continue
            }
            def pkgs = []
            for (fail_list_fn in fail_list.readLines()){
                echo fail_list
                result += '    ' + fail_list_fn.split('/')[-1][0..-11] + ':\n'
                list_content = sshCommand remote: remote, command: "cat ${fail_list_fn}"
                
                for (fail_line in list_content.strip().readLines()){
                    pkg = fail_line.strip()
                    result += '        ' + pkg + '\n'
                    if (!(pkg in pkgs)){
                        pkgs.add(pkg)
                    }
                }
                
            }
            result += '\n    ' + pkgs.join(' ')
            result += '\n-----------------------------------------------------------------\n'
    
        }
        echo result
    }
}
