# hc_pos_customisation/controllers/main.py
from odoo import http
from odoo.http import request

class PosShopifySyncController(http.Controller):

    @http.route('/pos/shopify_orders', type='json', auth='user')
    def fetch_shopify_orders(self, limit=20, offset=0):
        config_id = request.env['pos.config'].sudo().search([('name','=','Retail')], limit=1).id
        session = request.env['pos.session'].sudo().search([
            ('state', '=', 'opened'),
            ('config_id','=', config_id)
        ], limit=1)
        if not session:
            return []

        query = """
            SELECT id FROM sale_order
            WHERE state = 'sale'
            AND synced_with_pos IS NULL
            AND shopify_order_id != 'f'
            ORDER BY write_date DESC
            LIMIT %s OFFSET %s
        """
        request._cr.execute(query, (limit, offset))
        ids = [row[0] for row in request._cr.fetchall()]
        if not ids:
            return []

        sale_orders = request.env['sale.order'].browse(ids).filtered(
            lambda sale: not sale.pos_order_line_ids.mapped('order_id')
        )

        result = [{
            'order_id': order.id,
            'name': order.name,
            'partner_id': order.partner_id.id if order.partner_id else False,
            'lines': [
                {
                    'product_id': line.product_id.id,
                    'qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                }
                for line in order.order_line
            ],
        } for order in sale_orders]

        sale_orders.write({'synced_with_pos': True})
        return result

