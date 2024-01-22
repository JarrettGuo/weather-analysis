# -*- coding: utf-8 -*-
# Description: MongoDB数据库操作封装
# UpdateNote: 新增统计集合总量;新增分页查询;
import sys
import hashlib
import pymongo


class MongoDBHelper(object):
    def __init__(self, db='spider_db', uri='mongodb://localhost:27017/'):
        '''
             初始化连接
        '''
        self.connect_client = pymongo.MongoClient(uri)
        self.mydb = self.connect_client[db]  # 连接指定数据库

    def str_to_md5(self, parm_str):
        if isinstance(parm_str, str):
            # 如果是unicode先转utf-8
            parm_str = parm_str.encode("utf-8")
        m = hashlib.md5()
        m.update(parm_str)
        return m.hexdigest()

    def insert_collection(self, collection_name, value):  # 单个插入
        mycol = self.mydb[collection_name]
        if mycol.find_one({'_id': value.get('_id')}):
            mycol.update_one({"_id": value.get("_id")}, {'$set': value})
            print('update successful')
        else:
            mycol.insert_one(value)
            print('insert successful')

    def insert_batch_collection(self, collection_name, value_list):  # 批量插入
        mycol = self.mydb[collection_name]

        insert_list = []
        for value in value_list:
            if mycol.find_one({'_id': value.get('_id')}):
                mycol.update_one({"_id": value.get("_id")}, {'$set': value})
            else:
                insert_list.append(value)

        if insert_list:
            mycol.insert_many(insert_list)
        print('update data: {} record, insert data: {} record'.format(len(value_list) - len(insert_list),
                                                                      len(insert_list)))

    def select_one_collection(self, collection_name, search_col=None):  # 获取一条数据
        '''search_col：只能是dict类型,key大于等于一个即可，也可为空
        可使用修饰符查询：{"name": {"$gt": "H"}}#读取 name 字段中第一个字母 ASCII 值大于 "H" 的数据
        使用正则表达式查询：{"$regex": "^R"}#读取 name 字段中第一个字母为 "R" 的数据'''
        my_col = self.mydb[collection_name]
        try:
            result = my_col.find_one(search_col)  # 这里只会返回一个对象，数据需要自己取
            return result
        except TypeError as e:
            print('查询条件只能是dict类型')
            return None

    def select_all_collection(self, collection_name, search_col=None, limit_num=sys.maxsize, sort_col='None_sort',
                              sort='asc'):
        '''search_col：只能是dict类型,key大于等于一个即可，也可为空
        可使用修饰符查询：{"name": {"$gt": "H"}}#读取 name 字段中第一个字母 ASCII 值大于 "H" 的数据
        使用正则表达式查询：{"$regex": "^R"}#读取 name 字段中第一个字母为 "R" 的数据
        limit_num:返回指定条数记录，该方法只接受一个数字参数(sys.maxsize:返回一个最大的整数值)'''
        my_col = self.mydb[collection_name]
        try:
            if sort_col == False or sort_col == 'None_sort':
                results = my_col.find(search_col).limit(limit_num)  # 这里只会返回一个对象，数据需要自己取
            else:
                sort_flag = 1
                if sort == 'desc':
                    sort_flag = -1
                results = my_col.find(search_col).sort(sort_col, sort_flag).limit(limit_num)  # 这里只会返回一个对象，数据需要自己取
            result_all = [i for i in results]  # 将获取到的数据添加至list
            return result_all
        except TypeError as e:
            print('查询条件只能是dict类型')
            return None

    def select_page_query(self, collection_name, query_filter=None, page_size=10, page_no=1):
        '''
        pymongo 分页查询
        :param collection_name:
        :param query_filter:
        :param page_size:
        :param page_no:
        :return:
        '''
        my_col = self.mydb[collection_name]
        try:
            skip = page_size * (page_no - 1)
            results = my_col.find(query_filter).limit(page_size).skip(skip)
            page_result = [i for i in results]
            return page_result
        except TypeError as e:
            print('查询出错')
            return None

    def select_count_all(self, collection_name):
        '''
        统计集合中文档总量
        :param collection_name:
        :return:
        '''
        my_col = self.mydb[collection_name]
        try:
            result = my_col.count()
            return result
        except TypeError as e:
            print('统计出错')
            return 0

    def update_one_collecton(self, collection_name, search_col, update_col):
        '''该方法第一个参数为查询的条件，第二个参数为要修改的字段。
            如果查找到的匹配数据多余一条，则只会修改第一条。
            修改后字段的定义格式： { "$set": { "alexa": "12345" } }'''
        my_col = self.mydb[collection_name]
        try:
            relust = my_col.update_one(search_col, update_col)
            return relust
        except TypeError as e:
            print('查询条件与需要修改的字段只能是dict类型')
            return None

    def update_batch_collecton(self, collection_name, search_col, update_col):
        '''批量更新数据'''
        my_col = self.mydb[collection_name]
        try:
            relust = my_col.update_many(search_col, update_col)
            return relust
        except TypeError as e:
            print('查询条件与需要修改的字段只能是dict类型')
            return None

    def delete_one_collection(self, collection_name, search_col):  # 删除集合中的文档
        my_col = self.mydb[collection_name]
        try:
            relust = my_col.delete_one(search_col)
            return relust
        except TypeError as e:
            print('查询条件与需要修改的字段只能是dict类型')
            return None

    def delete_batch_collection(self, collection_name, search_col):  # 删除集合中的多个文档
        '''删除所有 name 字段中以 F 开头的文档:{ "name": {"$regex": "^F"} }
        删除所有文档：{}'''
        my_col = self.mydb[collection_name]
        try:
            relust = my_col.delete_many(search_col)
            return relust
        except TypeError as e:
            print('查询条件与需要修改的字段只能是dict类型')
            return None

    def drop_collection(self, collection_name):
        '''删除集合，如果删除成功 drop() 返回 true，如果删除失败(集合不存在)则返回 false'''
        my_col = self.mydb[collection_name]
        result = my_col.drop()
        return result

    def get_connections(self):  # 获取所有的connections
        return self.mydb.list_collection_names()

    def close_connect(self):
        self.connect_client.close()
        return 'mongo连接已关闭'
