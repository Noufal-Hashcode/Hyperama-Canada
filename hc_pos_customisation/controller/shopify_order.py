# hc_pos_customisation/controllers/main.py
from odoo import http
from odoo.http import request

class PosShopifySyncController(http.Controller):

    @http.route('/pos/shopify_orders', type='json', auth='user')
    def fetch_shopify_orders(self):
        session = request.env['pos.session'].sudo().search([
            ('state', '=', 'opened'),
            ('config_id','=',request.env['pos.config'].sudo().search([('name','=','Retail')], limit=1).id)
        ], limit=1)
        if not session:
            return []

        # Fetch only unsynced Shopify orders
        request._cr.execute("""
                        SELECT
                            id
                        FROM
                            sale_order
                        WHERE
                            state = 'sale'
                            AND synced_with_pos = 'f'
                            AND shopify_order_id != 'f'
                        ORDER BY
                            write_date DESC
                            """)
        ids = [row[0] for row in request._cr.fetchall()]
        sale_order_ids = request.env['sale.order'].browse(ids)
        sale_orders = sale_order_ids.filtered(lambda sale: not sale.pos_order_line_ids.mapped('order_id'))
        result = []
        for order in sale_orders:
            result.append({
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
            })

        # Mark them as synced so they're not re-sent
        sale_orders.write({'synced_with_pos': True})
        return result
