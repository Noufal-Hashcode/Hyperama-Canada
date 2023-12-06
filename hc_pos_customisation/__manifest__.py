# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS-Custom Receipt',
    "author": "MKR",
    'version': '1.1',
    'category': 'pos',
    'sequence': 6,
    'summary': 'hide product in receipt based on category',
    'description': """

.
""",
    'depends': ['point_of_sale', 'product','base'],
    'data': [

        'views/product_category.xml',

    ],
    'assets': {

        'point_of_sale._assets_pos': [
            'hc_pos_customisation/static/src/xml/pos.xml',
            'hc_pos_customisation/static/src/app/js/models.js',
            # 'hc_pos_customisation/static/src/app/js/OrderLine.js',

        ],

    },
    'installable': True,
    'auto_install': True,

    'license': 'LGPL-3',
}
