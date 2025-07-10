# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime
from markupsafe import Markup
from functools import partial
from itertools import groupby
from collections import defaultdict

import psycopg2
import pytz
import re

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero, float_round, float_repr, float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"


    def _compute_total_cost_at_session_closing(self, stock_moves):
        """
        Compute the margin at the end of the session. This method should be called to compute the remaining lines margin
        containing a storable product with a fifo/avco cost method and then compute the order margin
        """
        for order in self:
            storable_fifo_avco_lines = order.lines.filtered(lambda l: l._is_product_storable_fifo_avco())
            for item in storable_fifo_avco_lines:
                item._compute_total_cost(stock_moves)

    @api.depends('lines.margin', 'is_total_cost_computed')
    def _compute_margin(self):
        """
            Compute the margin and margin percentage for the order based on the cost of products in each line.

            This method overrides the standard margin computation logic to ensure that margin is calculated using
            the current product cost, even if the product has a nested BOM or the cost method has changed over time.

            Why this is needed:
            - The default Odoo margin logic may consider historical cost from past configurations (e.g., standard price at the time of order),
            which can lead to incorrect margin reporting when product costs or BOMs are updated later.
            - This method forces the margin to be recalculated based on the **current product cost** and **currency conversion**,
            rather than relying on stored or historical data.
            - It accounts for nested BOM structures by ensuring that each line's cost reflects the correct up-to-date value.

            Key logic:
            - For each order line, it calculates `total_cost` as: `line.qty * converted product cost`.
            - Then it calls `line._compute_margin()` to update line-level margin.
            - If `is_total_cost_computed` is True, it sums all line margins for the order margin,
            and calculates margin percentage over the untaxed total.
            - If not, the margin and margin percentage are set to 0.

            Note:
            - This method is meant to fix margin inconsistencies that arise when past product cost configurations.
        """
        for order in self:
            for line in order.lines:
                product = line.product_id
                product_cost = product.standard_price
                line.total_cost = line.qty * product.cost_currency_id._convert(
                    from_amount=product_cost,
                    to_currency=line.currency_id,
                    company=line.company_id or self.env.company,
                    date=line.order_id.date_order or fields.Date.today(),
                    round=False,
                )
                line._compute_margin()
            if order.is_total_cost_computed:
                order.margin = sum(order.lines.mapped('margin'))
                amount_untaxed = order.currency_id.round(sum(line.price_subtotal for line in order.lines))
                order.margin_percent = not float_is_zero(amount_untaxed, precision_rounding=order.currency_id.rounding) and order.margin / amount_untaxed or 0
            else:
                order.margin = 0
                order.margin_percent = 0