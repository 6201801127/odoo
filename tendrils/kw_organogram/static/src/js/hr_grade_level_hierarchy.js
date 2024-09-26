var grade_level_data = [];
odoo.define('hr.hr_grade_level_hierarchy_report', function (require) {
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
    var rpc = require('web.rpc');
    
    var GradelevelHierarchyView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel : false,

        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
            if (value.tag == 'hr.hr_grade_level_hierarchy_report') {
            	ajax.jsonRpc("/get_grade_level_data", 'call')
               .then(function(result){
                    console.log(result);
                    self.grade_level_data = result;
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
            return this._super();
        },
        render: function() {
            var self = this;
            var hr_grade_level = QWeb.render('hr_grade_level_hierarchy_report',{widget: self});
            $(hr_grade_level).prependTo(self.$el);
            return hr_grade_level;
        },
        reload: function () {
            window.location.href = this.href;
        },
    });
    core.action_registry.add('hr.hr_grade_level_hierarchy_report', GradelevelHierarchyView);

    return GradelevelHierarchyView
   });
