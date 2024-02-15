odoo.define('hc_pos_orderline_report.order_line', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var utils = require('web.utils');

//    import { download } from "@web/core/network/download";
    var download = require('web.download');

    var QWeb = core.qweb;
    var _t = core._t;
    var framework = require('web.framework');


    var datepicker = require('web.datepicker');
    var time = require('web.time');


    window.click_num = 0;
    var VatReport = AbstractAction.extend({
    template: 'TrialTemp',
        events: {
//            'click .parent-line': 'journal_line_click',
//            'click .child_col1': 'journal_line_click',
//            'click #apply_filter': 'apply_filter',
//            'click #pdf': 'print_pdf',
//            'click #xlsx': 'print_xlsx',
//            'click #vat': 'open_vat_report',
////            'click .show-gl': 'show_gl',
//            'mousedown div.input-group.date[data-target-input="nearest"]': '_onCalendarIconClick',
        },

        init: function(parent, action) {
        this._super(parent, action);
                this.currency=action.currency;
//                this.report_lines = action.report_lines;
                this.wizard_id = action.context.wizard | null;
            },


          start: function() {
            var self = this;
            self.initial_render = true;
            rpc.query({
                model: 'line.report.view',
                method: 'create',
                args: [{

                }]
            }).then(function(t_res) {
                self.wizard_id = t_res;
                self.load_data(self.initial_render);
            })
        },


        load_data: function (initial_render = true) {
            var self = this;
                self.$(".categ").empty();
                try{
                    var self = this;
                    self._rpc({
                        model: 'line.report.view',
                        method: 'view_report',
                        args: [[this.wizard_id]],
                    }).then(function(datas) {

                            if (initial_render) {
                                    self.$('.filter_view_tb').html(QWeb.render('TrialFilterView', {
                                        filter_data: datas['filters'],
                                    }));
                                    self.$el.find('.target_move').select2({
                                        placeholder: 'Report Type...',
                                    });
                            }
                            var child=[];

                        self.$('.table_view_tb').html(QWeb.render('TrialTable', {

                                            lines : datas['vals']['lines'],
                                            filter : datas['filters'],
//                                            currency : datas['currency'],
//                                            credit_total : self.format_currency(datas['currency'],datas['debit_total']),
//                                            debit_total : self.format_currency(datas['currency'],datas['debit_total']),
                                        }));

                });

                    }
                catch (el) {
                    window.location.href
                    }
            },



            print_pdf: function(e) {
            e.preventDefault();
            var self = this;
            self._rpc({
                model: 'vat.report.view',
                method: 'view_report',
                args: [
                    [self.wizard_id]
                ],
            }).then(function(data) {
                var action = {
                    'type': 'ir.actions.report',
                    'report_type': 'qweb-pdf',
                    'report_name': 'hc_vat_report.vat_report_priview',
                    'report_file': 'hc_vat_report.vat_report_priview',
                    'data': {
                        'report_data': data
                    },
                    'context': {
                        'active_model': 'line.report.view',
                        'landscape': 1,
                        'trial_pdf_report': true
                    },
                    'display_name': 'VAT Report',
                };
                return self.do_action(action);
            });
        },

            open_vat_report: function(e) {


                var action= {

                    'type': 'ir.actions.act_window',
                    'name': 'Vat closing Action',
                    'res_model': 'vat.closing.wiz',
                    'view_mode': 'form',
                    'target': 'new',
                    'views': [[false, 'form']],
                    'context': {

                           'default_wizard_id': this.wizard_id,
                    },

                    }

                return this.do_action(action);

        },


        _onCalendarIconClick: function (ev) {
        var $calendarInputGroup = $(ev.currentTarget);

        var calendarOptions = {



            icons : {
                date: 'fa fa-calendar',

            },
            locale : moment.locale(),
            format : time.getLangDateFormat(),
             widgetParent: 'body',
             allowInputToggle: true,
        };

        $calendarInputGroup.datetimepicker(calendarOptions);
    },



        format_currency: function(currency, amount) {
            if (typeof(amount) != 'number') {
                amount = parseFloat(amount);
            }
            var formatted_value = (parseInt(amount)).toLocaleString(currency[2],{
                minimumFractionDigits: 2
            })
            return formatted_value
        },

        print_xlsx: function() {
            var self = this;
            self._rpc({
                model: 'vat.report.view',
                method: 'view_report',
                args: [
                    [self.wizard_id]
                ],
            }).then(function(data) {
                var action = {
//                    'type': 'ir_actions_dynamic_xlsx_download',
                    'data': {
                         'model': 'vat.report.view',
                         'options': JSON.stringify(data['filters']),
                         'output_format': 'xlsx',
                         'report_data': JSON.stringify(data['vals']),
                         'report_name': 'VAt Report',
                         'dfr_data': JSON.stringify(data),
                    },
                };

                  self.downloadXlsx(action);

            });
        },

        downloadXlsx: function (action){



        framework.blockUI();
            session.get_file({
                url: '/dynamic_vat_xlsx_reports',
                data: action.data,
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },




        apply_filter: function(event) {

            event.preventDefault();
            var self = this;
            self.initial_render = false;




            var filter_data_selected = {};

            if (this.$el.find('.datetimepicker-input[name="date_from"]').val()) {
                filter_data_selected.date_from = moment(this.$el.find('.datetimepicker-input[name="date_from"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
            }

            if (this.$el.find('.datetimepicker-input[name="date_to"]').val()) {
                filter_data_selected.date_to = moment(this.$el.find('.datetimepicker-input[name="date_to"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
            }


            if ($(".target_move").length) {
            var post_res = document.getElementById("post_res")
            filter_data_selected.report_type = $(".target_move")[1].value
            post_res.value = $(".target_move")[1].value
                    post_res.innerHTML=post_res.value;
              if ($(".target_move")[1].value == "") {
              post_res.innerHTML="default";
//
              }
            }
            rpc.query({
                model: 'vat.report.view',
                method: 'write',
                args: [
                    self.wizard_id, filter_data_selected
                ],
            }).then(function(res) {
            self.initial_render = false;
                self.load_data(self.initial_render);
            });
        },

    });
    core.action_registry.add("ord_line_report", VatReport);
    return VatReport;
});