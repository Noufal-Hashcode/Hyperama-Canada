# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True, tracking=True)

    def _check_default_code_constraint(self):
        """ Internal Reference must be unique """
        for product in self.filtered(lambda p: p.default_code):
            domain = [('id', '!=', product.id), ('default_code', '=', product.default_code)]
            if self.search(domain):
                raise ValidationError(_('The Internal Reference must be unique!'))

    @api.model
    def create(self, vals):
        # if self.is_using_quotation_number(vals):
        if not vals.get('default_code'):
            sequence = self.env["ir.sequence"].next_by_code("product.template.reference")
            vals["default_code"] = sequence or "/"
        return super().create(vals)

