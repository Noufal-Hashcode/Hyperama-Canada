from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    division = fields.Many2one('product.division', 'Division')

    def update_product_division(self):
        for rec in self:
            if not rec.division and rec.product_tag_ids:
                division = self.env['product.division'].search([('name', '=', rec.product_tag_ids[0].name)], limit=1)
                if division:
                    rec.division = division.id