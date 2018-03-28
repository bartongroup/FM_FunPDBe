#!/usr/bin/env python3

# Copyright 2018 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the
# License.


class User(object):
    """
    User object to handle prompts if no user name
    or password were provided when running the Client()
    """

    def __init__(self, user=None, pwd=None):
        self.user_name = user
        self.user_pwd = pwd

    def set_user(self):
        """
        Set user name
        """
        self.user_name = self.set_attribute(self.user_name, "funpdbe user name: ")

    def set_pwd(self):
        """
        Set password
        """
        self.user_pwd = self.set_attribute(self.user_pwd, "funpdbe password: ")

    def set_attribute(self, attribute, text):
        """
        Set attribute to user input
        :param attribute:
        :param text:
        :return:
        """
        value = attribute
        if not value:
            while not value:
                value = input(text)
        return value

