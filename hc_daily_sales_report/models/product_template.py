from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    division = fields.Many2one('product.division', 'Division')