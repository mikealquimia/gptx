# -*- coding: utf-8 -*-
{
    'name': "charge_on_calls",
    'summary': """ """,
    'description': """ """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account'],
    'data': [
        'security/payment_collection_permitions.xml',
        'security/ir.model.access.csv',
        'views/payment_collection_views.xml',
        'views/account_invoice_views.xml',
        'reports/payment_collection_report_pdf.xml',
        'reports/payment_collection_report.xml',
    ],
}