# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Import Purchase',
    "author": "",
    'version': '17.0.0.0',
    'category': 'stock',
    'sequence': 6,
    'summary': 'Import Purchase',
    'description': """
.
""",
    'depends': ['stock', 'product', 'purchase'],
    'data': [
        'views/picking_type_view.xml',
        'views/purchase_view.xml',
    ],
    'assets': {  },
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
