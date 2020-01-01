# Copyright 2015 The Meson development team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from flask import render_template

from wrapweb import api, jsonstatus
from wrapweb.app import APP


def response_to_json(resp):
    return json.loads(resp.get_data().decode('utf-8'))


@APP.route('/', methods=['GET'])
def index():
    j = response_to_json(api.get_projectlist())
    return render_template(
        'projects.html',
        projects=j['projects'])


@APP.route('/<project>', methods=['GET'])
def project_info(project):
    j = response_to_json(api.get_project_info(project))
    return render_template(
        'project.html',
        title='%s - Wrap DB' % project,
        project=project,
        resp=j)


# This is called when user opens get_wrap handler and CSS override is not
# present.
@APP.route('/favicon.ico')
def favicon():
    return jsonstatus.error(404, 'Favicon not found')
