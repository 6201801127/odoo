odoo.define('kw_training.training_calendar', function (require) {
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
    
    var CalendarView = AbstractAction.extend(ControlPanelMixin, {
        events: {
            'change #t_f_year': 'action_load_financial_year',
        },
        init: function(parent, value) {
            this._super(parent, value);
            var training = [];
            var self = this;
            if (value.tag == 'kw_training.training_calendar') {
                self._rpc({
                    model:'kw_training',
                    method : 'get_calendar'
                }, []).then(function(result){
                    self.training = result;
                    self.render();
                    self.href = window.location.href;
                    $('.o_menu_apps').find('.dropdown-menu').removeClass('show');
                    $('.o_form_button_edit').hide();
                    $('.o-kanban-button-new').hide();
                    $('.o_form_button_save').hide();
                    $('.o_form_button_cancel').hide();
                    $('.o_import_cancel').hide();
                    $('.oe_import_file').hide();
                    $('.o_form_button_create').hide();
                    $('.o_list_button_add').hide();
                    $('.o_button_import').hide();
                });
            }
            
            setTimeout(function () {
                $('#t_f_year').val($('#t_f_year').attr('data-selected'));
            }, 1000);
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
            var kw_calendar = QWeb.render('kw_training.training_calendar', {
                widget:self,
            });
            $(kw_calendar).prependTo(self.$el);
            return kw_calendar;
        },
        reload: function () {
                window.location.href = this.href;
        },
        action_load_financial_year: function (event) {
            var self = this;
            var f_id = $("#t_f_year option:selected").val();
            $('#training_year_string').html($("#t_f_year option:selected").text());
            self._rpc({
                model: 'kw_training',
                method: 'get_calendar_by_financial_year',
                args: [{
                    'financial_id': f_id,
                }],

            }).then(function (result) {
                if (result){
                    $.each(result, function (key, value) {
                        if (value.length>0){
                            var element_data = '<table class="table m-0"><thead class="thead-orange training_thead">\
                                            <th scope="col" class="text-left"> Topic </th>\
                                            <th scope="col"> Type </th></thead >\
                                            <tbody class="training_tbody">';
                            $.each(value, function (index, val) {
                                element_data += '<tr><td class="text-capitalize text-left m-0 p-0">\
                                                <p>'+val.name+'</p></td>\
                                                <td class="text-capitalize m-0 p-0">\
                                                <p>'+ val.instructor +'</td></tr>';
                            });
                            element_data +='</tbody></table>';
                            $("#training_" + key).html(element_data);
                        } else {
                            $("#training_" + key).html('<p class="p-2"> No training found.</p >');
                        }
                    });
                } else {
                    $('.rcontent').html('<p class="p-2"> No training found.</p >');
                }
            });
        },
    });
    core.action_registry.add('kw_training.training_calendar', CalendarView);
    return CalendarView;
});
