# Copyright 2016 Onestein (<http://www.onestein.eu>)
# Copyright 2018 Tecnativa - David Vidal
# Copyright 2020 Abdou Nasser
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Prevent export, delete and print",
    "summary": "Allows admin to restrict export, delete and print button for a specific user",
    "category": "Extra Tools",
    "images": ['images/undraw_throw_away_ldjd.png'],
    "version": "1.0.0",
    'price': 18,
    'currency': 'USD',
    "author": 'Abdou Nasser',
    "support": "abdounasser202@gmail.com",
    "website": "https://formation-odoo.blogspot.com",
    "license": "AGPL-3",
    "depends": ["web"],
    "data": [
        'security/groups.xml',
        'templates/assets.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
