{
    'name': "bsscl_accounting",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "CSM Technologies",
    'website': "http://www.csm.tech",

    'category': 'BSSCL',
    'version': '0.1',

    'depends': ['account','base','base_accounting_kit','base_account_budget'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'data/discipline_category.xml',
        'views/account_inherit.xml',
       
    ],

    'demo': [
        # 'data/hr_resume_demo.xml'
        ],

    # 'qweb': [
    #     'static/src/xml/resume_templates.xml','
    #     'static/src/xml/skills_templates.xml',
    # ],
}

