#!/usr/bin/python3
# coding=utf-8

import sqlite3
# from numpy import inf

# 定义数据库连接
global _conn
# 定义游标
global _cursor


def init_sqlite():
    # 定义数据库连接
    global _conn
    # 定义游标
    global _cursor

    # 初始化数据库
    _conn = sqlite3.connect("sqlite.db")
    # 连接数据库
    _cursor = _conn.cursor()
    print("sqlite connected.")


def release_sqlite():
    # 定义数据库连接
    global _conn
    # 定义游标
    global _cursor

    # 释放数据库资源
    try:
        if _cursor is not None:
            # 关闭游标
            _cursor.close()
            # except shodan.APIError as e:
    finally:
        if _conn is not None:
            # 关闭数据库连接
            _conn.close()
            print("database released.")


# 判断IP是否已经存在于ip_all表中
def ip_exists(ip: str):
    # 定义数据库连接
    global _conn

    # 查询
    c1 = _conn.cursor()
    c1.execute("SELECT ip FROM ip_all where ip='{}'".format(ip))

    # 返回一条
    db_ip_value = c1.fetchone()

    # result = None
    if db_ip_value is None:
        result = False
    else:
        result = True

    c1.close()

    return result


def main():
    try:

        # 临时的编号
        i_update = 0
        i_ignore = 0

        # 初始化数据库连接
        init_sqlite()

        # 定义数据库连接
        global _conn
        # 定义游标
        global _cursor

        # 从表shodan_data中读取数据，解析，存入表ip_all
        _cursor = _conn.cursor()
        _cursor.execute("SELECT result_matches FROM shodan_data ORDER BY id asc")

        # 循环
        for row in _cursor:

            result_matches = eval(row[0])

            # 遍历list
            for result in result_matches:

                # 国家编码
                country = str(result["location"]["country_code3"])
                # 忽略部分IP，避免误伤
                if country == "CHN" or country == "HKG" or country == "TWN":
                    print("found [", country, "], ignore")
                    i_ignore = i_ignore + 1
                    pass

                else:
                    # 数据来源
                    source = "shodan"

                    # 解析
                    ip = str(result["ip_str"])
                    port = str(result["port"])
                    org = str(result["org"])
                    hosts = str(result["hostnames"])
                    datetime = str(result["timestamp"])

                    os_temp = result.get("redis")
                    if os_temp:
                        os_temp = os_temp.get("server")

                    if os_temp:
                        os_temp = os_temp.get("os")
                    else:
                        os_temp = "n/a"

                    os = str(os_temp)

                    redis_version_temp = result.get("redis")
                    if redis_version_temp:
                        redis_version_temp = redis_version_temp.get("server")

                    if redis_version_temp:
                        redis_version_temp = redis_version_temp.get("redis_version")

                    redis_version = str(redis_version_temp)

                    separator = " | "

                    print(format(i_update) + separator + country + separator + "ip: " +
                          ip + ":" + port + separator + "redis: " + redis_version + separator + "os: " + os + separator + "org: " + org + separator + hosts + separator + datetime)

                    # 执行插入或更新

                    # 如果存在此记录，则更新
                    if ip_exists(ip):
                        # 更新记录
                        c1 = _conn.cursor()
                        c1.execute(
                            "update ip_all set ref_info=?,ip=?,port=?,country=?,datetime=?,source=?,org=?,hosts=?,redis_version=?,os=? where ip=?",
                            (str(result), ip, port, country, datetime, source, org, hosts, redis_version, os, ip))
                        c1.close()

                    else:
                        # 如果不存在此记录，则插入记录
                        c1 = _conn.cursor()
                        c1.execute(
                            "insert into ip_all (ref_info,ip,port,country,datetime,source,org,hosts,redis_version,os) values (?,?,?,?,?,?,?,?,?,?)",
                            (str(result), ip, port, country, datetime, source, org, hosts, redis_version, os))
                        c1.close()

                    _conn.commit()

                    # 临时编号+1
                    i_update = i_update + 1

                    pass

        # 释放数据库
        release_sqlite()

        print("update: [{}]".format(i_update))
        print("ignore: [{}]".format(i_ignore))
        print("total records: [{}] , all done!".format(i_update + i_ignore))

    except Exception as e:
        print("Error: {}".format(e))


if __name__ == '__main__':
    # 执行主函数
    main()
