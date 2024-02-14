from odoo import models, fields, api
import base64


class ProductDivision(models.Model):
    _name = 'product.division'

    name = fields.Char("Name")

    @api.model
    def send_email_with_attachment(self):
        wizard = self.env['daily.sales.report.wizard'].create({})
        report_content = wizard.generate_daily_report()
        recipients = wizard.get_email_recipients()
        if report_content and recipients:
            wizard.send_daily_report_email(report_content, recipients)
