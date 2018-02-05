#-*-coding=utf-8*-
__author__ = 'ZivLi'

import MySQLdb
import re
import time

class IDentity:
    def __int__(self, txt_string):
        self.string = txt_string
        self.App_name = []
        self.option = []
        self.host_name = []

    def get_App_name(self):
        pattern = re.compile(r'(.+?)###')
        self.App_name.append(re.findall(pattern, self.string)[0])

    def get_Opt_Host(self):
        pattern = re.compile(r'###(.+?)Host字段为: (.+)')
        self.option.append(re.findall(pattern, self.string)[0][0])
        self.host_name.append(re.findall(pattern, self.string)[0][1])

    def insert_SQL(self, imei_idfa):
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='identity', charset='utf8')
        cur = conn.cursor
        alter_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        for i in range(len(self.App_name)):
            cur.execute("insert into " + str(imei_idfa) + " values('%s', '%s', '%s', '%s')" % (self.App_name[i], self.option[i], self.host_name[i], alter_time))
        cur.close()
        conn.commit()
        conn.close()

def read_file(file_path):
    f = open(file_path)
    file_strings = f.readlines()
    return file_strings

def save_file(fstring, imei_idfa):
    ident = IDentity(fstring)
    ident.get_App_name()
    ident.get_Opt_Host()
    ident.insert_SQL(imei_idfa)


if __name__ == '__main__':

    save_file(fstring, 'idfa')

# def get_App(string):
#     pattern = re.compile(r'(.+?)###')
#     App_name = re.findall(pattern, string)[0]
#     return App_name
#
#
# def get_Opt_Host(string):
#     pattern = re.compile(r'###(.+?)Host字段为：(.+)')
#     opt_string = re.findall(pattern, string)[0][0]
#     host = re.findall(pattern, string)[0][1]
#     return opt_string, host

#
# def read_idfa_file(file_path):
#     App = []
#     Options = []
#     Host = []
#     f = open(file_path)
#     file_strings = f.readlines()
#     for i in range(len(file_strings)):
#         App.append(get_App(file_strings[i]))
#         opt, host = get_Opt_Host(file_strings[i])
#         Options.append(opt)
#         Host.append(host)
#
#     return App, Options, Host
#
#
# def insert_mySQL_idfa(App, Options, Host):
#     conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='identity', charset='utf8')
#     cur = conn.cursor()
#     alter_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
#     for i in range(len(App)):
#         cur.execute("insert into idfa values('%s', '%s', '%s', '%s')" % (App[i], Options[i], Host[i], str(alter_time)))
#     cur.close()
#     conn.commit()
#     conn.close()
#
#
# def read_imei_file(file_path):
#     App = []
#     Options = []
#     Host = []
#     f = open(file_path)
#     file_strings = f.readlines()
#     for i in range(len(file_strings)):
#         App.append(get_App(file_strings[i]))
#         opt, host = get_Opt_Host(file_strings[i])
#         Options.append(opt)
#         Host.append(host)
#
#     return App, Options, Host
#
#
# def insert_mySQL_imei(App, Options, Host):
#     conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='identity', charset='utf8')
#     cur = conn.cursor()
#     alter_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
#     for i in range(len(App)):
#         cur.execute("insert into imei values('%s', '%s', '%s', '%s')" % (App[i], Options[i], Host[i], str(alter_time)))
#     cur.close()
#     conn.commit()
#     conn.close()
#
# def IDFA(idfa_file_path):
#     App, Options, Host = read_idfa_file(idfa_file_path)
#     insert_mySQL_idfa(App, Options, Host)
#
# def IMEI(idfa_file_path):
#     App, Options, Host = read_imei_file(idfa_file_path)
#     insert_mySQL_imei(App, Options, Host)
