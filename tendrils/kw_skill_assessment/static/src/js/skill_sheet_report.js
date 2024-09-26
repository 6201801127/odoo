odoo.define('kw_skill_assessment.skill_sheet_report.js', function (require) {
   'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;
    var rpc = require('web.rpc')
   var SkillSheetClient = AbstractAction.extend({
   template: 'SkillSheetHead',
       events: {
       },
       init: function(parent, action) {
           this._super(parent, action);

       },
       start: function() {
           var self = this;
           self.load_data();
           $(document).on('click', '#action_export', function() {
                    self.method_call();

                });

       },
        method_call: function(type, fn, dl) {

            var elt = document.getElementById('skill_employee');
            var wb = XLSX.utils.table_to_book(elt, { sheet: "sheet1", raw : true});
            return dl ?
                XLSX.write(wb, { bookType: type, bookSST: true, type: 'base64' }) :
                XLSX.writeFile(wb, fn || ('SkillSheetReport.' + (type || 'xlsx')));
        },
       load_data: function () {
           var self = this;
                   var self = this;
                   
                   self._rpc({
                       model: 'skill_sheet_report_filter_wizard',
                       method: 'get_skill_sheet_data',
                       args: [],
                   }).then(function(result) {

                       self.$('.table_view').html(QWeb.render('SkillSheetTable', {
                                  m_data : result[0],
                                  length_data : result[1],
                                  template_body_data : result[2]
                       }));
                   });
           },
   });
   core.action_registry.add("skill_sheet_client", SkillSheetClient);
   return SkillSheetClient;
});