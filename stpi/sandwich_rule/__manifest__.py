# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Sandwich Rule For HR Leave",
    'summary': """
        Calculate leave as per sandwich Rules.
        Updated by 21/10/20 by smehata
    """,
    'description': """
         Transition by SMehata
         Updated by 21/10/19 by smehata
         This module allows HR to apply Sandwich rule when employees apply
         for leave and is coming under the rule where employee has taken 
         leave in midst of two working days. 
    """,
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'license': "AGPL-3",
    'category': 'Leave',
    'version': '12.0.2',
    'depends': ['hr',
                'hr_holidays',
                'resource'
    ],
    'data': [
        'views/hr_holiday.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
