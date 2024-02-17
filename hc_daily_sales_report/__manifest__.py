# -*- coding: utf-8 -*-

{
    'name': "hc_daily_sales_report",
    'version': '17.0.1.0.1',
    'depends': ['point_of_sale'],
    'author': "frs",
    'website': "http://www.hashcodeit.com",
    'category': '',
    'description': """
    hc_daily_sales_report
    """,

    'data': [
        'security/ir.model.access.csv',
        'data/division_data.xml',
        'views/product_division_view.xml',
        'views/product_template_view.xml',
        'wizard/sales_daily_report_wizard.xml',
        'reports/report.xml',
        'reports/sales_report_template.xml',
        'data/daily_sale_crone.xml',
        'data/group.xml',

    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
