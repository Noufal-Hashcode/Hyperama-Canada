# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo import models, fields, _
from odoo.exceptions import UserError
import logging
import time
from odoo import _, api, fields, models, SUPERUSER_ID



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.",
        track_visibility='onchange'
    )
    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""Value of the product (automatically computed in AVCO).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""",
        track_visibility='onchange'
    )

    qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
        compute_sudo=False, digits='Product Unit of Measure',track_visibility='onchange')



class StockQuant(models.Model):
    _inherit = 'stock.quant'

#     # @api.depends('quantity')
#     # def _compute_inventory_quantity_auto_apply(self):
#     #     for quant in self:
#     #         quant.inventory_quantity_auto_apply = quant.quantity
#     @api.depends('quantity', 'reserved_quantity')
    @api.onchange('quantity')
    def _compute_available_quantities(self):
        for quant in self:
            old_qty =quant.available_quantity
            quant.available_quantity = quant.quantity - quant.reserved_quantity
            new_qty = quant.available_quantity

            x =self.product_tmpl_id.sudo().message_post(body=f"Quantity changed from {old_qty} to {new_qty}",
                                 message_type="notification",
                                 subtype_xmlid="mail.mt_comment")
            print(x,'dsc')
            return

