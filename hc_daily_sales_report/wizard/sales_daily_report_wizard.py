from odoo import models, fields, api
from datetime import datetime, time, timedelta
import base64


class SalesDailyReportWizard(models.TransientModel):
    _name = 'daily.sales.report.wizard'

    date = fields.Date('Date')

    def print_daily_report(self):
        self.ensure_one()
        form_data = self.read()[0]
        form_data['company_id'] = self.env.company and self.env.company.id or False
        if self.date:
            form_data['start_date'] = self.date
        else:
            form_data['start_date'] = fields.Datetime.today()
        # form_data['end_date'] = self.date + timedelta(days=1)
        form_data['end_date'] = datetime.combine(form_data['start_date'], time.max)
        data = {
            'ids': self.env.context.get('active_ids', []),
            'model': self.env.context.get('active_model', 'ir.ui.menu'),
            'form': form_data
        }
        self = self.with_context({
            'data': data,
            'active_model': 'daily.sales.report.wizard',
            'custom_method': True
        })
        for record in self:
            return self.env.ref('hc_daily_sales_report.report_daily_sales').report_action(self, data=data)

    def generate_daily_report(self):
        # Generate the report content
        form_data = self.read()[0]
        form_data['company_id'] = self.env.company and self.env.company.id or False
        if self.date:
            form_data['start_date'] = self.date
        else:
            form_data['start_date'] = fields.Datetime.today()
        # form_data['end_date'] = self.date + timedelta(days=1)
        form_data['end_date'] = datetime.combine(form_data['start_date'], time.max)
        context = dict(self.env.context)
        context['active_model'] = self._name

        data = {
            'ids': self.env.context.get('active_ids', []),
            'model': self._name,
            'form': form_data
        }
        self = self.with_context({
            'data': data,
            'active_model': 'daily.sales.report.wizard',
            'custom_method': True
        })

        report_template_id = (self.env['ir.actions.report'].with_context(force_report_rendering=True)._render_qweb_pdf
                              ('hc_daily_sales_report.report_daily_sales', self, data=data))

        data_record = base64.b64encode(report_template_id[0])

        return report_template_id

    def get_email_recipients(self):
        # Retrieve the users or user groups to whom you want to send the report
        # Example: You can search for specific user groups or users based on your requirements
        recipients = self.env.ref('hc_daily_sales_report.user_group_daily_sales_report').mapped('users.partner_id.email')
        return recipients

    def send_daily_report_email(self, report_content, recipients):
        # Create an attachment with the PDF content
        attachment_values = {
            'name': 'Daily Sales Report.pdf',
            'type': 'binary',
            'datas': base64.b64encode(report_content[0]),
            'res_model': 'mail.message',
            'res_id': False,
            'res_name': 'Daily Sales Report.pdf',
        }
        attachment = self.env['ir.attachment'].create(attachment_values)

        # Send the report via email to the recipients
        mail_values = {
            'subject': 'Daily Sales Report',
            'body_html': '<p>Please find attached the daily sales report.</p>',
            'email_from': self.env.user.email,
            'email_to': 'firasafarhath8@gmail.com',
            'attachment_ids': [(4, attachment.id)],  # Associate the attachment with the email
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()







