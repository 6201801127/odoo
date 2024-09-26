# -*- coding: utf-8 -*-
#############################################################################
#
#    CSM Technologies
#
#    Copyright (C) 2019-TODAY CSM Technologies(<https://csm.tech>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


{
    'name': "Kwantify Restrict Concurrent User Login",
    'version': '1.0.1',
    'summary': 'Restrict concurrent sessions, User force logout, Automatic session expiry',
    "description": """Restrict concurrent sessions, User force logout, Automatic session expiry, 
                      restrict user login, session expiry, session, user session, force logout,
                      automatic expiry""",
    'author': 'Kwantify',
    'company': 'CSM Technologies',
    'maintainer': 'Kwantify',
    'website': "https://csm.tech",
    'depends': ['base', 'kw_sendsms', 'kwantify_theme', 'kw_onboarding'],
    'category': 'Kwantify/Security',
    'data': [
        'data/scheduler_data.xml',
        'data/mail_template.xml',
        'data/sms_template.xml',
        'views/res_users_view.xml',
        'views/kw_otp_template.xml',
        'views/templates.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
