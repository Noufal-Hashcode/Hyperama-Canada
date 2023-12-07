# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_round, groupby


class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_type =  fields.Selection(related='product_tmpl_id.purchase_type', readonly=False)
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_type = fields.Selection([('local', 'Local'), ('import', 'Import')], string='Purchase Type', required=True,
                                     default='local')
