# ##################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Utils 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##################################################################################
{ 
    "name": "Kwantify DMS Utils",
    "summary": """Utility Features""",
    "version": '1.0',  
    "category": 'Extra Tools',   
    
    "website": "",
   
    "depends": [
        "base_setup"
    ],
    "data": [
        "actions/ir_attachment.xml",
        "views/ir_attachment.xml",
        "views/mixins_groups.xml",
        "views/res_config_settings.xml",
        "template/assets.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "sequence": 3,    
    "auto_install": False,
    "application": False,
    "installable": True,
    "post_load": "_patch_system",
}
