#!/usr/bin/env python

# Copyright 2015 The Meson development team

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

from mesonwrap import wrapdb, wrapcreator


class WrapUpdater:
    def __init__(self, dbdir='.'):
        self.dbdir = dbdir
        self.db = wrapdb.WrapDatabase(self.dbdir, True)

    def close(self):
        self.db.close()

    def update_db(self, project_name, repo_url, branch):
        wrap = wrapcreator.make_wrap(project_name, repo_url, branch)
        self.db.insert(project_name, branch,
                       wrap.revision, wrap.wrapfile_content, wrap.zip)


def main(prog, args):
    parser = argparse.ArgumentParser(prog)
    parser.add_argument('--dbdir', default='.')
    parser.add_argument('project')
    parser.add_argument('repo_url')
    parser.add_argument('branch')
    args = parser.parse_args(args)
    m = WrapUpdater(dbdir=args.dbdir)
    m.update_db(args.project, args.repo_url, args.branch)
