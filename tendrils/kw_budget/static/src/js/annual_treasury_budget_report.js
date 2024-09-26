odoo.define('kw_budget.annual_budget_vs_actual', function (require) {
    "use strict";

    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var AdvanceVsPaymentReport = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        events: {
            'click #submit-adavance-filter-button': _.debounce(function () {
                var self = this;
                // self.selected_advance_ledger_id = $('#advance-ledger-select').val();
                // self.employee_id = $('#employee-report-select').val();
                // self.date_from = $('#from_date').val();
                // self.date_to = $('#to_date').val();
                self.renderLedgerDetails();
            }),
        },
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_budget.annual_budget_vs_actual') {
                self._rpc({
                    model: 'annual_treasury_report_budget_actual',
                    method: 'annual_treasury_report_budget_actual_data',
                }, []).then(function(result){
                    console.log(result)
                    
                }).done(function(){
                    self.render();
                    self.href = window.location.href;
                });
                self.render();
                self.href = window.location.href;
            }
        },
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var advance_vs_payment_page = QWeb.render('kw_budget.annual_budget_vs_actual', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(advance_vs_payment_page).prependTo(self.$el);
            $("#advance-ledger-select,#employee-report-select").select2();
            return advance_vs_payment_page
        },
        reload: function () {
            window.location.href = this.href;
        },
        // renderLedgerDetails: async function (status) {
        //     framework.unblockUI();
        //     var self = this;
        //     var params = {}
        //     params = { 'employee_id': self.employee_id, 'ledger_id': self.selected_advance_ledger_id, 'date_from': self.date_from, 'date_to': self.date_to }
        //     return this._rpc({
        //         model: 'account.account',
        //         method: 'advance_vs_payment_report_details',
        //         kwargs: params,
        //     }).done(function (result) {
        //         var advance_vs_payment_template = $(QWeb.render('RenderAdavnceVSPaymentReport', {
        //             'report_data': result[0],
        //             'sum_report_data': result[1]
        //         }));
        //         self.$el.find('#block-ledger-data').empty();
        //         self.$el.find('#block-ledger-data').append(advance_vs_payment_template);
        //         self.previewTable();
        //     });
        // },

        // previewTable: function () {
        //     var advance_vs_payment_report_page = $('#advance_vs_payment_report_page').DataTable({
        //         dom: 'Bfrtip',
        //         bFilter: false,
        //         buttons: [
        //             {
        //                 extend: 'excel',
        //                 title: 'Advance Vs Payment Report',
        //                 footer: 'true'
        //             },
        //             {
        //                 extend: 'pdf',
        //                 footer: 'true',
        //                 orientation: 'landscape',
        //                 title: 'Advance Vs Payment Report',
        //                 text: 'PDF',
        //                 exportOptions: {
        //                     modifier: {
        //                         selected: true
        //                     }
        //                 }
        //             },
        //             {
        //                 extend: 'print',
        //                 title: 'Advance Vs Payment Report',
        //                 exportOptions: {
        //                     columns: ':visible'
        //                 },
        //                 footer: 'true'
        //             },
        //             'colvis'
        //         ],
        //         // columnDefs: [ {
        //         //     targets: -1,
        //         //     visible: false
        //         // } ],
        //         columnDefs: [
        //             { "orderable": false, "targets": '_all' },
        //         ],
        //         // fixedColumns: true,
        //         // paging: false,
        //         // scrollCollapse: true,
        //         // scrollX: true,
        //         // scrollY: 300,
        //         lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
        //         pageLength: 1000,
        //     });
        //     $(".buttons-excel").removeClass("dt-button").addClass("btn btn-primary");
        //     $(".buttons-pdf").removeClass("dt-button").addClass("btn btn-primary");
        // },
    });

    core.action_registry.add('kw_budget.annual_budget_vs_actual', AdvanceVsPaymentReport);
    return AdvanceVsPaymentReport
});
