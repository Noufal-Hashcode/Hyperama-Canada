# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS-Customer Payment Restriction',
    "author": "JJ",
    'version': '17.0.1.0.0',
    'category': 'pos',
    'sequence': 6,
    'summary': 'Customer Payment Restriction',
    'description': """

.
""",
    'depends': ['point_of_sale'],
    'data': [

        # 'views/product_category.xml',

    ],
    'assets': {

        'point_of_sale._assets_pos': [
            'hc_pos_payment_restriction/static/src/static/js/payment.js',
        ],



    },
    'installable': True,
    'auto_install': True,

    'license': 'LGPL-3',
}
