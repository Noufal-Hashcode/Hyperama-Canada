# -*- coding: utf-8 -*-


from odoo import fields, models, api, _

import logging
import io
import json
import time
from odoo.http import request


class ProducrSaleReport(models.Model):
    _name = "product.sale.report"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    default_code = fields.Char(related='product_id.default_code')
    barcode = fields.Char(related='product_id.barcode')

    ordered_qty = fields.Integer()
    invoiced_qty = fields.Integer()
    total_sales = fields.Float(
        'Total Sales',
    )
    total_cost =fields.Float('Total Cost' )
    gross_profit =fields.Float('GP' )

