#!/usr/bin/python3
# coding=utf-8

import time
import sqlite3
import masscan

# 要扫描的端口号
global _ports
_ports = "6379"

# 临时文件名称
global _temp_filename
_temp_filename = "active_ip_temp.txt"

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
    _cursor_exists.execute("SELECT ip FROM redis_active where ip='{}'".format(ip))

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

        mas = masscan.PortScanner()

        # 临时的编号
        i_active = 0
        i_quiet = 0

        # 初始化数据库连接
        init_sqlite()

        # 每页数据数量
        page_size = 1000
        # page_size = 10

        # 页码
        page_index = 0

        # 翻页循环的flag
        flag=True

        # 从ip_all表中，分页读取IP和端口，用masscan扫描
        while flag:
            # 分页查询
            # flag = _cursor_query.execute(
            #     "SELECT ip,port,country,datetime,source,org,hosts,redis_version,os,ref_info FROM ip_all ORDER BY ip asc limit ? offset ?*?"
            #     , (page_size, page_index, page_size))

            _cursor_query.execute(
                "SELECT ip FROM ip_all ORDER BY ip asc limit ? offset ?*?"
                , (page_size, page_index, page_size))

            rows = _cursor_query.fetchall()

            print("list rows count: ",len(rows))

            if rows is not None and len(rows) > 0:

                str_ips = str(rows).replace("[('","")
                str_ips = str_ips.replace("',)]","")
                str_ips = str_ips.replace("',), ('","\r\n")


                # print(rows)
                f = open(_temp_filename, 'w')
                f.write(str_ips)
                f.close()

                # 在这里用masscan扫描ip和port
                try:
                    mas.scan('', ports=_ports, arguments='--includefile {} --max-rate 1000'.format(_temp_filename))

                except Exception as e:
                    # network is unreachable.
                    if  "network is unreachable." == str(e):
                        # 如果只是无法访问，则忽略
                        print("Error: {}".format(e))
                        pass

                    else:
                        # 其他错误打印出来
                        print("Error: {}".format(e))

                # 尝试读或扫描结果
                dict_scan_result = None

                try:
                    dict_scan_result = mas.scan_result
                except Exception as e:
                    # Do a scan before trying to get result !
                    if "Do a scan before trying to get result !" == str(e):
                        # 如果只是没扫到开放的端口，则忽略
                        # print("Error: {}".format(e))
                        pass
                    else:
                        # 其他错误打印出来
                        print("Error: {}".format(e))

                # 扫描结果是open还是close，还是什么
                if dict_scan_result is not None:
                    # 尝试解析ip和端口号，然后存储入数据库
                    try:

                        for ip, item_result in dict_scan_result["scan"].items():
                            # 端口
                            port = None
                            for port_item in item_result["tcp"]:
                                # 因为只扫描一个端口，所以循环一次就离开
                                port = str(port_item)
                                break

                            # if port is not None and port in "6379":
                            if port is not None and port in _ports:
                                # 格式化成2016-03-20 11:45:39形式
                                datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                                # 如果存在此记录，则更新
                                if ip_exists(ip):
                                    # 更新记录
                                    _cursor_update.execute(
                                        "update redis_active set port=?, datetime=? where ip=?", (port, datetime, ip))

                                else:
                                    # 如果不存在此记录，则插入记录
                                    _cursor_update.execute("insert into redis_active (ip, port, datetime) values (?, ?, ?)", (ip, port, datetime))

                                _conn.commit()

                                # 临时编号+1
                                i_active = i_active + 1
                                # 写入数据库


                    except Exception as e:
                        print("Error: {}".format(e))
                        pass

                    # 页码+1

                else:
                    # 扫描结果是空或者超时之类的
                    i_quiet = i_quiet + 1

            else:
                flag = False
                pass


            # 翻页，再查询
            page_index = page_index + 1


        print("active hosts: [{}]".format(i_active))
        print("quiet hosts: [{}]".format(i_quiet))
        print("total records: [{}] , all done!".format(i_active+i_quiet))

        # 释放数据库
        release_sqlite()

        #清空临时扫描IP文件
        f_cls = open(_temp_filename, 'w')
        f_cls.write("")
        f_cls.close()

    except Exception as e:
        print("Error: {}".format(e))



if __name__ == '__main__':
    # 执行主函数
    main()

