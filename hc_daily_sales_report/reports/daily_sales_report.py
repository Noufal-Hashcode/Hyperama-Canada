from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import datetime
import base64

class ReportsaleSummary(models.AbstractModel):
    _name = 'report.hc_daily_sales_report.daily_sales_report_template'
    _description = 'Daily Sales Report'

    def sales_report_data(self,start_date,end_date):

        data_list = []
        divisions = self.env["product.division"].search([])
        methods = self.get_payment_methods()

        for division in divisions:
            orders = self.env["pos.order.line"].sudo().search([
                ('order_id.date_order', '>=', start_date),
                ('order_id.date_order', '<', end_date),
                ('product_id.division', '=', division.id)
            ])
            data = {'division_name':division.name,
                    'date': start_date,
                    'total': round(sum(orders.mapped('price_subtotal_incl')),3),
                    'gross':round(sum(orders.mapped('margin')),3),
                    'gross_percent':round(sum(orders.mapped('margin_percent')),3)
                    }
            for method in methods:
                globals()[method] = 0.00
                for rec in orders:
                    if rec.order_id.payment_ids:
                        for payment in rec.order_id.payment_ids:
                            if payment.payment_method_id.name == method:
                                globals()[method] += rec.price_subtotal_incl
                data[method] = globals()[method]


            data_list.append(data)

        return data_list

    def get_payment_methods(self):
        method_list = []
        methods = self.env["pos.payment.method"].search([])
        for method in methods:
            method_list.append(method.name)
        return method_list

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        form_data = data['form']
        start_date = form_data['start_date']
        end_date = form_data['end_date']
        payments = self.get_payment_methods()
        lines = self.sales_report_data(start_date,end_date)

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'date': start_date,
            'company_name': self.env.user.company_id.name,
            'lines': lines,
            'payment_method': payments
        }
        return docargs


    def send_email_with_attachment(self):
        report_template_id = self.env.ref(
            'hc_daily_sales_report.report_daily_sales').render_qweb_pdf(self.id)
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Customer Report",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        template = self.template_id
        template.attachment_ids = [(6, 0, [data_id.id])]
        email_values = {'email_to': self.partner_id.email,
                        'email_from': self.env.user.email}
        template.send_mail(self.id, email_values=email_values, force_send=True)
        template.attachment_ids = [(3, data_id.id)]
        return True


