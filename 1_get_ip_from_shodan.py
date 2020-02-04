#!/usr/bin/python3
# coding=utf-8

import time
import sqlite3
import shodan

# shodan api
_SHODAN_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxx"

# 调用shodan API查询
_api = shodan.Shodan(_SHODAN_API_KEY)

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


# 查询数据库，返回shodan api查询的总数
# 用于判断是否重复搜索，避免shodan多花钱
def get_result_total(key_word: str, page_index: int):
    # 定义数据库连接
    global _conn
    # 定义游标
    global _cursor

    # 查询
    _cursor = _conn.cursor()
    _cursor.execute("SELECT result_total FROM shodan_data WHERE search_key_word=? and search_page_index=?",
                    (key_word, page_index))
    # 返回一条
    result = _cursor.fetchone()

    # print("searching ",key_word,", ",page_index,", result: ",result)
    # 返回None或者数据库中shodan api查询到的总数
    return result


# shodan api 分页搜索
def shodan_search(key_word: str, page_index: int):
    # 是否重复搜索，先看数据库中是否已经查询过此关键词（key_word）和页码（page_index）
    result_total_in_DB = get_result_total(key_word, page_index)
    if result_total_in_DB is None:
        # 不重复，可以搜索

        try:

            # search_key_word
            search_key_word = key_word

            # search_page_index
            search_page_index = page_index

            # Search Shodan
            results_api = _api.search(search_key_word, page=search_page_index)

            # 结果集存储进数据库

            # result_matches
            result_matches = results_api["matches"]


            # 查询到的数据>0，则写入数据库
            # result_total
            if results_api["total"] is not None and len(result_matches) > 0:

                try:

                    result_total_api = int(results_api["total"])

                    if result_total_api > 0:

                        # datetime
                        # 格式化成2016-03-20 11:45:39形式
                        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                        # 打印结果集
                        # print(len(format(results)))

                        # Show the results
                        print("#keyword:[", format(search_key_word), "], page:[", format(search_page_index),
                              "], results:[",
                              format(result_total_api), "], datetime: ", format(datetime))

                        # 定义数据库连接
                        global _conn
                        # 定义游标
                        global _cursor

                        # 写入数据库
                        _cursor = _conn.cursor()
                        _cursor.execute("insert into shodan_data (id,search_key_word,search_page_index,result_matches,"
                                        "result_total,datetime) values (NULL,?,?,?,?,?)",
                                        (search_key_word, search_page_index,
                                         str(result_matches), result_total_api, datetime))
                        _conn.commit()

                        print(">>keyword:[", format(search_key_word), "], page:[", format(search_page_index),
                              "], results:[",
                              format(result_total_api), "], stored at: ", format(datetime))

                        # 翻页，再次调用
                        shodan_search(search_key_word, search_page_index + 1)

                    else:
                        print("result_total: {}".format(result_total_api)," , done.")
                        pass

                except Exception as e:
                    print("result_total Error: {}".format(e))

                    pass

            else:
                # 如果数据为None或 <= 0 则什么也不做
                pass

        except shodan.APIError as e:
            print("Error: {}".format(e))
            # 如果超时，再执行一次

            if "timed out" in format(e) or "Unable to connect to Shodan" in format(e):
                # The search request timed out or your query was invalid.
                print("page:[",format(search_page_index),"] timeout, request again...")
                shodan_search(key_word, page_index)
            elif "Insufficient query credits" in format(e) or "wait for the monthly limit to reset" in format(e):
                # Insufficient query credits, please upgrade your API plan or wait for the monthly limit to reset
                print("page:[",format(search_page_index),"] , Hmmm... no money...")
            else:
                print("unknown error!")


    else:
        # 重复了
        # 但是，可能是程序中断造成的，查看数据的总条数是多少
        # 如果(page_index*100)<result_total，则page_index加1
        if  (page_index * 100) < int(result_total_in_DB[0]):
            # 页码+1,再次搜索
            shodan_search(key_word, page_index + 1)

        else:
            # 如果等于或大于result_total，什么都不做
            pass

    return


def main():
    print('init...')

    # 初始化数据库连接
    init_sqlite()

    # 默认搜索的关键词
    # key_word = "redis_version:4.0.1"
    key_word = "product:redis"

    print("Searching keyword: [",key_word,"]...")


    # 默认查询第一页
    page_index = 1

    # 开始批量搜索，获得shodan的信息
    shodan_search(key_word, page_index)

    # 释放数据库
    release_sqlite()

    print("All done!")


if __name__ == '__main__':
    # 执行主函数
    main()
