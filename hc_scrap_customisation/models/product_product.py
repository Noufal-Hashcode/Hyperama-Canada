# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_round, groupby


class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_type = fields.Selection([('local', 'Local'), ('import', 'Import')], string='Purchase Type', required=True,
                                     default='local')
