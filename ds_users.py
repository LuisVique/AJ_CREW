
from ds_connect import Ds_connect

class Ds_users(object):

    def __init__(self, u_data):
        self.u_data = u_data
        self.ds_server = Ds_connect(u_data)

    def ds_register(self, message):

        ret = self.ds_server.ds_connect("REGISTER " + message)
        if ret.split()[0] == 'NOK':
            return None

        return ret

    def ds_query(self, message):

        ret = self.ds_server.ds_connect("QUERY " + message)

        if ret.split()[0] == 'NOK':
            return None

        return ret

    def ds_listUsers(self):

        ret = self.ds_server.ds_connect("LIST_USERS")
        if ret.split()[0] == 'NOK':
            return None

        userList = sorted(ret[16:].split('#'))

        return userList

    def ds_quit(self):

        ret = self.ds_server.ds_connect("QUIT")
        if ret.split()[0] == 'NOK':
            return None

        return ret
