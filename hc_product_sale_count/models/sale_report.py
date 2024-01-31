from odoo import api, fields, models


class SaleReportInherit(models.Model):
    _inherit = "sale.report"

    @api.model
    def _get_done_states(self):
        done_states = super()._get_done_states()
        done_states.extend(['done'])
        return done_states

    state = fields.Selection(
        selection_add=[('done', 'Posted')],
    )
