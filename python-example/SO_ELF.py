#__author__ == 'ZivLi'

import struct

class SO_Header:
    def __int__(self):
        self.e_ident = ""
        self.e_ident = 0
        self.e_machine = ""
        self.e_version = ""
        self.e_entry = 0
        self.e_phoff = 0
        self.e_shoff = 0
        self.e_flags = ""
        self.e_ehsize = 0
        self.e_phentsize = 0
        self.e_phnum = 0
        self.e_shentsize = 0
        self.e_shnum = 0
        self.e_shstrndx = 0