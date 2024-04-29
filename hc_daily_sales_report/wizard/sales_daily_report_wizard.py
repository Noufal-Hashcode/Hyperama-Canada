from odoo import models, fields, api
from datetime import datetime, time, timedelta
import base64
import pytz


class SalesDailyReportWizard(models.TransientModel):
    _name = 'daily.sales.report.wizard'

    from_date = fields.Datetime('From Date')
    to_date = fields.Datetime('To Date')

    def print_daily_report(self):
        self.ensure_one()
        form_data = self.read()[0]
        form_data['company_id'] = self.env.company and self.env.company.id or False

        # tz = pytz.timezone('UTC')
        tz = pytz.timezone("America/Toronto")
        # tz = pytz.timezone('Asia/Dubai')
        if self.from_date:
            # current_date = self.date
            # date = self.from_date
            # start = tz.localize(date)
            form_data['start_date'] = self.from_date
        else:
            current_date = datetime.now().date()
            date = datetime.combine(current_date, time.min)
            start = tz.localize(date)
            form_data['start_date'] = start.astimezone(pytz.utc)
        form_data['end_date'] = self.to_date
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
        # tz = pytz.timezone(self.env.user.tz or 'UTC')
        tz = pytz.timezone("America/Toronto")
        # tz = pytz.timezone('Asia/Dubai')
        if self.from_date:
        #     current_date = datetime.now().date()
            form_data['start_date'] = self.from_date
            # form_data['end_date'] = datetime(current_date + timedelta(hours=self.env.company.end_time))
        else:
            current_date = datetime.now().date()
            date = datetime.combine(current_date, time.min)
            # start = tz.localize(date)
            start = date.astimezone(tz)
            form_data['start_date'] = start
        end = tz.localize(datetime.combine(current_date, time.max))
        form_data['end_date'] = end.astimezone(tz)
        print("form",form_data)
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
            'body_html': '<p>Please find attached daily sales report.</p>',
            'email_from': self.env.user.email,
            'email_to': ','.join(recipients),
            'attachment_ids': [(4, attachment.id)],  # Associate the attachment with the email
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)

        mail.sudo().send()







