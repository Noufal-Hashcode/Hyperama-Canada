# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS-Order Line Report',
    "author": "MKR",
    'version': '1.2',
    'category': 'pos',
    'sequence': 6,
    'summary': 'POS Orderline Report',
    'description': """

.
""",
    'depends': ['point_of_sale', 'product','base','account_reports','account_accountant'],
    'data': [

        'report/report.xml',
        'wizard/product_report_wiz.xml',
        'views/product_order_report.xml',
        'security/ir.model.access.csv'


    ],
    'assets': {

        'point_of_sale._assets_pos': [
            # 'hc_pos_customisation/static/src/xml/pos.xml',
            # 'hc_pos_orderline_report/static/src/js/order_line.js',
            # 'hc_pos_orderline_report/static/src/xml/order_line.xml'
            # 'hc_pos_customisation/static/src/app/js/models.js',

        ],



    },
    'installable': True,
    'auto_install': True,

    'license': 'LGPL-3',
}
