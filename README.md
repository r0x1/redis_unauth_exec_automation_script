## redis_unauth_exec_automation_script

redis_unauth_exec 自动化脚本

5个可独立运行的脚本，可以同时运行，通过sqlite数据库交互数据。可以做个计划任务，间隔几小时运行一次，查询到新的可用ip和端口数据，就自动入侵检测一次。

1. 从shodan上获取 'product:redis' 数据，存入shodan_data表
2. 从shodan_data表读取数据，解析字符串，存入ip_all表
3. 从ip_all表中读取数据，用python-masscan扫描是否开放6379端口，是的话存入redis_active表
4. 从redis_active表中读取数据，用python-nmap扫描操作系统信息，扫描redis版本，扫描成功的话存入redis_target表
5. 从redis_target表中读取数据，判断redis的版本，如果是4.x-5.x，用pymetasploit攻击，如果攻击成功，将redis_target表的is_exploited字段值改为1 （初始值为0）。
