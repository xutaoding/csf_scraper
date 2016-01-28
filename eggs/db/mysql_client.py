# encoding: utf8
import MySQLdb


class MySQLClient:
    def __init__(self, _db_host, _db_user, _db_passwd, _db_db):
        self.__host = _db_host
        self.__user = _db_user
        self.__passwd = _db_passwd
        self.__db = _db_db
        self.__conn = None

        try:
            self.connect()
        except:
            raise IOError('数据库连接失败')

    def connect(self):
        if self.__conn is not None:
            try:
                self.__conn.close()
                self.__conn = None
            except MySQLdb.Error as e:
                print '`connect` error:', e
        self.__conn = MySQLdb.connect(host=self.__host, user=self.__user, passwd=self.__passwd, db=self.__db, charset='utf8')

    def disconnect(self):
        try:
            self.__conn.close()
            self.__conn = None
        except MySQLdb.Error as e:
            self.__conn = None
            print '` disconnect` error:', e

    def check(self, _sql):
        """
            check something in db or not
        """
        if self.__conn is None:
            self.connect()
        else:
            self.ping()
        cur = self.__conn.cursor()
        c = cur.execute(_sql)
        if c > 0:
            return True
        return False

    def count(self, table):
        """
            return the num of the 'table' 's record
        """
        _sql = 'SELECT COUNT(*) FROM ' + table
        if self.__conn is None:
            self.connect()
        else:
            self.ping()
        cur = self.__conn.cursor()
        c = cur.execute(_sql)
        if c > 0:
            data = cur.fetchone()
            return data[0]
        return 0

    @classmethod
    def parameter_check(cls, query, args):
        if not isinstance(args, (tuple, list)):
            raise ValueError('`args` type is error.')
        if query.count('%s') + query.count('%d') != len(args):
            raise ValueError('Number of parameters is fail.')

    def get(self, query, *args):
        """
            input: your select sql, e.g. "SELECT * FROM table_name WHERE id > 10"
            return: one row
        """
        if self.__conn is None:
            self.connect()
        else:
            self.ping()
        try:
            self.__class__.parameter_check(query, args)
            cur = self.__conn.cursor()
            c = cur.execute(query, args)
            if c > 0:
                return cur.fetchone()
        except MySQLdb.Error as e:
            print '`get` data error:', e

    def query(self, query, *args):
        """
            input: your select sql, e.g. "SELECT * FROM table_name WHERE id > 10"
            return: the data
        """
        if self.__conn is None:
            self.connect()
        else:
            self.ping()

        try:
            self.__class__.parameter_check(query, args)
            cur = self.__conn.cursor()
            c = cur.execute(query, args)
            if c > 0:
                return cur.fetchall()
        except MySQLdb.Error as e:
            print '`query` data error:', e

    def ping(self):
        """check mysql server has gone away or not, if gone away, reconnet server"""
        try:
            self.__conn.ping()
        except Exception as e:
            self.connect()
            print '`ping` database error:', e

    def execute(self, query, *args):
        """
            function could create, update, insert data to mysql
            args: is tuple or list,`insert` need values, `update` also to.

        """
        if self.__conn is None:
            self.connect()

        try:
            self.__class__.parameter_check(query, args)
            cursor = self.__conn.cursor()
            cursor.execute(query, args)
            self.__conn.commit()
        except Exception, e:
            print 'execute sql statement error:', e


if __name__ == '__main__':
    m = MySQLClient("192.168.250.208", "ada_user", "ada_user", "ada-fd")
    m.connect()

    sql_ = """select close_price from equity_price where secu_code=%s order by trade_date DESC limit 1000"""
    print sql_
    res = m.get(sql_, *('600201_SH_EQ', ))
    print res[0] * 100
    print type(res)


