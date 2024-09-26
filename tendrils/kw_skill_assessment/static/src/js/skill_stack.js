odoo.define('kw_skill_assessment.skill_stack_report', function (require) {
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
    
    var SkillStackReportView = AbstractAction.extend(ControlPanelMixin, {
        init: function(parent, value) {
            this._super(parent, value);
            var group_master = [];
            var self = this;
            if (value.tag == 'kw_skill_assessment.skill_stack_report') {
                self._rpc({
                    route: '/skill-stack-report',
                }, []).then(function(result){
                    self.group_master = result
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
            console.log(self.group_master);
            var kw_skill_stack = QWeb.render( 'kw_skill_assessment.skill_stack_report', {
                widget:self.group_master,
            });
            $(kw_skill_stack).prependTo(self.$el);
            return kw_skill_stack;
        },
        reload: function () {
                window.location.href = this.href;
        },
    });
    core.action_registry.add('kw_skill_assessment.skill_stack_report', SkillStackReportView);
    return SkillStackReportView
});
