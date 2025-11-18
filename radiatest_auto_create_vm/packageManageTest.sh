node{
    
    // def host = 'b'
    // 172.168.108.56
    def name_rgx = ~/[a-zA-Z0-9]+-(x86|arm)-(1|2)-([0-9]+\.){3}[0-9]{1,3}/
    def host = ''
    def case_num = ''    
    
    if ("${JOB_NAME}" ==~ "${name_rgx}"){
        echo 'matched ok'
        def name_items = "${JOB_NAME}".split('-')
        case_num = name_items[2]
        host = name_items[3].strip()
    }else{
        echo 'not matched'
        error "job name not right!!!"
    }
    
    // /root/update.hosts.csv
    case_host = """${sh(
                returnStdout: true,
                script: 'awk -F \',\' \'{if($1=="' + "${host}" + '"){print $2}}\'  /root/update.hosts.csv | head -1'
            )}""".strip()
    
    if("${case_host}" == ''){
        echo 'Error: testcase host ip is empty!!!'
        error 'Error: testcase host ip is empty!!!'
    }
    
    def remote = [:]
    remote.name = 'test'
    remote.host = "${host}".strip()
    remote.user = 'root'
    remote.password = 'openEuler12#$'
    remote.allowAnyHosts = true
    
    def casenode = [:]
    casenode.name = 'test2'
    casenode.host = "${case_host}"
    casenode.user = 'root'
    casenode.password = 'openEuler12#$'
    casenode.allowAnyHosts = true
    
    bash_env = ''
    if(params.DISABLE_UPDATE_EPOL){
        bash_env += "export DISABLE_UPDATE_EPOL=1;"
    }
    
    stage('info') {
        echo "${host} --> ${case_host} testcase-${case_num}"
        println '=================host info==============='
        sshCommand remote: remote, command: "cat /etc/openEuler-release"
        sshCommand remote: remote, command: "lscpu | grep Architecture | awk '{print \$2}'"
        println '=================case info==============='
        sshCommand remote: casenode, command: "cat /etc/openEuler-release"
        sshCommand remote: casenode, command: "lscpu | grep Architecture | awk '{print \$2}'"
        println '========================================='
        
        sshCommand remote: remote, command: "ip a"
        sshCommand remote: remote, command: "yum repolist --all | grep update_2025  | grep -v source |awk '{print \$1}' | xargs -i dnf config-manager --set-disabled {}"
        sshCommand remote: remote, command: "cd /root/mugen/; bash dep_install.sh"
        sshCommand remote: remote, command: "rm -rf /home/* /root/rpmbuild/*  /root/mugen/logs/* /root/mugen/results/* /root/mugen/conf/*"
        sshCommand remote: remote, command: "cd /root/mugen/;bash mugen.sh -c --password openEuler12#\$ --ip ${host};bash mugen.sh -c --password openEuler12#\$ --ip ${case_host};"
        sshCommand remote: remote, command: bash_env + "cd /root/mugen/;bash mugen.sh -f pkgmanager-test -r oe_test_pkg_manager0${case_num} -x"
        println '============ ok =========='
    }
    
}
