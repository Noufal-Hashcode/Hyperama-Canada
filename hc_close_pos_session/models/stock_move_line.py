# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import float_round, groupby


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.depends('quantity', 'product_uom_id')
    def _compute_quantity_product_uom(self):
        print("########_compute_quantity_product_uom############")
        for line in self:
            qty = line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id,
                                                        rounding_method='HALF-UP')
            if qty > 0:
                line.quantity_product_uom = qty
            else:
                line.quantity_product_uom = line.quantity