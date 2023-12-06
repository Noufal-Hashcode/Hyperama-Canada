# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.scrap'

    scrap_reason = fields.Many2one(
        'scrap.reason', string="Scrap Reason",
        readonly=False, store=True,
        help="Select Reason to Scrap")

    def action_view_stock_valuation_layers(self):
        self.ensure_one()
        scraps = self.env['stock.scrap'].search([('picking_id', '=', self.id)])
        domain = [('id', 'in', (self.move_ids + scraps.move_ids).stock_valuation_layer_ids.ids)]
        action = self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
        context = literal_eval(action['context'])
        context.update(self.env.context)
        context['no_at_date'] = True
        return dict(action, domain=domain, context=context)