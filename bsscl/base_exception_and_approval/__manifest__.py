# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Approval Management',
 'version': '12.0.2',
 'category': 'BSAP',
 'summary': """This module provide an abstract model to manage customizable
  exceptions to be applied on different models (sale order, invoice, ...)""",
 'author': "CSM Technologies",
'description':"""
                 updated by CSM Technologies 13/08/19
                 
                 
                 """,
 'website': 'http://www.csm.tech',
 'depends': ['base','base_setup','resource','mail','web'],
 'license': 'AGPL-3',
 'data': [
     'security/base_exception_security.xml',
     'security/ir.model.access.csv',
     'data/squence.xml',
     'views/assets.xml',
     'wizard/base_exception_confirm_view.xml',
     'views/base_exception_view.xml',
     'views/approval_views.xml',
     'views/approval_menu.xml',

 ],
 'installable': True,
 }
