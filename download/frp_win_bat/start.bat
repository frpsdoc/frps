@echo off

REM 启动FRPC客户端，并指定TOML配置文件
start "" frpc.exe -c frpc.toml

REM 提示用户客户端已启动
echo frpc start ok ...
pause