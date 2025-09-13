# -*- coding: utf-8 -*-
{
    'name': "sale_credit_auth",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sale'],

    'data': [
        'security/gp_credit_auth.xml',
        'views/sale_order_views.xml',
    ],
}