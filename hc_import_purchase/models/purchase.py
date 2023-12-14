# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import float_round, groupby


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection([('local', 'Local'), ('import', 'Import')], string='Purchase Type', tracking=True,
                                     required=True,default='import'
                                     )

    @api.onchange('purchase_type')
    def onchange_purchase_type(self):
        print("onchange_purchase_type")
        for rec in self:
            if rec.purchase_type and rec.purchase_type == 'import':
                import_picking = self.env['stock.picking.type'].search([('is_import_receipt', '=', True)])
                print("import_picking", import_picking)
                if import_picking:
                    rec.picking_type_id = import_picking.id
            else:
                rec.picking_type_id = self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
