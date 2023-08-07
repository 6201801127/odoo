{
    'name': "Test Employee",
    'description':"Test model for employee",
    'sequence':1,
    'depends':['base','sale','mail', 'board','web_google_maps'],
    'installable':True,
    'application':True,
    'version': '14.0.1',
    'license': 'AGPL-3',
    'category':'sale',
    'author':'Ajay Kumar Ravidas',
    'website':'https://www.ask.com',
    'data':[
        'security/security.xml',
        'security/security_rules.xml',
        'security/ir.model.access.csv',
        'views/language_wiz_view.xml',
        'views/training_wiz_view.xml',
        'views/payslip_wiz_view.xml',
        'views/employee_view.xml',
        'views/city_view.xml',
        'views/country_view.xml',
        'views/state_view.xml',
        'views/training_view.xml',
        'views/language_view.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/employee_payslip.xml',
        'views/delegation_view.xml',
        'views/serveraction.xml',
        'data/emp_sequence.xml',
        'data/templates.xml',
        'data/employee.city.csv',
        'data/rescity.xml',
        'data/blood_group.xml',
        'report/employee_detail_report_template.xml',
        'report/employee_detail_report.xml',
        'views/dashboard.xml',
        
        
    ],
    'price': 49.99,
    'currency': 'USD',
    'images': ['static/description/test_emp.jpg'],



    
    
}