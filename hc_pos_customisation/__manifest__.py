# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS-Custom Receipt',
    "author": "MKR",
    'version': '1.2',
    'category': 'pos',
    'sequence': 6,
    'summary': 'Dide product in receipt based on category and Add a button in POS to sync Shopify sales orders',
    'description': """
        This module extends the Odoo Point of Sale (POS) module by adding a custom button to the Product Screen.
        The button allows users to fetch and synchronize sales orders from Shopify into the POS system.
        When clicked, it retrieves Shopify order data via an RPC call,
        which creates new POS orders, and populates them with the corresponding products and customer details.
        The button is conditionally displayed only for POS configurations named 'Retailer',
        ensuring targeted functionality for specific POS setups.
    """,
    'depends': ['point_of_sale', 'product','base','pos_sale'],
    'data': [

        'views/product_category.xml',

    ],
    'assets': {

        'point_of_sale._assets_pos': [
            'hc_pos_customisation/static/src/xml/pos.xml',
            'hc_pos_customisation/static/src/app/js/models.js',
            'hc_pos_customisation/static/src/js/pos_screen_button.js',
            # 'hc_pos_customisation/static/src/js/pos_ticket_screen.js',
            'hc_pos_customisation/static/src/xml/shopify_order_sync_button.xml',
            # 'hc_pos_customisation/static/src/xml/ticket_screen_extend.xml'

        ],
        },
    'installable': True,
    'auto_install': True,

    'license': 'LGPL-3',
}
