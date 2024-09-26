# -*- coding: utf-8 -*-


{
    'name': 'Dynamic Workflow Builder',
    'version': '1.0',
    'sequence': '10',
    'category': 'Kwantify/Extra Tools',
    'author': 'CSM Technologies',
    'website': 'https://www.csm.tech',
    'summary': 'Dynamic Workflow Builder',
    'description': """
            Dynamic Workflow Builder
            ========================
            * You can build dynamic workflow for any model.
    """,
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'views/menu.xml',
        'wizards/views/odoo_workflow_refuse_wizard_view.xml',
        'wizards/views/odoo_workflow_update_wizard_view.xml',
        'views/odoo_workflow_view.xml',
        'views/ir_actions_server_view.xml',
        # 'views/set_authority_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
