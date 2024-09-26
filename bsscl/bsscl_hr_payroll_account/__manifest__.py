# -*- coding:utf-8 -*-

{
    'name': 'HR Payroll Accounting (BSSCL) / एचआर पेरोल लेखा (बिहार शरीफ स्मार्ट सिटी लिमिटेड)',
    'category': 'Web Application',
    'author': 'BSSCL / बिहार शरीफ स्मार्ट सिटी लिमिटेड',
    'version': '14.0.4.0.0',
    'sequence': 1,
    'license': 'LGPL-3',
    'website': 'https://www.odoomates.tech',
    'live_test_url': 'https://www.youtube.com/watch?v=0kaHMTtn7oY',
    'summary': 'Generic Payroll system Integrated with Accounting / सामान्य पेरोल सिस्टम लेखांकन के साथ एकीकृत',
    'description': """Generic Payroll system Integrated with Accounting. / सामान्य पेरोल सिस्टम लेखांकन के साथ एकीकृत।""",
    'depends': [
        'bsscl_hr_payroll',
        'account'
    ],
    'data': [
        'views/hr_payroll_account_views.xml'
    ],
    'demo': [],
    'test': ['../account/test/account_minimal_test.xml'],
    'images': ['static/description/banner.png'],
    'application': True,
}
