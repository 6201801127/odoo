odoo.define('support.ticket.dashboard', function (require) {
"use strict";

var core = require('web.core');
var KanbanController = require('web.KanbanController');
var KanbanModel = require('web.KanbanModel');
var KanbanRenderer = require('web.KanbanRenderer');
var KanbanView = require('web.KanbanView');
var session = require('web.session');
var view_registry = require('web.view_registry');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var SupportTicketDashboardRenderer = KanbanRenderer.extend({
    events: _.extend({}, KanbanRenderer.prototype.events, {
        'click .o_dashboard_action': '_onDashboardActionClicked',
        'click .o_target_to_set': '_onDashboardTargetClicked',
    }),

    _notifyTargetChange: function (target_name, value) {
        this.trigger_up('dashboard_edit_target', {
            target_name: target_name,
            target_value: value,
        });
    },

    _render: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var values = self.state.dashboardValues;
            var support_ticket_dashboard = QWeb.render('gts_ticket_management.SupportTicketDashboard', {
                widget: self,
                show_demo: values.show_demo,
                rating_enable: values.rating_enable,
                success_rate_enable: values.success_rate_enable,
                values: values,
            });
            self.$el.prepend(support_ticket_dashboard);
        });
    },
    _onDashboardActionClicked: function (e) {
        var self = this;
        e.preventDefault();
        var $action = $(e.currentTarget);
        var action_ref = $action.attr('name');
        var title = $action.attr('title');
        var search_view_ref = $action.attr('search_view_ref');
        if ($action.attr('show_demo') != 'true'){
            if ($action.attr('name').includes("gts_ticket_management.")) {
                this._rpc({
                    model: 'support.ticket',
                    method: 'create_action',
                    args: [action_ref, title, search_view_ref],
                }).then(function (result) {
                    if (result.action) {
                        self.do_action(result.action, {
                            additional_context: $action.attr('context')
                        });
                    }
                });
            }
            else {
                this.trigger_up('dashboard_open_action', {
                    action_name: $action.attr('name'),
                });
            }
        }
    },
    _onDashboardTargetClicked: function (e) {
        var self = this;
        var $target = $(e.currentTarget);
        var target_name = $target.attr('name');
        var target_value = $target.attr('value');

        var $input = $('<input/>', {type: "text", name: target_name});
        if (target_value) {
            $input.attr('value', target_value);
        }
        $input.on('keyup input', function (e) {
            if (e.which === $.ui.keyCode.ENTER) {
                self._notifyTargetChange(target_name, $input.val());
            }
        });
        $input.on('blur', function () {
            self._notifyTargetChange(target_name, $input.val());
        });
        $input.replaceAll($target)
              .focus()
              .select();
    },
});

var SupportTicketDashboardModel = KanbanModel.extend({
    init: function () {
        this.dashboardValues = {};
        this._super.apply(this, arguments);
    },
    __get: function (localID) {
        var result = this._super.apply(this, arguments);
        if (_.isObject(result)) {
            result.dashboardValues = this.dashboardValues[localID];
        }
        return result;
    },
    __load: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },
    __reload: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },
    _loadDashboard: function (super_def) {
        var self = this;
        var dashboard_def = this._rpc({
            model: 'support.team',
            method: 'retrieve_dashboard',
        });
        return Promise.all([super_def, dashboard_def]).then(function(results) {
            var id = results[0];
            var dashboardValues = results[1];
            self.dashboardValues[id] = dashboardValues;
            return id;
        });
    },
});

var SupportTicketDashboardController = KanbanController.extend({
    custom_events: _.extend({}, KanbanController.prototype.custom_events, {
        dashboard_open_action: '_onDashboardOpenAction',
        dashboard_edit_target: '_onDashboardEditTarget',
    }),
    _onDashboardEditTarget: function (e) {
        var target_name = e.data.target_name;
        var target_value = e.data.target_value;
        if (isNaN(target_value)) {
            this.do_warn(false, _t("Please enter an integer value"));
        } else {
            var values = {};
            values[target_name] = parseInt(target_value);
            this._rpc({
                    model: 'res.users',
                    method: 'write',
                    args: [[session.uid], values],
                })
                .then(this.reload.bind(this));
        }
    },
    _onDashboardOpenAction: function (e) {
        var self = this;
        var action_name = e.data.action_name;
        if (_.contains(['action_view_rating_today', 'action_view_rating_7days'], action_name)) {
            return this._rpc({model: this.modelName, method: action_name})
                .then(function (data) {
                    if (data) {
                    return self.do_action(data);
                    }
                });
        }
        return this.do_action(action_name);
    },
});

var SupportTicketDashboardView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Model: SupportTicketDashboardModel,
        Renderer: SupportTicketDashboardRenderer,
        Controller: SupportTicketDashboardController,
    }),
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard',
    searchview_hidden: true,
});

view_registry.add('support_ticket_dashboard', SupportTicketDashboardView);

return {
    Model: SupportTicketDashboardModel,
    Renderer: SupportTicketDashboardRenderer,
    Controller: SupportTicketDashboardController,
};

});
