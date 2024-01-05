from Aops_Api_Auto_Test.utils.MysqlUtil import ql


class QueryDataBase:
    ql.connect()
    def query_group_name(self, host_group_name):
        sql = "select host_group_name from host_group where host_group_name='{}'".format(host_group_name)
        query_result = ql.fetchall(sql)
        return query_result[0]['host_group_name']

    def delete_host_group(self, host_group_name):
        sql = "delete from host_group where host_group_name='{}';".format(host_group_name)
        print("sql: ", sql)
        return ql.exec(sql)

    def query_host_info(self, field):
        sql = "select host_id, host_name,host_ip from host where host_id='{host_id}' or host_ip='{host_ip}' or host_name='{host_name}';"\
            .format(host_id=field,host_ip=field,host_name=field)
        ql.connect()
        query_result = ql.fetchall(sql)
        return query_result[0]

    def delete_host(self, field):
        sql = "delete from host where host_ip='{}'".format(field)
        print("sql:" ,sql)
        return ql.exec(sql)

    def batch_delete_host(self):
        sql = "delete from host where host_name like 'batch%'"
        ql.exec(sql)

    def delete_repo(self,repo_name):
        sql = "delete from repo where repo_name='{}'".format(repo_name)
        ql.exec(sql)

    def query_repo(self,repo_name):
        sql = "select * from repo where repo_name='{}'".format(repo_name)
        query_result = ql.fetchall(sql)
        return query_result[0]

