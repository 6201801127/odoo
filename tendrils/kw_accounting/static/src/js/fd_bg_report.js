odoo.define('kw_accounting.fd_bg_report', function (require) {
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
    var PivotView = require('web.PivotView');
    
    var FD_BG_Report = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
      
        init: function(parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_accounting.fd_bg_report') {
                self._rpc({
                    model: 'bg_reference',
                    method: 'fd_bg_report',
                }, []).then(function(result){
                    
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
            // this.renderPivotView();
            return this._super();

        },
        render: function() {
            var super_render = this._super;
            var self = this;
            var ledger_report_page = QWeb.render( 'kw_accounting.fd_bg_report', {
                widget: self,
            });
            $( ".o_control_panel" ).addClass( "o_hidden" );
            $(ledger_report_page).prependTo(self.$el);
            return ledger_report_page
        },
        renderPivotView: function () {
            var self = this;

            var fields = {
                loan_bank : {type: 'Char', string: ''},
                loan_id : {type: 'many2one', relation: 'hr.loan',string: 'Loan Ref.'},
                date : {type: 'date', string: 'Date'},
                opening_blance_principle : {type: 'float', string: 'opening_blance_principle'},
                new_amount : {type: 'float', string: 'new_amount'},
                interest_per : {type: 'float', string: 'interest_per'},
                interest_amt : {type: 'float', string: 'interest_amt'},
                amount : {type: 'float', string: 'amount'},
                principle : {type: 'float', string: 'principle'},
                closing_blance_principle : {type: 'float', string: 'closing_blance_principle'},
                // Add other fields as needed
            };

            var arch = `
                <pivot string="Your Pivot View">
                    <field name="loan_bank" type="col"/>
                    <field name="loan_id" type="col"/>
                    <field name="date" type="row"/>
                    <field name="opening_blance_principle" type="measure" />
                    <field name="new_amount" type="measure" />
                    <field name="interest_per" type="measure" />
                    <field name="interest_amt" type="measure" />
                    <field name="amount" type="measure" />
                    <field name="principle" type="measure" />
                    <field name="closing_blance_principle" type="measure" />
                </pivot>`;

            var pivotView = new PivotView(this, {
                modelName: 'hr.loan',
                domain: [],
                fields: fields,
                arch: arch,
                viewInfo: {
                    arch: arch,
                    fields: fields,
                },
                resModel: 'hr.loan',
               
            });

            pivotView.appendTo(this.$('.pivot_container')).then(function () {
                // Pivot view rendered
            });
        },
        reload: function () {
            window.location.href = this.href;
        },
       
    });

    core.action_registry.add('kw_accounting.fd_bg_report', FD_BG_Report);
    return FD_BG_Report
});
