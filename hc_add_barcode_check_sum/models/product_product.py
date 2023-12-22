# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_round, groupby


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_add_check_sum(self):
        for rec in self:
            if rec.barcode:
                ean12_data = rec.barcode + '00000'
                check_digit = self.calculate_ean13_check_digit(ean12_data)
                ean13_barcode = ean12_data + str(check_digit)
                rec.barcode = ean13_barcode

    def calculate_ean13_check_digit(self, data):
        # Ensure that the input data is a 12-digit string
        if not (isinstance(data, str) and len(data) == 12 and data.isdigit()):
            raise ValueError("Input must be a 12-digit string")

        # Calculate the check digit
        sum_odd = sum(int(data[i]) for i in range(0, 12, 2))
        sum_even = sum(int(data[i]) for i in range(1, 12, 2))
        total_sum = sum_odd + sum_even * 3
        check_digit = (10 - (total_sum % 10)) % 10

        return check_digit
