# -*- coding: utf-8 -*-


from odoo import fields, models, api, _

import logging
import io
import json
import time
from odoo.http import request


class ProductReportWiz(models.TransientModel):
    _name = 'product.report.wiz'
    _description = 'product report wizard'

    all_product = fields.Boolean(string='All Product', default=False)
    products = fields.Many2many('product.product', string='Filter Products')
    date_filter = fields.Boolean(string='Period Wise', default=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def confirm(self):
        data = self.env['product.sale.report'].search([])
        data.unlink()

        if self.all_product:
            product = self.env['product.product'].search([])
        else:
            product = self.products

        domain =[]

        pos_order = self.env['pos.order'].search([])
        if self.date_filter:
            start_date = self.start_date
            end_date = self.end_date
            domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date)
            ]
            pos_order = self.env['pos.order'].search(domain)
            print(len(pos_order),'orderssssssss')

        for item in product:
            # domain += [('product_id.id', '=', item.id)]
            # else:
            order_count = pos_order.lines.filtered(lambda x: x.product_id.id == item.id)

            if order_count:
                qty = sum(sale_line.qty for sale_line in order_count)
                total_sales = sum(sale_line.price_subtotal_incl for sale_line in order_count)
                total_cost = sum(pos_line.product_id.standard_price * pos_line.qty for pos_line in order_count)
                gross_profit = total_sales - total_cost
                res = self.env['product.sale.report'].create({
                    'product_id': item.id,
                    'ordered_qty': qty,
                    'total_sales':total_sales,
                    'total_cost':total_cost,
                    'gross_profit':gross_profit
                })

        action = self.env.ref('hc_pos_orderline_report.action_hc_closing_date_alteration').sudo()
        result = action.read()[0]
        return result