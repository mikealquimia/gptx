# -*- coding: utf-8 -*-
{
    'name': "Movimientos de caja",
    'summary': """
        Registra todos los movimientos realizado en caja
        """,
    'description': """
        Genera el reporte del detalle de los movimientos realizados en caja
    """,
    'author': "Pitaya Tech",
    'website': "http://www.pitaya.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'l10n_gt', 'account_tax_python', 'account_cancel', 'product', 'purchase'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/report.xml',        
        'views/account_payment_invoice_form_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
}