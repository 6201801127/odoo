{
    "name": "Kwantify Theme",
    "summary": "Theme designed by CSM Technology",
    'description': "Kwantify ERP application theme",
    "category": "Theme/Kwantify",
    "website": "https://www.csm.tech",
    "author": "CSM Technologies",
    'application': True,
    'installable': True,
    'auto_install': False,
    "depends": [
        'web','mail','website','hr','auth_signup'
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'views/about_us.xml',
        'views/homepage.xml',
        # 'views/footer.xml',
        'views/tendril_footer.xml',
        'views/homepage_assets.xml',
        'views/assets.xml',
		'views/res_company_view.xml',
        'views/res_users.xml',
		'views/users.xml',
        # 'views/sidebar.xml',
        'views/login.xml',
        'views/forgot_password.xml',
        'views/web_tree_dynamic_colored_field.xml',
        'views/login_assets.xml',
        'views/ir_model_views.xml',
        'views/menu_icons.xml',
        'views/forbidden_page.xml',
        
    ],
    'qweb': [
        'static/src/xml/apps.xml',
        'static/src/xml/form_view.xml',
        'static/src/xml/navbar.xml',
        'static/src/xml/settings.xml',
    ],
}

