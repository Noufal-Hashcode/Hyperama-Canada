# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Scrap Customisation',
    "author": "MKR",
    'version': '1.1',
    'category': 'pos',
    'sequence': 6,
    'summary': 'valuation layer in scrap form',
    'description': """

.
""",
    'depends': ['stock', 'product','base'],
    'data': [

        'views/scrap_form.xml',

    ],
    'assets': {


    },
    'installable': True,
    'auto_install': True,

    'license': 'LGPL-3',
}
