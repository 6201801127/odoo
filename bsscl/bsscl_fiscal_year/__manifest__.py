# -*- encoding: utf-8 -*-
{
    'name': 'BSSCL Fiscal Year / बिहार शरीफ स्मार्ट सिटी लिमिटेड वित्तीय वर्ष',
    'version': '14.0.0.1',
    'category': 'BSSCL / बिहार शरीफ स्मार्ट सिटी लिमिटेड',
    'summary': 'BSSCL Fiscal year and account period creation /  बिहार शरीफ स्मार्ट सिटी लिमिटेड वित्तीय वर्ष और खाता अवधि निर्माण',
    'description': """
        This module provide feature to define fiscal year and period for company 
        and link with journal entry and journal items / यह मॉड्यूल कंपनी के लिए वित्तीय वर्ष और अवधि को परिभाषित करने की सुविधा प्रदान करता है
        और जर्नल प्रविष्टि और जर्नल आइटम के साथ लिंक करें
    """,
    'author': 'BSSCL / बिहार शरीफ स्मार्ट सिटी लिमिटेड',
    'website': 'http://www.csm.tech',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_year_view.xml',
    ],
    'installable': True,
    'application': True,
}
