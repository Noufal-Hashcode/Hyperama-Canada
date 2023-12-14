# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import models, fields, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_import_receipt = fields.Boolean("Is Import Receipt", default=False)
    is_transfer_to_main = fields.Boolean("Is Transfer To Main", default=False)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_import_receipt = fields.Boolean(related='picking_type_id.is_import_receipt', readonly=False)
    main_transfer_picking_id = fields.Many2one('stock.picking', 'Main Transfer Picking')
    main_transfer_created = fields.Boolean("Main Transfer Created", default=False)

    def action_transfer_to_main_stock(self):
        print("action_transfer_to_main_stock")
        for rec in self:
            main_transfer_picking_type_id = self.env['stock.picking.type'].search([('is_transfer_to_main', '=', True)])
            print("main_transfer_picking_type_id", main_transfer_picking_type_id)
            if main_transfer_picking_type_id:
                main_transfer_picking_id = rec.copy({
                    'picking_type_id': main_transfer_picking_type_id.id,
                    'location_id': main_transfer_picking_type_id.default_location_src_id.id,
                    'location_dest_id': main_transfer_picking_type_id.default_location_dest_id.id,
                })
                # create new picking for returned products
                # main_transfer_picking_id = rec.copy(self._prepare_picking_default_values())
                picking_type_id = main_transfer_picking_id.picking_type_id.id
                if main_transfer_picking_id:
                    rec.main_transfer_picking_id = main_transfer_picking_id.id
                    rec.main_transfer_created = True
                    main_transfer_picking_id.action_confirm()
                    main_transfer_picking_id.action_assign()
                    main_transfer_picking_id.button_validate()
            print("main_transfer_picking_id", main_transfer_picking_id)
            if rec.main_transfer_picking_id:
                ctx = dict(self.env.context)
                ctx.update({
                    'default_partner_id': self.partner_id.id,
                    'search_default_picking_type_id': main_transfer_picking_id.id,
                    'search_default_draft': False,
                    'search_default_assigned': False,
                    'search_default_confirmed': False,
                    'search_default_ready': False,
                    'search_default_planning_issues': False,
                    'search_default_available': False,
                })
                print("ctx", ctx)
                return {
                    'name': _('Main Transfer'),
                    'view_mode': 'form,tree,calendar',
                    'res_model': 'stock.picking',
                    'res_id': main_transfer_picking_id.id,
                    'type': 'ir.actions.act_window',
                    'context': ctx,
                }

    def _prepare_main_picking_default_values(self):
        vals = {
            'move_ids': [],
            'picking_type_id': self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id,
            'state': 'draft',
            'return_id': self.picking_id.id,
            'origin': _("Return of %s", self.picking_id.name),
        }
        # TestPickShip.test_mto_moves_return, TestPickShip.test_mto_moves_return_extra,
        # TestPickShip.test_pick_pack_ship_return, TestPickShip.test_pick_ship_return, TestPickShip.test_return_lot
        if self.picking_id.location_dest_id:
            vals['location_id'] = self.picking_id.location_dest_id.id
        if self.location_id:
            vals['location_dest_id'] = self.location_id.id
        return vals

    def action_see_main_transfer(self):
        print("action_see_main_transfer")
        self.ensure_one()
        print("self.main_transfer_picking_id", self.main_transfer_picking_id)
        if self.main_transfer_picking_id:
            print("@@@@@@@@@@@@@@@@@")
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "views": [[False, "form"]],
                "res_id": self.main_transfer_picking_id.id
            }
