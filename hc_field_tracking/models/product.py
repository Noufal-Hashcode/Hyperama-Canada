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
        digits='Product Unit of Measure', compute_sudo=False,
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.",
        track_visibility='onchange')

    def write(self, vals):
        for product in self:
            if 'qty_available' in vals:
                old_qty = product.qty_available
                new_qty = vals.get('qty_available')
                if old_qty != new_qty:
                    # Log the change using message_post
                    product.message_post(body=f"Quantity changed from {old_qty} to {new_qty}",
                                         message_type="notification",
                                         subtype="mail.mt_comment")
        return super(ProductTemplate, self).write(vals)

# class StockQuant(models.Model):
#     _inherit = 'stock.quant'
#
#     # @api.depends('quantity')
#     # def _compute_inventory_quantity_auto_apply(self):
#     #     for quant in self:
#     #         quant.inventory_quantity_auto_apply = quant.quantity
    @api.depends('quantity', 'reserved_quantity')
    def _compute_available_quantity(self):
        for quant in self:
            old_qty =quant.available_quantity
            quant.available_quantity = quant.quantity - quant.reserved_quantity
            new_qty = quant.available_quantity

            x =self.product_tmpl_id.sudo().message_post(body=f"Quantity changed from {old_qty} to {new_qty}",
                                 message_type="notification",
                                 subtype="mail.mt_comment")

            print(x,'xxxxxxxxxx')
#
#             # if 'qty_available' in vals:
#             #     old_qty = template.qty_available
#             new_qty = quant.available_quantity
#             if old_qty != new_qty:
#                 # Log the change here
#                 self.env['product.template.log'].create({
#                     'template_id': self.product_tmpl_idt,
#                     'old_qty': old_qty,
#                     'new_qty': new_qty,
#                     'user_id': self.env.user.id,
#                 })

#     inventory_quantity_auto_apply = fields.Float(
#         'Inventoried Quantity', digits='Product Unit of Measure',
#         compute='_compute_inventory_quantity_auto_apply',
#         inverse='_set_inventory_quantity', groups='stock.group_stock_manager',
#         track_visibility='onchange'
#     )
#     from odoo import models, api
#
#     # class YourModel(models.Model):
#     #     _inherit = 'your.model'
#
#         @api.multi
#         def write(self, vals):
#             for record in self:
#                 if 'your_field' in vals:
#                     old_value = record.your_field
#                     new_value = vals.get('your_field')
#                     if old_value != new_value:
#                         # Log the change here
#                         self.env['your.log.model'].create({
#                             'record_id': record.id,
#                             'field': 'your_field',
#                             'old_value': old_value,
#                             'new_value': new_value,
#                             'user_id': self.env.user.id,
#                         })
#             return super(YourModel, self).write(vals)
