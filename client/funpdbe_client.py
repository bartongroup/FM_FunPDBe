#!/usr/bin/env python3

import getpass
import requests
import getopt
import sys

"""
FunPDBe Deposition Client
Created on 16th January 2018
Author: Mihaly Varadi
"""


class User(object):

    def __init__(self, user=None, pwd=None):
        self.user_name = user
        self.user_pwd = pwd
        if not self.user_name:
            self.user_name = self.set_user()
        if not self.user_pwd:
            self.user_pwd = self.set_pwd()

    @staticmethod
    def set_user():
        return input("funpdbe user name: ")

    @staticmethod
    def set_pwd():
        return getpass.getpass("funpdbe password: ")


class Api(object):

    def __init__(self):
        # TODO
        self.url_base = "http://127.0.0.1:8000/funpdbe_deposition"
        self.entries_url = "%s/entries/" % self.url_base


class Client(object):

    def __init__(self, user=None, pwd=None):
        self.user = User(user, pwd)
        self.api = Api()

    def get_one(self, pdb_id):
        pass

    def get_all(self):
        r = requests.get(self.api.entries_url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)

    def post_one(self, json_data):
        pass

    def delete_one(self):
        pass



# c = Client()
# c.get_all()


"""
user calls python funpdbe_client.py
optionally with user name and password

if no user name and password, then the first thing after welcome message is prompt for
user name and password

after that, options can be chosen:
* get all your entries ()
* get one entry by pdb_id (arg: pdb_id)
* delete one entry (arg: pdb_id)
* post one entry (arg: path)
* batch post (arg: path)
* exit ()

need to have validation against schema when posting
"""

def main():
    user = None
    pwd = None
    mode = None
    pdbid = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:m:i:h", [
            "user=",
            "pwd=",
            "mode=",
            "pdbid="
            "help"])
    except getopt.GetoptError as err:
        print("Error: %s" % err)
        sys.exit(2)
    for option, value in opts:
        if option in ["-u", "--user"]:
            user = value
        elif option in ["-p", "--pwd"]:
            pwd = value
        elif option in ["-m", "--mode"]:
            if value in ("get", "post", "delete"):
                mode = value
        elif option in ["-i", "--pdbid"]:
            pdbid = value
        elif option in ["-h", "--help"]:
            # TODO
            pass
        else:
            assert False, "unhandled option"

    if mode == "get":
        # TODO reverse the logic
        if not pdbid:
            c = Client(user=user, pwd=pwd)
            c.get_all()

if __name__ == "__main__":
    main()