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

import getopt
import sys
from funpdbe_client.control import Control
from funpdbe_client.client import Client
from funpdbe_client.user import User
from funpdbe_client.schema import Schema


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:m:i:r:f:hd", [
            "user=",
            "pwd=",
            "mode=",
            "pdb_id=",
            "resource=",
            "path=",
            "help",
            "debug"])
    except getopt.GetoptError as err:
        print("Error: %s" % err)
        sys.exit(2)

    if opts:
        Control(opts, Client(), Schema(), User()).run()


if __name__ == '__main__':
    main()
