#!/usr/bin/python3
# coding=utf-8

import nmap
import time
import sqlite3

# 要扫描的端口号
global _ports
_ports = "6379"

# 临时文件名称
global _temp_filename
_temp_filename = "attack_ip_temp.txt"

# 定义数据库连接
global _conn
# 定义查询用途游标
global _cursor_query
# 定义更新用途游标
global _cursor_update
# 定义查询是否重复IP用途游标
global _cursor_exists


def init_sqlite():
    # 定义数据库连接
    global _conn
    # 定义查询用途游标
    global _cursor_query
    # 定义更新用途游标
    global _cursor_update
    # 定义查询是否重复IP用途游标
    global _cursor_exists

    # 初始化数据库
    _conn = sqlite3.connect("sqlite.db")
    # 连接数据库
    _cursor_query = _conn.cursor()
    _cursor_update = _conn.cursor()
    _cursor_exists = _conn.cursor()

    print("sqlite connected.")


def release_sqlite():
    # 定义数据库连接
    global _conn
    # 定义查询用途游标
    global _cursor_query
    # 定义更新用途游标
    global _cursor_update
    # 定义查询是否重复IP用途游标
    global _cursor_exists

    # 释放数据库资源
    try:
        if _cursor_query is not None:
            # 关闭游标
            _cursor_query.close()

        if _cursor_update is not None:
            # 关闭游标
            _cursor_update.close()

        if _cursor_exists is not None:
            # 关闭游标
            _cursor_exists.close()


    finally:
        if _conn is not None:
            # 关闭数据库连接
            _conn.close()
            print("database released.")


# 判断IP是否已经存在于redis_active表中
def ip_exists(ip: str):
    # # 定义数据库连接
    # global _conn

    # 定义查询用途游标
    global _cursor_exists

    # 查询
    _cursor_exists.execute("SELECT ip FROM redis_target where ip='{}'".format(ip))

    # 返回一条
    if _cursor_exists.fetchone() is None:
        return False
    else:
        return True


def main():
    # 要扫描的端口号
    global _ports
    # 临时文件名称
    global _temp_filename

    # 定义数据库连接
    global _conn
    # 定义查询用途游标
    global _cursor_query
    # 定义更新用途游标
    global _cursor_update

    try:
        nm = nmap.PortScanner()

        # 临时的编号
        i_active = 0
        i_quiet = 0

        i_online_count = 0
        i_offline_count = 0

        # 初始化数据库连接
        init_sqlite()

        # 每页数据数量
        page_size = 4
        # 页码
        page_index = 0

        # 翻页循环的flag
        flag = True

        # 从redis_active表中，分页读取IP和端口，用nmap扫描
        while flag:
            # 分页查询
            _cursor_query.execute(
                "SELECT ip FROM redis_active ORDER BY ip asc limit ? offset ?*?"
                , (page_size, page_index, page_size))

            rows = _cursor_query.fetchall()

            print("scanning hosts: ", len(rows))

            if rows is not None and len(rows) > 0:

                str_ips = str(rows).replace("[('", "")
                str_ips = str_ips.replace("',)]", "")
                str_ips = str_ips.replace("',), ('", "\r\n")

                # print(rows)
                f = open(_temp_filename, 'w')
                f.write(str_ips)
                f.close()

                # 在这里用nmap扫描ip和port
                try:
                    # 配置nmap扫描参数
                    # scan_raw_result = nm.scan(hosts=network_prefix, arguments='-n -A -sS -sV -p 6942')
                    scan_raw_result = nm.scan(
                        arguments='T4 -A -n -sS -sV -p {0} -iL {1}'.format(_ports, _temp_filename))
                    # scan_raw_result = nm.scan(arguments='-iL {0} -A -n -sS -sV -p {1}'.format("test.txt",_ports))

                    i_online_count = i_online_count + len(scan_raw_result['scan'].items())
                    i_offline_count = len(rows) - len(scan_raw_result['scan'].items()) + i_offline_count

                    # 分析扫描结果
                    for host, result in scan_raw_result['scan'].items():
                        if result['status']['state'] == 'up':

                            # ip地址
                            # host
                            # 操作系统信息
                            os_result = ""
                            # 端口状态
                            port_state = ""
                            # redis版本
                            redis_version = ""
                            # redis端口
                            redis_port = ""

                            print('#' * 17 + 'Host:' + host + '#' * 17)
                            # print('-' * 20 + '操作系统猜测' + '-' * 20)

                            try:
                                for os in result['osmatch']:
                                    print('操作系统为：' + os['name'] + ' ' * 3 + '准确度为：' + os['accuracy'])
                                    os_result = os['name']
                                    # 这里只取一个准确度最高的os名称
                                    break
                            except:
                                pass

                            try:
                                for port in result['tcp']:
                                    try:
                                        # print('-' * 17 + 'TCP服务器详细信息' + '[' + str(idno) + ']' + '-' * 17)
                                        redis_port = str(port)
                                        print('TCP端口号：' + str(redis_port))

                                        try:
                                            port_state = result['tcp'][port]['state']
                                            print('状态：' + result['tcp'][port]['state'])
                                        except:
                                            pass
                                        # try:
                                        #     print('原因：' + result['tcp'][port]['reason'])
                                        # except:
                                        #     pass
                                        # try:
                                        #     print('额外信息：' + result['tcp'][port]['extrainfo'])
                                        # except:
                                        #     pass
                                        # try:
                                        #     print('名字：' + result['tcp'][port]['name'])
                                        # except:
                                        #     pass
                                        try:
                                            redis_version = result['tcp'][port]['version']
                                            print('版本：' + result['tcp'][port]['version'])
                                        except:
                                            pass
                                        # try:
                                        #     print('产品：' + result['tcp'][port]['product'])
                                        # except:
                                        #     pass
                                        # try:
                                        #     print('CPE：' + result['tcp'][port]['cpe'])
                                        # except:
                                        #     pass
                                        # try:
                                        #     print('脚本：' + result['tcp'][port]['script'])
                                        # except:
                                        #     pass

                                        # 因为只扫描一个端口，所以扫描一次就退出
                                    except:
                                        pass
                                    finally:
                                        break
                            except:
                                pass

                            # ip地址
                            # host
                            # 操作系统信息
                            # os_result = ""
                            # 端口状态
                            # port_state = ""
                            # redis版本
                            # redis_version = ""
                            # redis端口
                            # redis_port = ""

                            try:
                                # if port is not None and port in "6379":
                                if port_state == "open" and redis_port is not None and redis_port in _ports:
                                    # 格式化成2016-03-20 11:45:39形式
                                    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                                    # 如果存在此记录，则更新
                                    if ip_exists(host):
                                        # 更新记录
                                        _cursor_update.execute(
                                            "update redis_target set port=?, redis_version=?, os=?, datetime=? where ip=?",
                                            (port, redis_version, os_result, datetime, host))

                                    else:
                                        # 如果不存在此记录，则插入记录
                                        _cursor_update.execute(
                                            "insert into redis_target (ip, port, redis_version, os, is_exploited, datetime) values (?,?,?,?,0,?)",
                                            (host, port, redis_version, os_result, datetime))

                                    _conn.commit()

                                    # 临时编号+1
                                    i_active = i_active + 1

                                else:
                                    i_quiet = i_quiet + 1

                            except Exception as e:
                                print("Error: {}".format(e))
                                pass

                        else:
                            # 扫描结果是空或者超时之类的
                            i_quiet = i_quiet + 1

                except Exception as e:
                    # network is unreachable.
                    if "network is unreachable." == str(e):
                        # 如果只是无法访问，则忽略
                        print("Error: {}".format(e))
                        pass

                    else:
                        # 其他错误打印出来
                        print("Error: {}".format(e))

            else:
                flag = False
                pass

            # 翻页，再查询
            page_index = page_index + 1

            print("hosts online:[{0}], offline:[{1}]".format(i_online_count, i_offline_count), )
            print("redis port {0} active:[{1}], quiet:[{2}]".format(_ports, i_active, i_quiet))

        print("total, hosts online:[{0}], offline:[{1}]".format(i_online_count, i_offline_count), )
        print("total, redis port {0} active:[{1}], quiet:[{2}]".format(_ports, i_active, i_quiet))

        print("total records: [{}] , all done!".format(i_active + i_quiet + i_offline_count))

        # 释放数据库
        release_sqlite()

        # 清空临时扫描IP文件
        f_cls = open(_temp_filename, 'w')
        f_cls.write("")
        f_cls.close()

    except Exception as e:
        print("Error: {}".format(e))


if __name__ == '__main__':
    main()

# 鸣谢
# https://blog.csdn.net/Tong_T/article/details/80603378
