# -*- coding: utf-8 -*-
{
    'name': "Indent - STPI",
    'summary': """ Indent - STPI""",
    'description': """
    """,
    'author': "Dexciss Technology Pvt Ldt (RGupta)",
    'website': "http://www.dexciss.com",
    'description': """

    """,
    'category': 'hrms',
    'version': '12.0.1',
    'depends': ['base','hr','product'],
    'data': [
        'security/ir.model.access.csv',
        'security/indent_security.xml',
        # 'wizard/select_child_block.xml',
        # 'data/ltc_mode_demo_data.xml',
        'views/indent_request.xml',
        'views/indent_configuration.xml',
        'views/issue_request.xml',
        'views/stock_log_book.xml',
        'wizard/multi_approve.xml',
        'wizard/confirmation.xml',
        'views/stock_item.xml',
        # 'report/ltc_report.xml',


    ],

    # 'demo': [
    #     'data/previous_occupation_organisation_type_demo.xml',
    #
    # ],


    'installable': True,
    'application': True,
    'auto_install': False,
    'demo': True

}