#!/bin/bash
PATH=/www/server/panel/pyenv/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
public_file=/www/server/panel/install/public.sh



Install_frp()
{
    mkdir -p /www/server/panel/plugin/wlfrp
    echo '安装完成'
}
checkos(){
    if grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
        OS=CentOS
    elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
        OS=Debian
    elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
        OS=Ubuntu
    else
        echo "安装失败：Not support OS, Please reinstall OS and retry!"
        exit 1
    fi
}
uninstall_s(){
    program_init='/etc/init.d/ftps'
    program_name='frps'
    checkos
    /etc/init.d/ftps stop
    if [ "${OS}" == 'CentOS' ]; then
        chkconfig --del ${program_name}
    else
        update-rc.d -f ${program_name} remove
    fi
    rm -f ${program_init} /var/run/${program_name}.pid /usr/bin/${program_name}
    rm -rf /usr/local/frps
    echo "${program_name} uninstall success!"
}
uninstall_c(){
    program_init='/etc/init.d/frpc'
    program_name='frpc'
    checkos
    ${program_init} stop
    if [ "${OS}" == 'CentOS' ]; then
        chkconfig --del ${program_name}
    else
        update-rc.d -f ${program_name} remove
    fi
    rm -f ${program_init} /var/run/${program_name}.pid /usr/bin/${program_name}
    rm -rf /usr/local/${program_name}
    echo "${program_name} uninstall success!"
}

Uninstall_frp()
{
    uninstall_s
    uninstall_c
    rm -rf /www/server/panel/plugin/wlfrp
}

action=$1
if [ "${1}" == 'install' ];then
    Install_frp
else
    Uninstall_frp
fi
