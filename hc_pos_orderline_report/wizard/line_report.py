# -*- coding: utf-8 -*-


from odoo import fields, models, api, _

import logging
import io
import json
import time
from odoo.http import request

_logger = logging.getLogger(__name__)
try:
    import xlsxwriter
except ImportError:
    _logger.debug("Can not import xlsxwriter`.")


class VatReportWizard(models.TransientModel):
    _name = 'line.report.view'
    _inherit = "account.report"
    _description = 'VAT Report view'

    date_from = fields.Date('Start Date', default=lambda *a: time.strftime('%Y-01-01'))
    date_to = fields.Date('End Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    # report_type = fields.Selection([
    #     ('default', 'Default'),
    #     ('consolidated', 'Consolidated')], string="Report Type", default='default')

    def generate_vat_report_data(self, start_date, end_date, report_type):
        print("jhjhd report_typehhjdd", report_type)
        result = {}
        res = []
        move_line = {}
        domain = [('date', '>=', start_date),
                  ('date', '<=', end_date), ('move_id.state', '=', 'posted')]

        print("self._context.get", self._context)
        company_id = self._context.get('company_id', self.env.company.id)
        print("sdcccc", company_id)
        if report_type == 'default':
            domain.append(('company_id', '=', company_id))
        list = ['auh_local_output', 'dxb_local_output', 'shj_local_output', 'ajm_local_output', 'rak_local_output',
                'fuj_local_output',
                'uaq_local_output', 'planet_tax_output', 'srcm_output', 'prcm_output', 'srcm_input', 'prcm_input',
                'import_input_adj',
                'import_input_adj',
                'auh_local_supplies', 'dxb_local_supplies', 'shj_local_supplies', 'ajm_local_supplies',
                'rak_local_supplies', 'rak_local_output',
                'fuj_local_supplies', 'fuj_local_output', 'uaq_local_supplies', 'uaq_local_output', 'planet_tax_sales',
                'planet_tax_output', 'rcm_supplies', 'nil_rate_supplies', 'exempt_supplies', 'import_adj',
                'import_input_adj', 'std_exp', 'std_exp_input', 'rcm_purchases', 'vat_closing_tag']

        tag_ids = self.env['account.account.tag'].search([('applicability', '=', "taxes"), ('name', 'in', list)])
        closing_tag_id = self.env['account.account.tag'].search(
            [('applicability', '=', "taxes"), ('name', '=', 'vat_closing_tag')]).id

        lines = self.env['account.move.line'].sudo().search(domain, order="company_id asc,date asc, id asc").filtered(
            lambda x: closing_tag_id not in x.tax_tag_ids.ids)
        for line in lines:
            print("sss", line.company_id.name)
            for tax in line.tax_tag_ids:
                vals = {
                    'id': line.id,
                    'tag': tax.name,
                    # 'amount': line.balance,
                }

                if tax.tax_negate:
                    vals['amount'] = -1 * (line.balance)
                else:
                    vals['amount'] = line.balance

                if not move_line.get(line.id):
                    move_line.update({line.id: [vals]})
                else:
                    move_line.get(line.id).append(vals)
                print("modhhdd", move_line)

        print("sdkksjdhfjshdfj", move_line)
        for tag in tag_ids:
            result.update({tag.name: 0.00})
            total = 0.0
            for rec in move_line:
                cl_list = move_line.get(rec)
                for cl in cl_list:
                    if cl.get('tag') == tag.name:
                        res.append(cl)
                        print("jhjhjsdghfjhsgfhgsdhf", cl)
                        total = sum(d.get('amount', 0) for d in res)
                        result[tag.name] = total

                        # if not result.get(tag.name):
                        #     result[tag.name] = total
                        # else:
                        #     result[tag.name] = result.get(tag.name) + total
            res.clear()
        return result

        #         move_line.update({line.id: vals})
        # for tag in tag_ids:
        #     result.update({tag.name: 0.00})
        #     total = 0.0
        #     for rec in move_line:
        #         cl = move_line.get(rec)
        #         if cl.get('tag') == tag.name:
        #             res.append(cl)
        #             total = sum(d.get('amount', 0) for d in res)
        #             result[tag.name] = total
        #     res.clear()
        # return result

    # @api.model
    def get_report_data(self, start_date, end_date, report_type, data=None):
        # model = self.env.context.get('active_model')
        # docs = self.env['ir.module.module'].browse(docids)
        # form_data = data['form']
        # start_date = form_data['start_date']
        # end_date = form_data['end_date']
        # report_type = 'default'
        lines = self.generate_vat_report_data(start_date, end_date, report_type)

        docargs = {
            # 'doc_ids': docids,
            # 'doc_model': model,
            # 'data': data['form'],
            # 'docs': docs,
            'start_date': start_date,
            'end_date': end_date,
            'lines': lines,
        }
        return docargs

    @api.model
    def view_report(self, option):
        r = self.env['vat.report.view'].search([('id', '=', option[0])])

        data = {
            'model': self,
        }
        if r.date_from:
            data.update({
                'date_from': r.date_from,
            })
        if r.date_to:
            data.update({
                'date_to': r.date_to,
            })

        vals = self.get_report_data(r.date_from, r.date_to, r.report_type)

        print("ASdkjasdjkas0", vals)

        filters = self.get_filter(option)
        # currency = self._get_currency()

        return {
            'name': "Vat Report",
            'type': 'ir.actions.client',
            'tag': 'v_r',
            'vals': vals,
            'filters': filters,

        }

    def get_filter(self, option):
        data = self.get_filter_data(option)
        filters = {}

        if data.get('date_from'):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to'):
            filters['date_to'] = data.get('date_to')
        filters['report_type'] = data.get('report_type').capitalize()
        return filters

    def get_current_company_value(self):

        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]
        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids

    def get_filter_data(self, option):
        r = self.env['vat.report.view'].search([('id', '=', option[0])])
        default_filters = {}
        company_id = self.env.companies.ids
        company_domain = [('company_id', 'in', company_id)]

        filter_dict = {

            'date_from': r.date_from,
            'date_to': r.date_to,
            'report_type': r.report_type,

        }
        filter_dict.update(default_filters)
        return filter_dict


    @api.model_create_multi
    def create(self, vals_list):
        print("fgkdfgfdg")
        for vals in vals_list:
            vals['name'] = 'eee'
        res = super(VatReportWizard, self).create(vals_list)
        return res

    def write(self, vals):
        print("Sdkaskd", vals)
        if vals.get('report_type'):
            vals.update({'report_type': vals.get('report_type').lower()})
        # if vals.get('journal_ids'):
        #     vals.update({'journal_ids': [(6, 0, vals.get('journal_ids'))]})
        # if vals.get('journal_ids') == []:
        #     vals.update({'journal_ids': [(5,)]})
        res = super(VatReportWizard, self).write(vals)
        return res

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(
            self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')
        currency_array = [self.env.company.currency_id.symbol,
                          self.env.company.currency_id.position,
                          lang]
        return currency_array

    def get_dynamic_xlsx_report(self, data, response, report_data, dfr_data):
        print("helloooooooo")
        report_data_main = json.loads(report_data)
        output = io.BytesIO()
        total = json.loads(dfr_data)
        filters = json.loads(data)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': 20})
        sub_heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': 10,
             'border': 1, 'num_format': '0.00',
             'border_color': 'black'})
        txt = workbook.add_format({'font_size': 10, 'border': 1, 'num_format': '0.00'})
        txt_l = workbook.add_format({'font_size': 10, 'border': 1, 'bold': True})
        # sheet.merge_range('A2:D3', filters.get('company_name') + ':' + ' Trial Balance', head)
        date_head = workbook.add_format({'align': 'center', 'bold': True,
                                         'font_size': 10})
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': 20})
        date_style = workbook.add_format({'align': 'center',
                                          'font_size': 10})
        sheet.merge_range('A5:E6', 'VAT Return', head)
        if filters.get('date_from'):
            sheet.merge_range('A4:B4', 'From: ' + filters.get('date_from'), date_head)
        if filters.get('date_to'):
            sheet.merge_range('C4:D4', 'To: ' + filters.get('date_to'), date_head)
        sheet.write('A7', 'Sl. No', sub_heading)
        sheet.write('B7', 'Particulars', sub_heading)
        sheet.write('C7', 'Amount (AED)', sub_heading)
        sheet.write('D7', 'VAT Amount (AED)', sub_heading)
        sheet.write('E7', 'Adjustment (AED)', sub_heading)
        sheet.merge_range('A8:E8', ' VAT on Sales and All Other Outputs ', sub_heading)
        row = 6
        col = 0
        total_amount = 0.00
        total_vat_amount = 0.00

        sheet.set_column('B7:B7', 45)
        sheet.set_column('C7:E7', 15)

        row += 2
        sheet.write(row, col, '1a', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Abu Dhabi', txt)
        sheet.write(row, col + 2, report_data_main['lines']['auh_local_supplies'], txt)
        total_amount += report_data_main['lines']['auh_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['auh_local_output'], txt)
        total_vat_amount += report_data_main['lines']['auh_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '1b', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Dubai', txt)
        sheet.write(row, col + 2, report_data_main['lines']['dxb_local_supplies'], txt)
        total_amount += report_data_main['lines']['dxb_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['dxb_local_output'], txt)
        total_vat_amount += report_data_main['lines']['dxb_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '1c', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Sharjah', txt)
        sheet.write(row, col + 2, report_data_main['lines']['shj_local_supplies'], txt)
        total_amount += report_data_main['lines']['shj_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['shj_local_output'], txt)
        total_vat_amount += report_data_main['lines']['shj_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '1d', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Ajman', txt)
        sheet.write(row, col + 2, report_data_main['lines']['ajm_local_supplies'], txt)
        total_amount += report_data_main['lines']['ajm_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['ajm_local_output'], txt)
        total_vat_amount += report_data_main['lines']['ajm_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '1e', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Ras Al Khaimah', txt)
        sheet.write(row, col + 2, report_data_main['lines']['rak_local_supplies'], txt)
        total_amount += report_data_main['lines']['rak_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['rak_local_output'], txt)
        total_vat_amount += report_data_main['lines']['rak_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '1f', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Fujairah', txt)
        sheet.write(row, col + 2, report_data_main['lines']['fuj_local_supplies'], txt)
        total_amount += report_data_main['lines']['fuj_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['fuj_local_output'], txt)
        total_vat_amount += report_data_main['lines']['fuj_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '1g', txt)
        sheet.write(row, col + 1, 'Standard rated supplies in Umm Al Quwain', txt)
        sheet.write(row, col + 2, report_data_main['lines']['uaq_local_supplies'], txt)
        total_amount += report_data_main['lines']['uaq_local_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['uaq_local_output'], txt)
        total_vat_amount += report_data_main['lines']['uaq_local_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '2', txt)
        sheet.write(row, col + 1, 'Tax Refunds provided to Tourists under the Tax Refunds for Tourists Scheme', txt)
        sheet.write(row, col + 2, report_data_main['lines']['planet_tax_output'] * 100 / 5, txt)
        total_amount += report_data_main['lines']['planet_tax_output'] * 100 / 5
        sheet.write(row, col + 3, report_data_main['lines']['planet_tax_output'], txt)
        total_vat_amount += report_data_main['lines']['planet_tax_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '3', txt)
        sheet.write(row, col + 1, 'Supplies subject to the reverse charge provisions', txt)
        sheet.write(row, col + 2, report_data_main['lines']['rcm_supplies'], txt)
        total_amount += report_data_main['lines']['rcm_supplies']
        sheet.write(row, col + 3, report_data_main['lines']['srcm_output'], txt)
        total_vat_amount += report_data_main['lines']['srcm_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '4', txt)
        sheet.write(row, col + 1, 'Zero rated supplies', txt)
        sheet.write(row, col + 2, report_data_main['lines']['nil_rate_supplies'], txt)
        total_amount += report_data_main['lines']['nil_rate_supplies']
        sheet.write(row, col + 3, '', txt)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '5', txt)
        sheet.write(row, col + 1, 'Exempt supplies', txt)
        sheet.write(row, col + 2, report_data_main['lines']['exempt_supplies'], txt)
        total_amount += report_data_main['lines']['exempt_supplies']
        sheet.write(row, col + 3, '', txt)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '6', txt)
        sheet.write(row, col + 1, 'Goods imported into the UAE', txt)
        sheet.write(row, col + 2, report_data_main['lines']['rcm_purchases'], txt)
        total_amount += report_data_main['lines']['rcm_purchases']
        sheet.write(row, col + 3, report_data_main['lines']['prcm_output'], txt)
        total_vat_amount += report_data_main['lines']['prcm_output']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '7', txt)
        sheet.write(row, col + 1, 'Adjustments to goods imported into the UAE', txt)
        sheet.write(row, col + 2, report_data_main['lines']['import_adj'], txt)
        total_amount += report_data_main['lines']['import_adj']
        sheet.write(row, col + 3, report_data_main['lines']['import_input_adj'], txt)
        total_vat_amount += report_data_main['lines']['import_input_adj']
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '8', txt)
        sheet.write(row, col + 1, 'Totals', sub_heading)
        sheet.write(row, col + 2, total_amount, sub_heading)
        sheet.write(row, col + 3, total_vat_amount, sub_heading)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.merge_range('A23:E23', ' VAT on Expenses and All Other Inputs', sub_heading)

        row = row + 1
        sheet.write(row, col, '9', txt)
        sheet.write(row, col + 1, 'Standard rated expenses', sub_heading)
        sheet.write(row, col + 2, report_data_main['lines']['std_exp'], txt)
        sheet.write(row, col + 3, report_data_main['lines']['std_exp_input'], txt)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '10', txt)
        sheet.write(row, col + 1, 'Supplies subject to the reverse charge provisions', sub_heading)
        sheet.write(row, col + 2, report_data_main['lines']['rcm_purchases'], txt)
        sheet.write(row, col + 3, report_data_main['lines']['srcm_input'], txt)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '11', txt)
        sheet.write(row, col + 1, 'Totals', sub_heading)
        sheet.write(row, col + 2, report_data_main['lines']['std_exp'] + report_data_main['lines']['rcm_purchases'],
                    sub_heading)
        sheet.write(row, col + 3, report_data_main['lines']['std_exp_input'] + report_data_main['lines']['srcm_input'],
                    sub_heading)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.merge_range('A27:E27', ' Net VAT Due', sub_heading)

        row = row + 1
        sheet.write(row, col, '12', txt)
        sheet.write(row, col + 1, 'Total value of due tax for the period', sub_heading)
        sheet.write(row, col + 2, '', txt)
        sheet.write(row, col + 3, total_vat_amount, txt)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '13', txt)
        sheet.write(row, col + 1, 'Total value of recoverable tax for the period', sub_heading)
        sheet.write(row, col + 2, '', txt)
        sheet.write(row, col + 3, report_data_main['lines']['std_exp_input'] + report_data_main['lines']['srcm_input'],
                    txt)
        sheet.write(row, col + 4, '', txt)

        row = row + 1
        sheet.write(row, col, '14', txt)
        sheet.write(row, col + 1, 'Payable tax for the period', sub_heading)
        sheet.write(row, col + 2, '', txt)
        sheet.write(row, col + 3, (total_vat_amount) - (
                    report_data_main['lines']['std_exp_input'] + report_data_main['lines']['srcm_input']), sub_heading)
        sheet.write(row, col + 4, '', txt)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
