# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import models, fields
class ScrapReason(models.Model):
    _name = 'scrap.reason'
    _description = 'Scrap Reason'
    _order = 'sequence, id'


    # state = fields.Char( string='Status', required=True,)
    sequence = fields.Integer('Sequence', default=10)

    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)


