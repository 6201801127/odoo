{
    'name': "bsscl_court_case",

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

    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/court_case_create_views.xml',
        'views/court_location_views.xml',
        'views/court_case_type.xml',
        'views/court_case_sub_type_views.xml',
        'views/manage_court_case_views.xml',
        
    ]
}