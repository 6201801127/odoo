odoo.define('kw_accounting.preview_budget_account_vouchers', function (require) {
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
    
    var AccountVouchers = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        events: {
            'click #voucher_preview': _.debounce(function(e){
                console.log('clickefd')
                var self = this;
                self.voucher_id = e.currentTarget.dataset.voucher
                self.voucher_type = e.currentTarget.dataset.vouchertype
                setTimeout(function(){self.get_voucher_preview(self.voucher_id,self.voucher_type);},200);
            },200,true),
        },
        init: function(parent, context) {
            this._super(parent, context);
            var self = this;
            var params = {'budget_line_id': context.context.active_id}
            console.log(context)
            if (context.tag == 'kw_accounting.preview_budget_account_vouchers') {
                this._rpc({
                    model: 'account.account',
                    method: 'preview_budget_account_vouchers',
                    kwargs: params
                }, []).then(function(result){
                    self.report_data = result[0];
                    self.sum_report_data = result[1];
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
            var ledger_report_page = QWeb.render( 'kw_accounting.preview_budget_account_vouchers', {
                widget: self,
            });
            $( ".o_control_panel" ).addClass( "o_hidden" );
            $(ledger_report_page).prependTo(self.$el);
            return ledger_report_page
        },
        reload: function () {
            window.location.href = this.href;
        },
        previewTable: function() {
            var general_ledger_report = $('#accounting_vouchers_template').DataTable({
                dom: 'Bfrtip',
                bFilter: false,
                buttons: [
                    {
                        extend:'excel',
                        title:'Ledger Report',
                        footer: 'true'
                    },
                    {
                        extend: 'pdf',
                        footer: 'true',
                        orientation: 'landscape',
                        title:'Ledger Report',
                        text: 'PDF',
                        exportOptions: {
                            modifier: {
                                selected: true
                            }
                        }
                    },
                    {
                        extend: 'print',
                        title:'Ledger Report',
                        exportOptions: {
                        columns: ':visible'
                        },
                        footer: 'true'
                    },
                'colvis'
                ],
                // columnDefs: [ {
                //     targets: -1,
                //     visible: false
                // } ],
                columnDefs: [
                    {"orderable": false, "targets": '_all'},
                    {width:'5%',targes:0},
                    {width:'8%',targets:1},
                    {width:'5%',targets:2},
                    {width:'5%',targets:3},
                    {width:'15%',targets:4},
                    {width:'33%',targets:5},
                    {width:'5%',targets:6},
                    {width:'5%',targets:7},
                    {width:'5%',targets:8},
                    {width:'5%',targets:9},
                    {width:'5%',targets:10},
                    {width:'5%',targets:11},
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
        get_voucher_preview: function(voucher_id,voucher_type){
            var view_id = ''
            var form_view_ref = ''
            if (voucher_type == 'invoice') {view_id = 'account.action_invoice_tree1'; form_view_ref = 'kw_accounting.preview_voucher_form'}
            if (voucher_type == 'move') {view_id= 'account.action_move_journal_line'; form_view_ref = 'kw_accounting.preview_move_form1'}
            var self = this;
            console.log(voucher_type)
            if(voucher_type == 'invoice') {
                return this._rpc({
                    model: 'account.invoice',
                    method: 'preview_invoices',
                    kwargs: {'voucher_id': voucher_id}
                }).done(function(result) {
                    self.do_action({
                        type: result.type,
                        res_model: result.res_model,
                        view_id: view_id,
                        views: [
                            result.views[0],
                        ],
                        res_id: result.res_id,
                        target: result.target,
                        context: {
                            'form_view_ref': form_view_ref,
                        },
                    }, {
                        on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                    });
                });
            }
            else {
                return this._rpc({
                    model: 'account.move',
                    method: 'preview_vouchers',
                    kwargs: {'voucher_id': voucher_id}
                }).done(function(result) {
                    self.do_action({
                        type: result.type,
                        res_model: result.res_model,
                        view_id: view_id,
                        views: [
                            result.views[0],
                        ],
                        res_id: result.res_id,
                        target: result.target,
                        context: {
                            'form_view_ref': form_view_ref,
                        },
                    }, {
                        on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                    });
                });
            }
            
        }
    });

    core.action_registry.add('kw_accounting.preview_budget_account_vouchers', AccountVouchers);
    return AccountVouchers
});
