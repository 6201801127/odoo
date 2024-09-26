var project_data = [];
var resource_data = [];
var nodeTemplate = function(data) {
      return `
        <div class="title">${data.name}</div>
        <div class="content pb-1">${data.title}</div>
      `;
    };
    //<span class="office">${data.office}</span>
odoo.define('hr.hr_project_hierarchy_report', function (require) {
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
    var _t = core._t;

    var ProjectHierarchyView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel : false,

        events: {
            'click .node': 'view_employee',
        },

        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
            if (value.tag == 'hr.hr_project_hierarchy_report') {
                ajax.jsonRpc("/get_project_data", 'call')
                .then(function(result){
                    project_data = result;
                }).done(function(){
                    self.render();
                    self.href = window.location.href;
                });
                
            }
        },
        searchProject:function(){
            $('#project_hierachy_project_search').on('keyup',function(event){
                var g = $(this).val().toLowerCase();
                $(".project_name").each(function() {
                    var s = $(this).text().toLowerCase();
                    $(this).closest('tr')[ s.indexOf(g) !== -1 ? 'show' : 'hide' ]();
                });
            });
            $('#project_hierachy_manager_search').on('keyup',function(event){
                var g = $(this).val().toLowerCase();
                $(".manager_name").each(function() {
                    var s = $(this).text().toLowerCase();
                    $(this).closest('tr')[ s.indexOf(g) !== -1 ? 'show' : 'hide' ]();
                });
            });
        },
        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            return this._super();
        },

        render: function() {
            var self = this;
            // self.$el.addClass('row');
            var project_hierarchy = QWeb.render('hr_project_hierarchy_select',{widget: self,project_data:project_data});
            $(project_hierarchy).prependTo(self.$el);

            // $('.middle-level .content, .product-dept .content, .rd-dept .content, .pipeline1 .content').css({"height":"32px"});

            // $('#project_hierachy_project_id').change(function () {
            //     self.get_project_hierachy($(this).val());
            // });
            let e = $('.organogram_project_search').click(function(){
                // $('#project_hierachy_project_select').find('.project_select').removeClass('active');
                // $(this).addClass('active');
                self.get_project_hierachy($(this).attr('val'));
            });
            e.eq(0).trigger('click');
            
            $('#organogram_project_count').html(project_data.length);
            $('#project_hierachy_organogram').find('.content').css({"height":"32px"});
            self.searchProject();
            return project_hierarchy;
        },
        get_project_hierachy: function(pid){
            var self = this;
            if(parseInt(pid) > 0){
                ajax.jsonRpc("/get_hierarchy_data", 'call',{pid:pid}).then(function(response){
                    // console.log('project response', response)
                    resource_data = response;
                }).done(function(response){
                    // console.log('project response done', response)
                    self.render_project_hierachy();
                    self.href = window.location.href;
                });
            }
        },
        render_project_hierachy: function(pid){
            var self = this;
            $('#project_hierachy_block').remove();
            var resource_hierarchy = QWeb.render('hr_project_hierarchy_report',{widget: self});
            $(resource_hierarchy).appendTo(self.$el.find('#project_hierachy_organogram'));
            
            // setTimeout(function(){
                $('#project_hierachy_organogram').find('.content').css({"height":"32px"});
            // }, 1000);
            
            return resource_hierarchy;
        },

        reload: function () {
            window.location.href = this.href;
        },
        view_employee: function(ev){
            if (ev.currentTarget.id){
                var id = parseInt(ev.currentTarget.id)
                this.do_action({
                    name: _t("Employee"),
                    type: 'ir.actions.act_window',
                    res_model: 'hr.employee',
                    res_id: id,
                    view_mode: 'form',
                    views: [[false, 'form']],
                })
            }
        },
    });
    core.action_registry.add('hr.hr_project_hierarchy_report', ProjectHierarchyView);

    return ProjectHierarchyView
   });
