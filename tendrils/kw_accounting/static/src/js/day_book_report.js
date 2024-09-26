odoo.define('kw_accounting.day_book_report', function (require) {
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
    
    var DayBookReport = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        events: {
            'click #submit-day-book-button': _.debounce(function(){
                var self = this;
                self.voucher_type = $('#voucher-type-select').val();
                self.date_from = $('#from_date').val();
                self.date_to = $('#to_date').val();
                self.renderLedgerDetails();
            }),
        },
        init: function(parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_accounting.day_book_report') {
                self._rpc({
                    model: 'account.account',
                    method: 'day_book_report',
                }, []).then(function(result){
                    console.log(result)
                    self.company_name = result[0];
                    self.company_currency = result[1];
                    self.fy_id = result[2];
                    self.branch_id = result[3];
                }).done(function(){
                    self.render();
                    self.href = window.location.href;
                });
            }
        },
        willStart: function() {
             return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            var self = this;
            return this._super();
        },
        render: function() {
            var super_render = this._super;
            var self = this;
            var day_book_page = QWeb.render( 'kw_accounting.day_book_report', {
                widget: self,
            });
            $( ".o_control_panel" ).addClass( "o_hidden" );
            $(day_book_page).prependTo(self.$el);
            return day_book_page
        },
        reload: function () {
            window.location.href = this.href;
        },
        renderLedgerDetails: async function(status){
            framework.unblockUI();
            var self = this;
            var params = {}
            params = {'voucher_type':self.voucher_type,'date_from':self.date_from,'date_to':self.date_to}
            return this._rpc({
                model: 'account.account',
                method: 'day_book_report_details',
                kwargs: params,
            }).done(function(result) {
                console.log(result)
                var day_book_template = $(QWeb.render('RenderDayBook', {
                    'report_data' : result[0],
                }));
                self.$el.find('#block-ledger-data').empty();
                self.$el.find('#block-ledger-data').append(day_book_template);
                self.previewTable();
            });
        },

        previewTable: function() {
            var day_book_report_page = $('#day_book_report_dt').DataTable({
                dom: 'Bfrtip',
                bFilter: false,
                buttons: [
                    {
                        extend:'excel',
                        title:'Advance Vs Payment Report',
                        footer: 'true'
                    },
                    {
                        extend: 'pdf',
                        footer: 'true',
                        orientation: 'landscape',
                        title:'Advance Vs Payment Report',
                        text: 'PDF',
                        exportOptions: {
                            modifier: {
                                selected: true
                            }
                        }
                    },
                    {
                        extend: 'print',
                        title:'Advance Vs Payment Report',
                        exportOptions: {
                        columns: ':visible'
                        },
                        footer: 'true'
                    },
                'colvis'
                ],
                columns: [
                    {
                        name: 'first',
                        title: 'Transaction Date',
                    },
                    {
                        name: 'second',
                        title: 'Voucher No.',
                    },
                    {
                        name: 'third',
                        title: 'Narration',
                    },
                    {
                        title: 'Particulars',
                    }, 
                    {
                        title: 'Budget Type',
                    },
                    {
                        title: 'Amount [Dr.]',
                    },
                    {
                        title: 'Amount [Cr.]',
                    },
                ],
                rowsGroup: [
                    'first:name',
                    'second:name',
                    'third:name',
                  ],
                columnDefs: [
                    {"orderable": false, "targets": '_all'},
                ],
                // fixedColumns: true,
                // paging: false,
                // scrollCollapse: true,
                // scrollX: true,
                // scrollY: 300,
                lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                pageLength: 1000,
            });
            $(".buttons-excel").removeClass("dt-button").addClass("btn btn-primary");
            $(".buttons-pdf").removeClass("dt-button").addClass("btn btn-primary");
        },
    });

    core.action_registry.add('kw_accounting.day_book_report', DayBookReport);
    return DayBookReport
});
