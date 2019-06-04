
from ds_connect import Ds_connect

class Ds_users(object):

    ds_server = Ds_connect()

    def ds_register(self, message):

        ret = self.ds_server.ds_connect("REGISTER" + message)
        if ret.split()[0] is "NOK":
            return None

        return ret

    def ds_query(self):

        ret = self.ds_server.ds_connect("QUERY" + message)
        if ret.split()[0] is "NOK":
            return None

        return ret

    def ds_listUsers(self):

        ret = self.ds_server.ds_connect("LIST_USERS")
        if ret.split()[0] is "NOK":
            return None

        userList = sorted(ret[16:].split('#'))
        return userList

    def ds_quit(self):

        ret = self.ds_server.ds_connect("QUIT")
        if ret.split()[0] is "NOK":
            return None

        return ret
