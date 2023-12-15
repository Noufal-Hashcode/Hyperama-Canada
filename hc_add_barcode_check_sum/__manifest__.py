{
    'name': 'Add EAN13 Barcode Check Sum',
    'author': "nbl",
    'maintainer': 'nbl',
    'website': 'https://hashcodeit.com/',
    'version': '17.0.1.0',
    'support': 'info@hashcodeit.com',
    'category': '',
    'summary': 'Add EAN13 Barcode Check Sum',
    'description': """ """,
    'depends': ['stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/customer_type_view.xml'
    ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}


{
    'name': 'Add EAN13 Barcode Check Sum',
    "author": "",
    'version': '17.0.0.0',
    'category': 'stock',
    'sequence': 6,
    'summary': 'Add EAN13 Barcode Check Sum',
    'description': """""",
    'depends': ['stock', 'product'],
    'data': [
        'views/product_product.xml',
    ],
    'assets': {},
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
