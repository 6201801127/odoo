# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Stock Request kanban',
    'version': '11.0.1.2.0',
    'category': 'Reporting',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'author': 'Creu Blanca, Eficent, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'summary': 'Adds a stock request order, and takes stock requests as lines',
    'depends': ['stock_request','base','barcodes'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_stock_inventory_kanban_views.xml',
        'wizard/wizard_stock_request_kanban_views.xml',
        'wizard/wizard_stock_request_order_kanban_views.xml',
        'views/stock_request_order_views.xml',
        'views/stock_request_kanban_views.xml',
        'views/stock_inventory_kanban_views.xml',
        'views/stock_request_menu.xml',
        'data/stock_request_sequence_data.xml',
        'report/report_paper_format.xml',
        'report/stock_request_kanban_templates.xml',

    ],
    'installable': True,
    'application': False,
}
