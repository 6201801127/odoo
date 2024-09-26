odoo.define('kw_timesheets.my_timesheet', function(require) {
    "use strict";
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var viewRegistry = require('web.view_registry');
    var _t = core._t;
    var QWeb = core.qweb;
    var framework = require('web.framework');
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var ControlPanelMixin = require('web.ControlPanelMixin');

    var kwMyTimesheet = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        row_clone:false,
        current_id:1,
        
        init: function(parent, state, params) {
            var self = this;
            this._super.apply(this, arguments);
            setTimeout(function(){
                self.current_id = $('#timesheet_block').find('tr.timesheet').size();
                self.row_clone=$('.timesheet').eq(0).clone();
            },500);
        },
        events: {
            'click .remove-timesheet-row': function(ev){
                $(ev.target).closest('tr').remove();
            },
            'click .add-timesheet-row': function(el){
                var self = this;
                
                var $e = $(el.currentTarget);
                //var $action = $e.closest('.timesheet');
                var nearclone = self.row_clone;
                var current_id = this.current_id++;
                nearclone.find('select option[value="0"]').attr("selected",true);
                nearclone.find('select,input').each(function(){
                    $(this).attr('id',$(this).attr('id').replace(/\d+/,current_id));
                    $(this).attr('name',$(this).attr('name').replace(/\d+/,current_id));
                });
                $('#timesheet_block').append('<tr class="timesheet">'+nearclone.html()+'</tr>');
            },
            'change .project-category-select': _.debounce(function(ev){
                var self = this;
                self.project_category_id = $(ev.target).val();
                self.onchangeProjectCategory(ev);
            },0,true),
            'change .project-select': _.debounce(function(ev){
                console.log(ev);
                var self = this;
                self.project_id = $(ev.target).val();
                self.onchangeProject(ev);
            },0,true)
        },
        on_attach_callback: function() {
            var self = this;
            self.kw_timesheet_fetch_data();
        },
        willStart: function() {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function() {return true});
        },

        start: function() {
            var self = this;
            return this._super();
        },
        kw_timesheet_fetch_data: async function(){
            var self = this;
            var $ItemContainer = self.renderTimesheet();
            $(".o_menu_apps").find('.dropdown-menu[role="menu"]').removeClass("show");
            self.$el.html(QWeb.render("MyTimesheet",{}));
        },
        
        renderTimesheet: async function(){
            var self = this;
            framework.blockUI();
            return this._rpc({
                route: '/weekly-timesheet',
            }).done(function(result) {
                console.log(result);
                self.weekly_timesheet_data = result;
                var $timesheet = QWeb.render("Timesheet", {
                    current_week: self.weekly_timesheet_data.current_week,
                    project_category: self.weekly_timesheet_data.project_category,
                    project: self.weekly_timesheet_data.project,
                    selected_period_id: self.weekly_timesheet_data.selected_period_id,
                    selected_project_id: self.weekly_timesheet_data.selected_project_id,
                    project_tasks: self.weekly_timesheet_data.project_task
                });
                $('#timesheet').empty().append($timesheet);
                $('.project-category-select').val($('.project-category-select').attr('data-selected'));
                // $('#project-select').val($('#project-select').attr('data-selected'));
                $('.add-timesheet-row, .remove-timesheet-row').tooltip({'delay': { show: 100, hide: 100 }, 'placement': "top", 'customClass': 'timesheet-tooltip'});
                framework.unblockUI();
            });
        },

        onchangeProjectCategory: function(ev){
            var self = this;
            return this._rpc({
                model: 'kw_project_category_master',
                method: 'onchangeProjectCategory',
                kwargs: {'category_id': self.project_category_id}
            }).done(function(result) {
                console.log(result);
                if (result[0].length > 0){
                    $(ev.target).closest('tr.timesheet').find(".project-select").empty()
                    $(ev.target).closest('tr.timesheet').find(".project-select").append('<option value="0">Select</option>');
                    $.each( result[0], function( key, value ) {
                        $(ev.target).closest('tr.timesheet').find(".project-select").append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $(ev.target).closest('tr.timesheet').find(".project-select").empty()
                    $(ev.target).closest('tr.timesheet').find(".project-select").append('<option value="">Select</option>');
                }
            });
        },

        onchangeProject: function(ev){
            var self = this;
            return this._rpc({
                model: 'kw_project_category_master',
                method: 'onchangeProject',
                kwargs: {'project_id': self.project_id}
            }).done(function(result) {
                if (result[0].length > 0){
                    $(ev.target).closest('tr.timesheet').find(".project-activity-select").empty()
                    $(ev.target).closest('tr.timesheet').find(".project-activity-select").append('<option value="0">Select</option>');
                    $.each( result[0], function( key, value ) {
                        $(ev.target).closest('tr.timesheet').find(".project-activity-select").append('<option value='+value['id']+'>'+value['name']+'</option>');
                      });
                } else {
                    $(ev.target).closest('tr.timesheet').find(".project-activity-select").empty()
                    $(ev.target).closest('tr.timesheet').find(".project-activity-select").append('<option value="">Select</option>');
                }
            });
        },
    });

    core.action_registry.add('kw_my_timesheet', kwMyTimesheet);
    return kwMyTimesheet;
});