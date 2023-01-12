```
[common]
server_addr =119.8.103.209
server_port = 7000
token = 群内公告获取
 
[Nas]   
#ssh连接
type = tcp         
local_ip = 127.0.0.1 
local_port = 22     
remote_port = 5000  




[http_wl]   
type = http    			
local_ip = 127.0.0.1   
local_port = 80          
use_compression = true
use_encryption = true
custom_domains = 把自己的域名解析到server_addr这个ip地址


[http_wl2] 
type = http
local_ip = 192.168.31.55
local_port = 8080
use_compression = true
use_encryption = true
custom_domains = 2.frpvip.wlphp.com



[https_wl1] 
type = https
custom_domains = 11.frpvip.wlphp.com
plugin = https2http
plugin_local_addr = 127.0.0.1:80


plugin_crt_path = ./cert/fullchain.pem
plugin_key_path = ./cert/privkey.pem
plugin_host_header_rewrite = 127.0.0.1
plugin_header_X-From-Where = frp

```