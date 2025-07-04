from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    synced_with_pos = fields.Boolean(default=False)