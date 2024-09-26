odoo.define('kw_accounting.ledger_report', function (require) {
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
    
    var LedgerReport = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        events: {
            'change #timeframe-select': _.debounce(function(){
                if($('#timeframe-select').val() == 'select-date') {$('#date_selection_row').removeClass('d-none');$('#period_selection_row').addClass('d-none'); }
                if($('#timeframe-select').val() == 'select-period') {$('#date_selection_row').addClass('d-none');$('#period_selection_row').removeClass('d-none');}
                if($('#timeframe-select').val() == 'select-current-date' || $('#timeframe-select').val() == '0') {$('#date_selection_row').addClass('d-none');$('#period_selection_row').addClass('d-none');}
            }),

            'click #submit-ledger-filter-button': _.debounce(function(){
                var self = this;
                self.selected_ledger_id = $('#ledger-select').val();
                self.from_date = $('#from_date').val();
                self.to_date = $('#to_date').val();
                self.budget_type = $("#budget-type-select").val();
                self.department = $("#department-type-select").val();
                self.period_from = $('#period-start-select').val();
                self.period_to = $('#period-stop-select').val();
                self.time_frame = $('#timeframe-select').val();
                self.employee_id = $('#employee-ledger-select').val();
                self.project_id = $('#project-select').val();
                self.division_id = $('#division-type-select').val();
                self.section_id = $('#section-type-select').val();
                self.renderLedgerDetails(self.time_frame);
            }),
            'click #voucher_preview': _.debounce(function(e){
                var self = this;
                self.voucher_id = e.currentTarget.dataset.voucher
                self.voucher_type = e.currentTarget.dataset.vouchertype
                setTimeout(function(){self.get_voucher_preview(self.voucher_id,self.voucher_type);},200);
            },200,true),

            'change #group-type-select': _.debounce(function(ev){
                var self = this;
                self.group_type = $(ev.target).val();
                self.onchangeGetGroupHeads(ev);
            },0,true),
            'change #group-head-select': _.debounce(function(ev){
                var self = this;
                self.group_head = $(ev.target).val();
                self.onchangeGetGroupNames(ev);
            },0,true),
            'change #group-name-select': _.debounce(function(ev){
                var self = this;
                self.group_name = $(ev.target).val();
                self.onchangeGetAccountHeads(ev);
            },0,true),
            'change #account-head-select': _.debounce(function(ev){
                var self = this;
                self.account_head = $(ev.target).val();
                self.onchangeGetAccountSubHeads(ev);
            },0,true),
            'change #account-sub-head-select': _.debounce(function(ev){
                var self = this;
                self.account_sub_head = $(ev.target).val();
                self.onchangeGetLedgers(ev);
            },0,true),
        },
        init: function(parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_accounting.ledger_report') {
                self._rpc({
                    model: 'account.account',
                    method: 'get_ledger_report_data',
                }, []).then(function(result){
                    self.company_name = result[0];
                    self.company_currency = result[1];
                    self.ledger_ids = result[2];
                    self.department_ids = result[3];
                    self.period_ids = result[4];
                    self.branch_id = result[5];
                    self.fy_id = result[6];
                    self.employee_ids = result[7];
                    self.project_wo_ids = result[8];
                    self.division_ids = result[9];
                    self.section_ids = result[10];
                    self.group_type_ids = result[11];
                    self.group_head_ids = result[12];
                    self.group_name_ids = result[13];
                    self.account_head_ids = result[14];
                    self.account_sub_head_ids = result[15];
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
            var ledger_report_page = QWeb.render( 'kw_accounting.ledger_report', {
                widget: self,
            });
            $( ".o_control_panel" ).addClass( "o_hidden" );
            $(ledger_report_page).prependTo(self.$el);
            $('#budget-type-select,#group-type-select,#group-head-select,#group-name-select,#account-head-select,#account-sub-head-select,#ledger-select,#employee-ledger-select,#department-type-select,#division-type-select,#section-type-select,#project-select').select2();
            return ledger_report_page
        },
        reload: function () {
            window.location.href = this.href;
        },
        renderLedgerDetails: async function(status){
            framework.unblockUI();
            var self = this;
            var params = {}
            if(status == 'select-date') { 
                params = {
                    'account_id':self.selected_ledger_id,
                    'from_date':self.from_date,
                    'to_date':self.to_date,
                    'budget_type': self.budget_type,
                    'department': self.department,
                    'employee_id': self.employee_id,
                    'project_wo_id': self.project_id,
                    'division_id': self.division_id,
                    'section_id': self.section_id,
                }
            }
            else if(status == 'select-period') {
                params = {
                    'account_id':self.selected_ledger_id,
                    'budget_type': self.budget_type,
                    'department': self.department,
                    'period_from' : self.period_from,
                    'employee_id': self.employee_id,
                    'period_to' : self.period_to,
                    'project_wo_id': self.project_id,
                    'division_id': self.division_id,
                    'section_id': self.section_id,
                }
            }
            else if(status == 'select-current-date'){
                params = {
                    'account_id':self.selected_ledger_id,
                    'budget_type': self.budget_type,
                    'employee_id': self.employee_id,
                    'department': self.department,
                    'project_wo_id': self.project_id,
                    'division_id': self.division_id,
                    'section_id': self.section_id,
                    'filter': 'current_date',
                }
            }
            
            return this._rpc({
                model: 'account.account',
                method: 'get_ledger_report_details',
                kwargs: params,
            }).done(function(result) {
                var ledger_details_template = $(QWeb.render('RenderLedgerDetails', {
                    'report_data_length' : result[0],
                    'report_data' : result[1],
                    'sum_report_data': result[2],
                    'ob_actual' : result[3],
                    'ob_account' : result[4],
                    'ob_period' : result[5],
                    'ob_company' : result[6],
                    'ob_branch': result[7],
                    'ob_company_currency': result[8]
                }));
                self.$el.find('#block-ledger-data').empty();
                self.$el.find('#block-ledger-data').append(ledger_details_template)
                self.previewTable();
            });
        },
        onchangeGetGroupHeads: async function(ev){
            var self = this;
            return this._rpc({
                model: 'account.account',
                method: 'get_accounts_onchange',
                kwargs: {'group_type': self.group_type}
            }).done(function(result) {
                if (result.length > 0){
                    $('#group-head-select').empty()
                    $('#group-head-select').append('<option value="0">Select</option>');
                    $.each( result[0], function( key, value ) {
                        $('#group-head-select').append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $('#group-head-select').empty()
                    $('#group-head-select').append('<option value="0">Select</option>');
                }
            });
        },
        onchangeGetGroupNames: async function(ev){
            var self = this;
            return this._rpc({
                model: 'account.account',
                method: 'get_accounts_onchange',
                kwargs: {'group_type': self.group_type,'group_head': self.group_head}
            }).done(function(result) {
                console.log(result)
                if (result.length > 0){
                    $('#group-name-select').empty()
                    $('#group-name-select').append('<option value="0">Select</option>');
                    $.each( result[1], function( key, value ) {
                        $('#group-name-select').append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $('#group-name-select').empty()
                    $('#group-name-select').append('<option value="0">Select</option>');
                }
            });
        },
        onchangeGetAccountHeads: async function(ev){
            var self = this;
            return this._rpc({
                model: 'account.account',
                method: 'get_accounts_onchange',
                kwargs: {'group_type': self.group_type,'group_head': self.group_head,'group_name': self.group_name,}
            }).done(function(result) {
                if (result.length > 0){
                    $('#account-head-select').empty()
                    $('#account-head-select').append('<option value="0">Select</option>');
                    $.each( result[2], function( key, value ) {
                        $('#account-head-select').append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $('#account-head-select').empty()
                    $('#account-head-select').append('<option value="0">Select</option>');
                }
            });
        },
        onchangeGetAccountSubHeads: async function(ev){
            var self = this;
            return this._rpc({
                model: 'account.account',
                method: 'get_accounts_onchange',
                kwargs: {'group_type': self.group_type,'group_head': self.group_head,'group_name': self.group_name,'account_head': self.account_head,}
            }).done(function(result) {
                if (result.length > 0){
                    $('#account-sub-head-select').empty()
                    $('#account-sub-head-select').append('<option value="0">Select</option>');
                    $.each( result[3], function( key, value ) {
                        $('#account-sub-head-select').append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $('#account-sub-head-select').empty()
                    $('#account-sub-head-select').append('<option value="0">Select</option>');
                }
            });
        },
        onchangeGetLedgers : async function(ev){
            var self = this;
            return this._rpc({
                model: 'account.account',
                method: 'get_accounts_onchange',
                kwargs: {'group_type': self.group_type,'group_head': self.group_head,'group_name': self.group_name,'account_head': self.account_head,'account_sub_head': self.account_sub_head,}
            }).done(function(result) {
                if (result.length > 0){
                    $('#ledger-select').empty();
                    $('#ledger-select').append('<option value="0">Select</option>');
                    $.each( result[4], function( key, value ) {
                        $('#ledger-select').append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $('#ledger-select').empty()
                    $('#ledger-select').append('<option value="0">Select</option>');
                }
            });
        },
        previewTable: function() {
            var general_ledger_report = $('#general_ledger_report').DataTable({
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
                    {width:'5%',targets:4},
                    {width:'15%',targets:5},
                    {width:'33%',targets:6},
                    {width:'5%',targets:7},
                    {width:'5%',targets:8},
                    {width:'5%',targets:9},
                    {width:'5%',targets:10},
                    {width:'5%',targets:11},
                    {width:'5%',targets:12},
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

    core.action_registry.add('kw_accounting.ledger_report', LedgerReport);
    return LedgerReport
});
