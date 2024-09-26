var employee_data = [];
var nodeTemplate = function(data) {
      return `
        <span class="office">${data.office}</span>
        <div class="title">${data.name}</div>
        <div class="content pb-5">${data.title}</div>
      `;
    };
odoo.define('hr.hr_employee_hierarchy_report', function (require) {
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
    
    var EmplHierarchyView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel : false,

        events: {
            'click .node': 'view_employee',
            'click #search_employee_btn': 'filterNodes',
            'click #search_employee_clear': 'clearFilterResult',
        },

        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
            if (value.tag == 'hr.hr_employee_hierarchy_report') {
                ajax.jsonRpc("/get_employee_data", 'call')
               .then(function(result){
                   console.log("returned data",result);
                    employee_data = result;
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
            console.log("self data ==",{widget: self});
            var hr_employee_hierarchy = QWeb.render('hr_employee_hierarchy_report',{widget: self});
            $(hr_employee_hierarchy).prependTo(self.$el);

            $('.middle-level').each(function(k,v){
                var el = $(this);
                var mid_level_height = el.find('.info_nodes').size() > 0 ? "70px" : "40px";
                var mid_level_width = el.find('.info_nodes').size() > 0 ? "100px" : "65px";
                el.find('.content').css({"height":mid_level_height});
                el.css({"width":mid_level_width});
            });
            $('.product-dept').each(function(k,v){
                var el = $(this);
                var pd_dept_level_height = el.find('.info_nodes').size() > 0 ? "70px" : "40px";
                var pd_dept_level_width = el.find('.info_nodes').size() > 0 ? "100px" : "65px";
                el.find('.content').css({"height":pd_dept_level_height});
                el.css({"width":pd_dept_level_width});
            });

            $('.rd-dept').each(function(k,v){
                var el = $(this);
                var rd_dept_level_height = el.find('.info_nodes').size() > 0 ? "70px" : "40px";
                var rd_dept_level_width = el.find('.info_nodes').size() > 0 ? "100px" : "65px";
                el.find('.content').css({"height":rd_dept_level_height});
                el.css({"width":rd_dept_level_width});
            });

            $('.pipeline1').each(function(k,v){
                var el = $(this);
                var pipe_level_height = el.find('.info_nodes').size() > 0 ? "70px" : "40px";
                var pipe_level_width = el.find('.info_nodes').size() > 0 ? "100px" : "65px";
                el.find('.content').css({"height":pipe_level_height});
                el.css({"width":pipe_level_width});
            });

            return hr_employee_hierarchy;
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
        filterNodes: function(){
            var self = this;
            var keyWord = $('#search_employee_node').val();
            self.clearFilterResult('clear');
            console.log('clearFilterResult >>> ');
            console.log('keyWord >>> ', keyWord);
            if(!keyWord.length) {
                window.alert('Please type key word firstly.');
                return;
            } else {
                var $chart = $('.orgchart');
                // disable the expand/collapse feature

                $chart.addClass('noncollapsable');
                // distinguish the matched nodes and the unmatched nodes according to the given key word
                $chart.find('.node').filter(function(index, node) {
                        //console.log($(node).find('.title').text(), $(node).find('.title').text().toLowerCase().indexOf(keyWord));
                        return $(node).find('.title').text().toLowerCase().indexOf(keyWord) > -1;
                    }).addClass('matched focused')
                    .closest('.hierarchy').parents('.hierarchy').children('.node').addClass('retained');
                // hide the unmatched nodes
                $chart.find('.matched,.retained').each(function(index, node) {
                    $(node).removeClass('slide-up')
                        .closest('.nodes').removeClass('hidden')
                        .siblings('.hierarchy').removeClass('isChildrenCollapsed');
                    var $unmatched = $(node).closest('.hierarchy').siblings().find('.node:first:not(.matched,.retained)')
                        .closest('.hierarchy').addClass('hidden');
                });
                // hide the redundant descendant nodes of the matched nodes
                $chart.find('.matched').each(function(index, node) {
                    if (!$(node).siblings('.nodes').find('.matched').length) {
                        $(node).siblings('.nodes').addClass('hidden').parent().addClass('isChildrenCollapsed');
                    }
                });
                // loop chart and adjust lines
                self.loopChart($chart.find('.hierarchy:first'));
            }
        },
        loopChart: function($hierarchy){
            var self = this;
            var $siblings = $hierarchy.children('.nodes').children('.hierarchy');
            if ($siblings.length) {
                $siblings.filter(':not(.hidden)').first().addClass('first-shown')
                  .end().last().addClass('last-shown');
            }
            $siblings.each(function(index, sibling) {
                self.loopChart($(sibling));
            });
        },
        clearFilterResult: function(flag){
            //console.log('flag>> ', flag, typeof(flag))
            if(flag != 'clear') {
                $('#search_employee_node').val('');
            }
            $('.orgchart').find('.node').removeClass('matched retained')
                .end().find('.hidden, .isChildrenCollapsed, .first-shown, .last-shown').removeClass('hidden isChildrenCollapsed first-shown last-shown')
                .end().find('.slide-up, .slide-left, .slide-right').removeClass('slide-up slide-right slide-left');
            $('.orgchart').removeClass('noncollapsable');
            $('.orgchart').find('.node').removeClass('slide-down slide-up matched focused');
            $('.orgchart').find('.hierarchy').removeClass('isSiblingsCollapsed isAncestorsCollapsed isCollapsedSibling isCollapsedDescendant');
            $('.orgchart>.nodes>.hierarchy>.nodes>.hierarchy').find('.nodes').addClass('hidden');
            $('.orgchart>.nodes>.hierarchy>.nodes').find('.hierarchy').addClass('isChildrenCollapsed');
        }
    });
    core.action_registry.add('hr.hr_employee_hierarchy_report', EmplHierarchyView);

    return EmplHierarchyView
   });
