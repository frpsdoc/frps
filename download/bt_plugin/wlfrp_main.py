#!/usr/bin/python
# coding: utf-8
# +------------------------------------------------------------------
# | frp
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: sww
# +-------------------------------------------------------------------
import json
import os
import platform
import subprocess
import sys
import re
import traceback

BASE_PATH = "/www/server/panel"
os.chdir(BASE_PATH)
sys.path.insert(0, "class/")
import public
import configparser

try:
    import toml
except:
    public.ExecShell('btpip install toml')
    import toml


class wlfrp_main:
    log_path = '/var/log/frps.log'
    config_path = '/usr/local/frps/frps.toml'

    def get_frps_config(self, get=None):
        if not os.path.exists(self.config_path):
            if os.path.exists('/usr/local/frps/frps.ini'):
                return public.returnMsg(False, '请重新安装frps服务，旧版本的配置文件即将弃用！')
            else:
                return public.returnMsg(False, '配置文件不存在!')
        self.config = toml.load('/usr/local/frps/frps.toml')
        self.config['serveraddr'] = public.get_server_ip()
        self.config['bind'] = public.check_firewall_rule(self.config['bindPort'])
        self.config['http'] = public.check_firewall_rule(self.config['vhostHTTPPort'])
        self.config['https'] = public.check_firewall_rule(self.config['vhostHTTPSPort'])
        self.config['webserverport'] = public.check_firewall_rule(self.config['webServer']['port'])
        self.config['tcpmux'] = public.check_firewall_rule(self.config['tcpmuxHTTPConnectPort'])
        self.config['kcp'] = public.check_firewall_rule(self.config['kcpBindPort'])
        return self.config



    def get_frps_panel_url(self, get):
        port= get['port']
        frps_panel_url_addr = 'http://' + public.get_server_ip() + ':' + port
        data = {
            'status': True,
            'frps_panel_url_addr': frps_panel_url_addr,
            "msg":"获取成功！"
        }
        return data






    def check_port(self, port):
        '''
        @name 检查端口是否被占用
        @args port:端口号
        @return: 被占用返回True，否则返回False
        '''
        a = public.ExecShell("netstat -nltp|awk '{print $4}'")
        if a[0]:
            if re.search(':' + str(port) + '\n', a[0]):
                return True
            else:
                return False
        else:
            return False

    def install_frps(self, get=None):
        if os.path.exists('/etc/init.d/frps') and os.path.exists('/usr/local/frps/frps'):
            return public.returnMsg(False, 'FRPS已经安装了!')
        public.ExecShell('wget -O /www/server/panel/plugin/wlfrp/frp_0.53.2_linux_amd64.tar.gz https://frps.wlphp.com/download/src/frp/frp_0.53.2_linux_amd64.tar.gz')
        public.ExecShell('tar -zxvf /www/server/panel/plugin/wlfrp/frp_0.53.2_linux_amd64.tar.gz -C /usr/local/')
        public.ExecShell('mv /usr/local/frp_0.53.2_linux_amd64 /usr/local/frps')
        public.ExecShell('rm -f /www/server/panel/plugin/wlfrp/frp_0.53.2_linux_amd64.tar.gz')
        public.ExecShell('wget -O /etc/init.d/frps https://frps.wlphp.com/download/src/frp/frps.init')
        public.ExecShell('cp /etc/init.d/frps /usr/bin/frps')
        public.ExecShell('chmod +x /etc/init.d/frps')
        set_bind_port = 7000
        set_vhost_http_port = 8080
        set_vhost_https_port = 8443
        set_dashboard_port = 7500
        set_dashboard_user = public.GetRandomString(8)
        set_dashboard_pwd = public.GetRandomString(16)
        set_token = public.GetRandomString(16)
        set_max_pool_count = 50
        str_log_level = "info"
        set_log_max_days = 30
        str_log_file = "/var/log/frps.log"
        str_log_file_flag = "enable"
        set_tcp_mux = 16337
        set_kcp_bind_port=15443
        data = """  
bindPort = {set_bind_port}
kcpBindPort = {set_kcp_bind_port}
webServer.addr = "0.0.0.0"
webServer.port = "{set_dashboard_port}"
webServer.user = "{set_dashboard_user}"
webServer.password = "{set_dashboard_pwd}"
dashboardPwd = "{set_dashboard_pwd}"
vhostHTTPPort = {set_vhost_http_port}
vhostHTTPSPort = {set_vhost_https_port}
log.file = "{str_log_file}"
log.level = "{str_log_level}"
log.maxDays = {set_log_max_days}
auth.token = "{set_token}"
maxPoolCount = {set_max_pool_count}
tcpmuxHTTPConnectPort  = {set_tcp_mux}
        """.format(set_bind_port=set_bind_port, set_vhost_http_port=set_vhost_http_port, set_vhost_https_port=set_vhost_https_port, set_dashboard_port=set_dashboard_port,
                   set_dashboard_user=set_dashboard_user, set_dashboard_pwd=set_dashboard_pwd, set_token=set_token, set_max_pool_count=set_max_pool_count, str_log_level=str_log_level,
                   set_log_max_days=set_log_max_days, str_log_file=str_log_file, str_log_file_flag=str_log_file_flag, set_tcp_mux=set_tcp_mux)
        public.writeFile('/usr/local/frps/frps.toml', data)
        if 'CentOS' in public.get_os_version():
            public.ExecShell('chkconfig --add frps')
            public.ExecShell('chkconfig --level 2345 frps on')
        else:
            public.ExecShell('update-rc.d frps defaults')
        public.ExecShell('/etc/init.d/frps start')
        return public.returnMsg(True, '安装成功!')

    def set_frps_config(self, get):
        try:
            data = dict(get.__dict__)
            config = toml.loads(public.readFile(self.config_path))
            for k, v in data.items():
                if k in ['bind', 'http', 'https', 'webserverport', 'tcpmux', 'kcp', 'action', 's', 'a', 'data', 'serveraddr', 'name']:
                    continue
                if '{' in v:
                    v = json.loads(v)
                    for k1, v1 in v.items():
                        if type(v1) == str and v1.isdigit():
                            v[k1] = int(v1)
                if type(v) == str and v.isdigit():
                    v = int(v)
                config[k] = v
            public.writeFile(self.config_path, toml.dumps(config))
            return public.returnMsg(True, '修改成功!')
        except:
            return traceback.format_exc()
            return public.returnMsg(False, '修改失败!')

    def get_frps_info(self, get=None):
        status = public.ExecShell("/etc/init.d/frps status")
        status = status[0].find("is running") != -1
        config = self.get_frps_config()
        try:
            get_bind_port = config['webServer']['port']
            server_addr = 'http://' + public.get_server_ip() + ':' + get_bind_port
        except:
            server_addr = ''
        msg = "重新安装frps"
        if os.path.exists('/usr/local/frps/frps.ini'):
            msg = "新版本中，采用<span style='color:red;'>新格式</span>配置文件，请<span style='color:red;'>重新安装</span>！"

        data = {
            'status': status,
            'server_addr': server_addr,
            'install_status': 1 if os.path.exists('/usr/local/frps/frps') else 0,
            "ps":msg
        }
        return data

    def frps_server_admin(self, get):
        if not hasattr(get, 'status') or not get.status:
            return public.returnMsg(False, '参数错误')
        if get['status'] == 'start':
            config = self.get_frps_config()
            for k, v in config.items():
                if k in ['bindPort', 'vhostHTTPPort', 'vhostHTTPSPort', 'kcpBindPort', 'tcpmuxHTTPConnectPort']:
                    if self.check_port(v):
                        return public.returnMsg(False, '{}端口被占用!请修改该端口或者关闭运行在该端口的进程后重试'.format(v))
            res = public.ExecShell("/etc/init.d/frps start")
        elif get['status'] == 'stop':
            res = public.ExecShell("/etc/init.d/frps stop")
        elif get['status'] == 'restart':
            res = public.ExecShell("/etc/init.d/frps restart")
        else:
            return public.returnMsg(False, '参数错误')
        if res[1]:
            return public.returnMsg(False, res[1])
        return public.returnMsg(True, '操作成功')

    def check_os_bit(self):
        try:
            # 尝试使用 platform 模块获取 Python 解释器的架构信息
            machine = platform.machine().lower()
            if "arm" in machine:
                return "arm"
            elif "amd" in machine or "x86_64" in machine:
                return "amd64"
        except Exception as e:
            print(f"Error using platform module: {e}")

        try:
            # 尝试使用命令行获取系统的整体架构信息
            result = subprocess.run(['uname', '-m'], stdout=subprocess.PIPE)
            system_architecture = result.stdout.decode('utf-8').strip().lower()
            if "arm" in system_architecture:
                return "arm"
            elif "amd" in system_architecture or "x86_64" in system_architecture:
                return "amd64"
        except Exception as e:
            print(f"Error using subprocess: {e}")
        return "Error"

    def get_frpc_config(self):
        if os.path.exists('/usr/local/frpc/frpc'):
            return True, public.readFile('/usr/local/frpc/frpc.toml')
        return False, ''

    def install_frpc(self, get=None):
        if os.path.exists('/usr/local/frpc/frpc.toml') and os.path.exists('/etc/init.d/frpc') and os.path.exists('/usr/local/frpc/frpc'):
            return public.returnMsg(False, 'FRPC已经安装了!')
        os_bit = self.check_os_bit()
        if 'Error' in os_bit:
            return public.returnMsg(False, '暂不支持该系统!')
        name = 'frp_0.52.3_linux_{}'.format(os_bit)
        public.ExecShell('wget -O /www/server/panel/plugin/wlfrp/{}.tar.gz https://frps.wlphp.com/download/src/frp/{}.tar.gz'.format(name, name))
        public.ExecShell('tar -zxvf /www/server/panel/plugin/wlfrp/{}.tar.gz -C /usr/local/'.format(name))
        public.ExecShell('mv /usr/local/{} /usr/local/frpc'.format(name))
        public.ExecShell('rm -f /www/server/panel/plugin/wlfrp/{}.tar.gz'.format(name))
        public.ExecShell('wget -O  /etc/init.d/frpc https://frps.wlphp.com/download/src/frp/frpc.init')
        public.ExecShell('chmod +x /etc/init.d/frpc')
        public.ExecShell('cp /etc/init.d/frpc  /usr/bin/frpc')
        data = """
serverAddr = "193.123.85.124"
serverPort = 7000
auth.token = "查看:frps.wlphp.com"
[[proxies]]
name = "ssh"
type = "tcp"
localIP = "127.0.0.1"
localPort = 22
remotePort = 6000               
[[proxies]]
name = "test-http"
type = "http"
localIP = "127.0.0.1"
localPort = 8000
customDomains = ["1.134.wlphp.com"]
[[proxies]]
name = "test_htts2http"
type = "https"
customDomains = ["2.134.wlphp.com"]
[proxies.plugin]
type = "https2http"
localAddr = "127.0.0.1:80"
# HTTPS 证书相关的配置
crtPath = "./server.crt"
keyPath = "./server.key"
hostHeaderRewrite = "127.0.0.1"
requestHeaders.set.x-from-where = "frp"
"""
        public.writeFile('/usr/local/frpc/frpc.toml', data)
        if 'CentOS' in public.get_os_version():
            public.ExecShell('chkconfig --add frpc')
            public.ExecShell('chkconfig --level 2345 frpc on')
        else:
            public.ExecShell('update-rc.d frpc defaults')
        public.ExecShell('ln -sf /etc/init.d/frpc /usr/bin/frpc')
        return public.returnMsg(True, '安装成功!')

    def frpc_server_admin(self, get):
        if not hasattr(get, 'status') or not get.status:
            return public.returnMsg(False, '参数错误')
        if get['status'] == 'start':
            res = public.ExecShell("/etc/init.d/frpc start")
        elif get['status'] == 'stop':
            res = public.ExecShell("/etc/init.d/frpc stop")
        elif get['status'] == 'restart':
            res = public.ExecShell("/etc/init.d/frpc restart")
        else:
            return public.returnMsg(False, '参数错误')
        if res[1]:
            return public.returnMsg(False, res[1])
        if 'failed' in res[0]:
            return public.returnMsg(False, '启动失败，请检查配置文件')
        return public.returnMsg(True, '启动成功！')

    def get_frpc_info(self, get=None):
        status = public.ExecShell("/etc/init.d/frpc status")
        status = status[0].find("is running") != -1
        data = {'status': status,
                'install_status': 1 if os.path.exists('/usr/local/frpc/frpc') else 0,
                'ps': "重新安装frpc"
                }
        return data

    def reinstall_frps(self,get=None):
        public.ExecShell('rm -rf /usr/local/frps')
        public.ExecShell('rm -rf /etc/init.d/frps')
        public.ExecShell('rm -rf /usr/bin/frps')
        return self.install_frps()

    def reinstall_frpc(self,get=None):
        public.ExecShell('rm -rf /usr/local/frpc')
        public.ExecShell('rm -rf /etc/init.d/frpc')
        public.ExecShell('rm -rf /usr/bin/frpc')
        return self.install_frpc()