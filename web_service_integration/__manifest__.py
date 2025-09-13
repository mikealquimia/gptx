# -*- encoding: UTF-8 -*-

{
    'name': 'Factura Electrónica',
    'summary': """Web service integrado con Infile S.A""",
    'version': '11.0.1.0.',
    'description': """Factura Electrónica para Guatemala""",
    'author': 'Osmin Cano --> osmincano@gmail.com',
    'maintainer': 'Osmin Cano',
    'website': 'https://www.pitaya.tech',
    'category': 'account',
    'depends': ['base','base_setup','account','document','account_cancel'],
    'license': 'AGPL-3',
    'data': [
                'views/api_view.xml',
                'views/account_journal_view.xml',
                'views/account_invoice_view.xml',
            ],
    'demo': [],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,


}
