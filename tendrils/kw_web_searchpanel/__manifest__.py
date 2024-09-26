###################################################################################
#
#    Copyright (C) 2018 MuK IT GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 'muk_web_utils',
###################################################################################

{
    'name': 'Kwantify Search Panel',
    'summary': 'Kanban Search Panel',
    'version': '12.0.1.2.0',
    'category': 'Kwantify/Extra Tools',
    'license': 'AGPL-3',
    'author': 'Kwantify',
    'website': 'https://www.csm.tech',
    'live_test_url': '',
    'contributors': [
       
    ],
    'depends': [
        
    ],
    'data': [
        "template/assets.xml",
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}