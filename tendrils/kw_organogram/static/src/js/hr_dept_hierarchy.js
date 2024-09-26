var department_data = [];
odoo.define('kw_organogram.hr_department_hierarchy_report', function(require) {
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

    var DeptHierarchyView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        events: {
            'click #search_department_btn': 'filterNodes',
            'click #search_department_clear': 'clearFilterResult',
        },
        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
            if (value.tag == 'kw_organogram.hr_department_hierarchy_report') {
                ajax.jsonRpc("/get_dept_data", 'call')
                    .then(function(result) {
                        department_data = result;
                        //console.log(result)
                    }).done(function() {
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
            var hr_dept_hierarchy = QWeb.render('DepartmentHierarchy', { widget: self });
            $(hr_dept_hierarchy).prependTo(self.$el);
//            $('.node .title').css({"background-color": "#f43841", "width": "100%"});
            $('.node .content').css({ "max-height": "130px", "min-height": "80px", "height": "80px" });
//            $('.nodes td table').css("margin", "auto");
//
//            $('.middle-level .title').css({ "background-color": "#f1891e", "width": "100%" });
            $('.middle-level .content').css({ "max-height": "130px", "min-height": "40px", "height": "80px" });
//
//            $('.product-dept .title').css({ "background-color": "#d81d2b", "width": "100%" });
            $('.product-dept .content').css({ "max-height": "130px", "min-height": "80px", "height": "80px" });
//
//            $('.rd-dept .title').css({ "background-color": "#108fbb", "width": "100%" });
            $('.rd-dept .content').css({ "max-height": "130px", "min-height": "80px", "height": "80px" });
//
//            $('.pipeline1 .title').css({ "background-color": "#943092", "width": "100%" });
            $('.pipeline1 .content').css({ "max-height": "130px", "min-height": "80px", "height": "80px" });

            // return hr_dept_hierarchy;
        },
        reload: function() {
            window.location.href = this.href;
        },
        filterNodes: function(){
            var self = this;
            var keyWord = $('#search_department_node').val();
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
                $('#search_department_node').val('');
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
    core.action_registry.add('kw_organogram.hr_department_hierarchy_report', DeptHierarchyView);

    return DeptHierarchyView
});