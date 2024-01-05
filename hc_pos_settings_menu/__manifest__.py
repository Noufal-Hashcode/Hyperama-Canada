{
    'name': 'POS Settings Menu',
    "author": "",
    'version': '17.0.0.2',
    'category': 'point_of_sale',
    'sequence': 6,
    'summary': 'POS Settings Menu',
    'description': """
.
""",
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/point_of_sale_view.xml'
    ],
    'assets': {},
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
