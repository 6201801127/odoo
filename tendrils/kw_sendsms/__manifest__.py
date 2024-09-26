{
    'name': "Kwantify SMS",
    'version': '0.1',
    'author': "Kwantify",
    'category': 'Kwantify/Tools',
    'summary': 'You can use multiple gateway for multiple sms template to send SMS.',
    'description': 'Allows you to send SMS to the mobile no.',
    'website': "https://www.csm.tech",
    
    'depends': ['base', 'web', 'mail'],
    
    'data': [
        'security/ir.model.access.csv',
        'view/send_sms_view.xml',
        # 'view/ir_actions_server_views.xml',
        'view/sms_track_view.xml',
        'view/gateway_setup_view.xml',
        'wizard/sms_compose_view.xml',
        'view/sms_log_view.xml',
        'view/sms_scheduler.xml',
        'view/kw_sendsms_menu_items.xml',
        'data/kw_gateway_setup.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
}
