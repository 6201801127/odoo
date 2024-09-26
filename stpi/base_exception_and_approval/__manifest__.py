# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Approval Management',
 'version': '12.0.2',
 'category': 'Generic Modules',
 'summary': """This module provide an abstract model to manage customizable
  exceptions to be applied on different models (sale order, invoice, ...)""",
 'author': "Dexciss Technology Pvt Ltd(Ayush)",
'description':"""
                 updated by smehata 13/08/19
                 updated by smehata 27/3/19
                 
                 """,
 'website': 'http://www.Dexciss.com',
 'depends': ['base','base_setup','resource','mail','web','groups_inherit'],
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
