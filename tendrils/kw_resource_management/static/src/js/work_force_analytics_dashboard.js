odoo.define('kw_resource_management.rcm_work_force_analytics_dashboard', function (require) {
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
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var RCMWorkForceDashboardView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_resource_management.rcm_work_force_analytics_dashboard') {
                this._rpc({
                    model: 'work_force_analytics_dashboard',
                    method: 'get_resource_nexus_filter_data',
                }, []).then(function (result) {
                    self.employee_role_filters = result['resource_nexus_dashboard_filters'][0];
                }).done(function () {
                    self.href = window.location.href;
                });
            }
            
            return this._super.apply(this, arguments);
        },

        events: {
            'click .resource_nexus_count': 'resource_nexus_count',
            'click .delivery_resource_count': 'delivery_resource_count',
            'click .sbu_resource': 'sbu_resource',
            'click .horizontal_resource': 'horizontal_resource',
            'click .talent_pool_resource': 'talent_pool_resource',
            'click .csuite_resource': 'csuite_resource',
            'click .company_overhead_csm_resource': 'company_overhead_csm_resource',
            'click .company_overhead_outsource_resource': 'company_overhead_outsource_resource',
            'click .delivery_lab_csm_resource': 'delivery_lab_csm_resource',
            'click .delivery_lab_outsource_resource': 'delivery_lab_outsource_resource',
            'click .delivery_overhead_csm_resource': 'delivery_overhead_csm_resource',
            'click .delivery_overhead_outsource_resource': 'delivery_overhead_outsource_resource',
            'click .resource_deployement_csm_resource': 'resource_deployement_csm_resource',
            'click .resource_deployement_outsource_resource': 'resource_deployement_outsource_resource',
            'click .delivery_consultancy_resource': 'delivery_consultancy_resource',
        },
    
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },
        start: function () {
            var self = this;
            this.set("title", 'Resource Nexus Dashboard');
            return this._super().then(function () {
                setTimeout(function () {
                    self.render();
                    
                }, 0);
            });
        },
        
        render: function () {
            var super_render = this._super;
            var self = this;
            var work_dashboard = QWeb.render('kw_resource_management.rcm_work_force_analytics_dashboard', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(work_dashboard).prependTo(self.$el);
            self.render_graphs();
            self.renderDashboard();
            return work_dashboard
        },
        fetch_data: function() {
            var self = this;
            var def0 =  this._rpc({
                    model: 'work_force_analytics_dashboard',
                    method: 'get_total_csm_resource_nexus_count'
            }).done(function(result) {
                self.csm_resource_count =  result[0];
            });
            var def00 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_delivery_dept_count'
            }).done(function(result) {
                self.delivery_dept_resource_count =  result[0];
            });
            var def1 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_cmpn_ovhd_csm_resource_count'
            }).done(function(result) {
                self.cmpn_ovhd_csm_resource_count =  result[0];
            });
            var def2 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_cmpn_ovhd_outsource_resource_count'
            }).done(function(result) {
                self.cmpn_ovhd_outsource_resource_count =  result[0];
            });
            var def3 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_dlvr_lab_csm_resource_count'
            }).done(function(result) {
                self.dlvr_lab_csm_resource_count =  result[0];
            });
            var def4 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_dlvr_lab_outsource_resource_count'
            }).done(function(result) {
                self.dlvr_lab_outsource_resource_count =  result[0];
            });
            var def5 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_dlvr_ovhd_csm_resource_count'
            }).done(function(result) {
                self.dlvr_ovhd_csm_resource_count =  result[0];
            });
            var def6 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_dlvr_ovhd_outsource_resource_count'
            }).done(function(result) {
                self.dlvr_ovhd_outsource_resource_count =  result[0];
            });
            var def7 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_resource_dpmlnt_csm_resource_count'
            }).done(function(result) {
                self.resource_dplmnt_csm_resource_count =  result[0];
            });
            var def8 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_resource_dpmnlt_outsource_resource_count'
            }).done(function(result) {
                self.resource_dpmnlt_outsource_resource_count =  result[0];
            });
            var def9 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_sbu_resource_count'
            }).done(function(result) {
                self.sbu_resource_count =  result[0];
            });
            var def10 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_horizontal_resource_count'
            }).done(function(result) {
                self.horizontal_resource_count =  result[0];
            });
            var def11 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_talent_pool_resource_count'
            }).done(function(result) {
                self.talent_pool_resource_count =  result[0];
            });
            var def12 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_csuite_resource_count'
            }).done(function(result) {
                self.csuite_resource_count =  result[0];
            });
            var def13 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_delivery_consultancy_resource_count'
            }).done(function(result) {
                self.delivery_consultancy_resource_count =  result[0];
            });
            var def14 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_total_resource_nexus_count'
            }).done(function(result) {
                self.total_resource_count =  result[0];
            });
            var def15 =  this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_out_source_resource_nexus_count'
            }).done(function(result) {
                self.outsource_resource_count =  result[0];
            });
            return $.when(def0,def1,def2,def3,def4,def5,def6,def7,def8,def9,def10,def11,def12,def00,def13,def14,def15);
        },
        
        render_graphs: function(){
            var self = this;
            self.render_department_wise_resource_distribution_container_graph();
            self.render_sbu_wise_resource_countcontainer_graph();
            self.render_count_of_horizontal_resource_container_graph();
            self.render_emp_role_wise_resourcecontainer_graph();
            self.render_sbu_wise_role_container_graph();
            self.render_location_wise_role_distribution_container_graph();
            self.render_engagement_plan_wise_distribution_container_graph();
            self.render_total_delivery_count_container_graph();
            self.render_database_wise_resource_container_graph();
            self.render_emtech_wise_resource_container_graph();
            // self.render_company_branch_resource_count_container_graph();
            

        },
        renderDashboard: async function () {
            var self = this;
            self.$el.find('.employee-role-filter-wrapper').css('display', 'none');
            self.$el.find('#employee-role-filter').click(function () {
                self.$el.find('.employee-role-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_employee_role_filter,#filter-employee-role-button').click(function () {
                self.$el.find('.employee-role-filter-wrapper').css('display', 'none');
            });
            return true;
        },

        resource_nexus_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Workforce Resource Count"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['employement_type.code','!=','O']],
                target: 'current'
            })
    
        },
        delivery_resource_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Delivery Resource Count"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['employement_type.code','!=','O'],['department_id.code','=','BSS']],
                target: 'current'
            })
        },
        company_overhead_csm_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Company Overhead/CSM Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','!=','O'],['emp_role.code','=','O']],
                target: 'current'
            })
    
        },
        company_overhead_outsource_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Company Overhead/Outsource Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','=','O'],['emp_role.code','=','O']],
                target: 'current'
            })
    
        },
        delivery_lab_csm_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Delivery Lab/CSM Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','!=','O'],['emp_role.code','=','DL']],
                target: 'current'
            })
    
        },
        delivery_lab_outsource_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Delivery Lab/Outsource Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','=','O'],['emp_role.code','=','DL']],
                target: 'current'
            })
    
        },
        delivery_overhead_csm_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Delivery Overhead/CSM Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','!=','O'],['emp_role.code','=','S']],
                target: 'current'
            })
    
        },
        delivery_overhead_outsource_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Delivery Overhead/Outsource Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','=','O'],['emp_role.code','=','S']],
                target: 'current'
            })
    
        },
        resource_deployement_csm_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Resource Deployement/CSM Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','!=','O'],['emp_role.code','=','R']],
                target: 'current'
            })
    
        },
        resource_deployement_outsource_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Resource Deployement/Outsource resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','=','O'],['emp_role.code','=','R']],
                target: 'current'
            })
    
        },
        delivery_consultancy_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Delivery Consultancy Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','!=','O'],['emp_role.code','=','DC']],
                target: 'current'
            })
    
        },
        sbu_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("SBU Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['department_id.code','=','BSS'],['sbu_type','=','sbu'],['sbu_master_id','!=',false]],
                target: 'current'
            })
    
        },
        horizontal_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Horizontal Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['department_id.code','=','BSS'],['sbu_master_id.name','not in',['C-Suite']]],
                target: 'current'
            })
    
        },
        talent_pool_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Resource"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                target: 'current'
            })
    
        },
        csuite_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("C-Suite Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['department_id.code','=','BSS'],['sbu_type','=','horizontal'],['sbu_master_id.name','=','C-Suite']],
                target: 'current'
            })
    
        },
        department_wise_resource: function(e, select_deg_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Department Wise Resource Distribution"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ["&",['employement_type.code','!=','O'],['department_id.name', '=', select_deg_bar]],
                target: 'current'
            });
        },
        sbu_wise_resource: function(e,select_sbu_bar) {
            var self = this;
            if (e) {
                e.stopPropagation();
                e.preventDefault();
            }
            self.do_action({
                name: _t("SBU Wise Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['sbu_type', '=', 'sbu'],['sbu_master_id.name', '=', select_sbu_bar],['department_id.code','=','BSS']],
                target: 'current'
            });
        },
        total_delivery_resource: function(e, select_type) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var domain;
        
            if (select_type == 'SBU') {
                domain = [['sbu_type', '=', 'sbu'], ['employement_type.code', '!=', 'O'], ['department_id.code', '=', 'BSS'], ['sbu_master_id', '!=', false]];
            } else if (select_type == 'Horizontal') {
                domain = [['emp_category.code', 'in', ['DIX', 'R&D', 'TQA', 'DBA', 'TD', 'ERP', 'Framework','EIT']]];
            } else if (select_type == 'C-suite') {
                domain = [['sbu_master_id.name', '=', 'C-Suite'], ['employement_type.code', '!=', 'O'], ['department_id.code', '=', 'BSS'], ['sbu_master_id', '!=', false]];
            } else if (select_type == 'Talent Pool') {
                self._getEmployeeIdsFromOtherModel().then(function(employeeIds) {
                    var domain = [['emp_id', 'in', employeeIds]];
                    self._executeAction(domain);
                });
                return; // Exit the function to wait for the async call
            } else {
                domain = [];
            }
        
            self._executeAction(domain);
        },
        
        _getEmployeeIdsFromOtherModel: function() {
            return this._rpc({
                model: 'sbu_bench_resource',
                method: 'search_read',
                args: [],
                fields: ['employee_id'],
            }).then(function(records) {
                return records.map(function(record) {
                    return record.employee_id[0];
                });
            });
        },
        
        _executeAction: function(domain) {
            this.do_action({
                name: _t("Delivery Department Bifurcation"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: domain,
                target: 'current'
            });
        },
        
        horizontal_wise_resource: function(e, select_horizontal_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Horizontal Wise Resource"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['emp_category.name', '=', select_horizontal_bar]],
                target: 'current'
            });
        },       
        sbu_wise_role: function(e, select_role,select_sbu) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Location Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['sbu_master_id.name', '=', select_sbu], ['emp_category', '=', select_role]],
                target: 'current'
            });
        },
        database_wise_role: function(e, db_skill,select_sbu) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Database Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['sbu_master_id.name', '=', select_sbu], ['primary_skill_id.name', '=', db_skill],['emp_role.code','=','DL']],
                target: 'current'
            });
        },
        dba_wise_skill_role: function(e, db_skill,db_role) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("DBA Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill_id.name', '=', db_skill], ['db_role', '=', db_role]],
                target: 'current'
            });
        },
        emtech_skill_wise_skill_role: function(e, emtech_skill,select_sbu) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("EmTech Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill_id.name', '=', emtech_skill],['sbu_master_id.name', '=', select_sbu]],
                target: 'current'
            });
        },
        static_emtech_skill_wise_skill_role: function(e, emtech_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("EmTech Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill_id.name', '=', emtech_skill], ['emp_category.name', '=','Emerging Tech']],
                target: 'current'
            });
        },
        engagement_plan_wise_emp: function(e, select_plan_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Engagement Plan Wise Employee"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['engagement_plan_by_id', '=', select_plan_bar]],
                target: 'current'
            });
        },
        emp_role_wise_resource: function(e, emp_role) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Employee Role"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['emp_category', '=', emp_role],['employement_type.code','!=','O']],
                target: 'current'
            });
        },
        location_wise_role: function(e,select_role,select_loc) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Role Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'work_force_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['emp_category', '=', select_role], ['job_branch_id', '=', select_loc]],
                target: 'current'
            });
        },
        render_company_branch_resource_count_container_graph: function() {
            var self = this;
            var defcompanybranch = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_company_branch_ditribution'
            }).done(function(result) {
                self.branch_wise_resource_count = result;
                var categories = [];
                var seriesData = {};
        
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (designation)
                    var branch = data.name; // branch
                    var branchCount = data.data; // branch count
        
                    if (!seriesData[branch]) {
                        seriesData[branch] = {};
                    }
                    seriesData[branch][category] = branchCount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                for (var branch in seriesData) {
                    var branchData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[branch][category] || 0;
                        branchData.push(count);
                    }
                    series.push({
                        name: branch,
                        data: branchData
                    });
                }
                Highcharts.chart('company_branch_wise_resource_count_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Organisation Resource Count',
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        }
                    },
                    tooltip: {
                        pointFormat: ' <b> {series.name}:{point.y}</b>'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            stacking: 'percent',
                            // point: {
                            //     events: {
                            //         click: function (e) {
                            //             self.location_wise_role(e, this.series.name, this.category);
                            //         }
                            //     }
                            // }
                        }
                    },
                    series: series,
                    colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ], // Add your desired colors here
                });
            });
        },
        render_department_wise_resource_distribution_container_graph: function() {
            var self = this;
            var defdeptresource = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_department_wise_resource_distribution'
            }).done(function(result) {
                self.department_resource_count = result[0];
                if (self.department_resource_count && self.department_resource_count.length > 0) {
                    self.department_resource_count.sort(function(a, b) {
                        if (a && b && a[0] && b[0]) {
                            return a[0].localeCompare(b[0]);
                        }
                        return 0;
                    });
                    // Calculate total count
                    var totalCount = self.department_resource_count.reduce(function(acc, item) {
                        return acc + item[1];
                    }, 0);
                    Highcharts.chart('department_wise_resource_distribution_container', {
                        chart: {
                            type: 'pie',
                            options3d: {
                                enabled: true,
                                alpha: 45
                            }
                        },
                        legend: {
                            itemStyle: {
                                fontSize: '8px',
                                font: '8pt Trebuchet MS, Verdana, sans-serif',
                                color: '#000'
                            },
                            itemHoverStyle: {
                                color: '#FFF'
                            },
                            itemHiddenStyle: {
                                color: '#444'
                            },
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom',
                            itemWidth: 100, // Adjust the width to control the number of items per row
                            useHTML: true
                        },
                        title: {
                            text: 'Total CSM(' + totalCount + ')',
                            align: 'center'
                        },
                        credits: {
                            enabled: false
                        },
                        tooltip: {
                            pointFormat: '<b>Resource {series.name}: {point.y}</b>'
                        },
                        accessibility: {
                            point: {
                                valueSuffix: '%'
                            }
                        },
                        plotOptions: {
                            pie: {
                                innerSize: 100,
                                depth: 45,
                                allowPointSelect: true,
                                showInLegend: true
                            },
                            series: {
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {
                                    padding: 0,
                                    enabled: true,
                                    style: {
                                        fontSize: 10
                                    }
                                }
                            }
                        },
                        series: [{
                            name: 'Count',
                            colors: [
                                '#4DB380', '#991AFF', '#FF6633', '#3366E6', '#FF1A66', '#FF4D4D', '#99E6E6', '#6666FF', '#E6B333',
                                '#99FF99', '#FF99E6', '#66991A', '#4D8066', '#00B3E6', '#1AB399', '#33FFCC', '#E64D66'
                            ],
                            colorByPoint: true,
                            data: self.department_resource_count,
                            point: {
                                events: {
                                    click: function(e) {
                                        self.department_wise_resource(e, this.name);
                                    }
                                }
                            }
                        }]
                    });
                } else {
                    // No data available, show a message in the donut container
                    var container = document.getElementById('department_wise_resource_distribution_container');
                    container.innerHTML = 'No data available.';
                    container.style.textAlign = 'center';
                }
            });
        },
        render_total_delivery_count_container_graph: function() {
            var self = this;
            var totaldelivery = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_total_delivery_resource_count'
            }).done(function(result) {
                self.total_delivery_count = result[0];
                // Calculate total count
                var totalCount = self.total_delivery_count.reduce((sum, item) => sum + item.y, 0);
                Highcharts.chart('total_delivery_resource_distribution_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Total Delivery(' + totalCount + ')'
                    },
                    xAxis: {
                        type: 'category',
                        labels: {
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        },
                    },
                    legend: {
                        enabled: false
                    },
                    credits: {
                        enabled: false
                    },
                    tooltip: {
                        pointFormat: ' <b> Resource Count: {point.y}</b>'
                    },
                    series: [{
                        name: 'Count',
                        colorByPoint: true,
                        colors: [
                            '#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066',
                            '#FF6633', '#00B3E6', '#991AFF', '#1AB399', '#791fb5', '#FF1A66', '#33FFCC',
                            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF', '#E6B333',
                        ], // Add your desired colors here
                        groupPadding: 0,
                        data: self.total_delivery_count,
                        dataLabels: {
                            enabled: true,
                            color: '#FFFFFF',
                            align: 'center',
                            format: '{point.y}', // one int
                            y: 10, // 10 pixels down from the top
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        },
                        point: {
                            events: {
                                click: function(e) {
                                    self.total_delivery_resource(e, this.name);
                                }
                            }
                        }
                    }]
                });
            });
        },
        render_sbu_wise_resource_countcontainer_graph: function() {
            var self = this;
            // RPC call to fetch data
            var defsbu = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_sbu_wise_resource'
            }).done(function(result) {
                // Assuming result[0] is an array of arrays with the format: [["SBU 1", 100], ["SBU 2", 150], ...]
                var data = result[0];
                var categories = data.map(item => item[0]); // Extract SBU names
                var seriesData = data.map(item => item[1]); // Extract values
                // Calculate the total count
                var totalCount = seriesData.reduce((sum, value) => sum + value, 0);
                // Initialize Highcharts
                Highcharts.chart('sbu_wise_resource_count_container', {
                    chart: {
                        type: 'line'
                    },
                    title: {
                        text: 'SBU Count(' + totalCount + ')',
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories
                    },
                    yAxis: {
                        title: {
                            text: 'Number of Employees'
                        }
                    },
                    plotOptions: {
                        line: {
                            dataLabels: {
                                enabled: true
                            },
                            enableMouseTracking: true
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    series: [{
                        name: 'SBU Resource',
                        data: seriesData,
                        point: {
                            events: {
                                click: function() {
                                    // Call the sbu_wise_resource function passing the selected bar name
                                    self.sbu_wise_resource(null, this.category);
                                }
                            }
                        }
                    }],
                    responsive: {
                        rules: [{
                            condition: {
                                maxWidth: 1000
                            },
                            chartOptions: {
                                legend: {
                                    layout: 'horizontal',
                                    align: 'center',
                                    verticalAlign: 'bottom'
                                }
                            }
                        }]
                    }
                });
            });
        },
        
        
        render_count_of_horizontal_resource_container_graph: function() {
            var self = this;
            var defhorizontal = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_horizontal_wise_resource_count'
            }).done(function(result) {
                self.horizontal_resource_count =  result[0];
                // Calculate total count
                var totalCount = self.horizontal_resource_count.reduce(function(acc, item) {
                    return acc + item[1];
                }, 0);
                Highcharts.chart('count_of_horizontal_resource_container', {
                    chart: {
                        type: 'pie',
                    },
                    title: {
                        text: 'Horizontal Count(' + totalCount + ')',
                        align: 'center'
                    },
                    accessibility: {
                        point: {
                            valueSuffix: '%'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        pie: {
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}</b>'
                            },
                            showInLegend: true
                        }
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.y}</b>'
                    },
                    series: [{
                        name: 'Count',
                        colors: [
                            '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                            '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                        ], // Add your desired colors here
                        colorByPoint: true,
                        data: self.horizontal_resource_count,
                        point: {
                            events: {
                                click: function(e) {
                                    // Call the horizontal_wise_resource function passing the selected bar name
                                    self.horizontal_wise_resource(e, this.name);
                                }
                            }
                        }
                    }],
                });               
            });
        },
        render_engagement_plan_wise_distribution_container_graph: function(){
            var self = this;
            var defloc =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_engagement_plan_wise_distribution'
            }).done(function(result) {
                self.engagement_plan_wise_distribution =  result[0];
                // Calculate total count
                var totalCount = self.engagement_plan_wise_distribution.reduce(function(acc, item) {
                    return acc + item[1];
                }, 0);
                Highcharts.chart('engagement_plan_wise_distribution_container', {
                    chart: {
                        type: 'pie',
                        options3d: {
                            enabled: true,
                            alpha: 45
                        }
                    },
                    title: {
                        text: 'Talent Pool Count(' + totalCount + ')',
                        align: 'center'
                    },
                    accessibility: {
                        point: {
                            valueSuffix: '%'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        pie: {
                            innerSize: 100,
                            depth: 45,
                            allowPointSelect: true,
                            showInLegend: true
                        }
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.y}</b>'
                    },
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom',
                        itemWidth: 100,  // Adjust the width to control the number of items per row
                        useHTML: true
                    },
                    series: [{
                        name: 'Count',
                        colors: [
                            '#E6B333','#66991A','#4D8066',
                            '#FF6633', '#00B3E6','#991AFF', '#33FFCC',
                            '#E64D66', '#99E6E6', '#6666FF',
                        ], // Add your desired colors here
                        colorByPoint: true,
                        data: self.engagement_plan_wise_distribution,
                        point: {
                            events: {
                                click: function(e) {
                                    // Call the engagement_plan_wise_emp function passing the selected bar name
                                    self.engagement_plan_wise_emp(e, this.name);
                                }
                            }
                        }
                    }],
                });               
            });
        },
        render_emp_role_wise_resourcecontainer_graph: function() {
            var self = this;
            var defhorizontal = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_employee_role_wise_resource'
            }).done(function(result) {
                self.role_wise_resource_count =  result[0];
                var totalCount = self.role_wise_resource_count.reduce(function(acc, item) {
                    return acc + item[1];
                }, 0);
                Highcharts.chart('emp_role_wise_resourcecontainer', {
                    chart: {
                        type: 'pie',
                    },
                    title: {
                        text: 'Employee Role(' + totalCount + ')',
                        align: 'center'
                    },
                    accessibility: {
                        point: {
                            valueSuffix: '%'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                                pie: {
                                    innerSize: 70,
                                    depth: 45,
                                    allowPointSelect: true,
                                    showInLegend: true
                                }
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.y}</b>'
                    },
                    series: [{
                        name: 'Count',
                        colors: [
                                '#99E6E6', '#6666FF','#3366E6', '#00B3E6','#991AFF',
                                '#99FF99', '#FF99E6','#66991A','#4D8066',
                                '#FF6633',  '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                                '#E64D66', '#4DB380', '#FF4D4D', '#E6B333',
                            ], // Add your desired colors here
                        colorByPoint: true,
                        data: self.role_wise_resource_count,
                        point: {
                            events: {
                                click: function(e) {
                                    self.emp_role_wise_resource(e, this.name);
                                }
                            }
                        }
                    }],
                });               
            });
        },
        render_sbu_wise_role_container_graph: function() {
            var self = this;
            var defskill = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_sbu_wise_role_distribution'
            }).done(function(result) {
                self.location_wise_skill_count = result;
                var categories = [];
                var seriesData = {};
                var categoryTotals = {};
                var overallTotal = 0; // To store the total count across all categories and skills
        
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; 
                    var skill = data.name; 
                    var skillCount = data.data; 
                    
                    if (!seriesData[skill]) {
                        seriesData[skill] = {};
                    }
                    seriesData[skill][category] = skillCount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
        
                    // Add to the total for the current category
                    if (!categoryTotals[category]) {
                        categoryTotals[category] = 0;
                    }
                    categoryTotals[category] += skillCount;
        
                    // Add to the overall total count
                    overallTotal += skillCount;
                }
        
                var series = [];
                for (var skill in seriesData) {
                    var skillData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[skill][category] || 0;
                        skillData.push(count);
                    }
                    series.push({
                        name: skill,
                        data: skillData
                    });
                }
        
                Highcharts.chart('sbu_wise_role_distribution_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: `SBU Wise Role (${overallTotal})`, // Adding the total count to the title
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        }
                    },
                    tooltip: {
                        pointFormat: ' <b>{series.name}: {point.y}</b>'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            stacking: 'percent',
                            point: {
                                events: {
                                    click: function(e) {
                                        self.sbu_wise_role(e, this.series.name, this.category);
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    // To Show Total Count Of Each Category in legend
                    legend: {
                        labelFormatter: function() {
                            var total = 0;
                            var skill = this.name;
                            categories.forEach(function(category) {
                                if (seriesData[skill] && seriesData[skill][category]) {
                                    total += seriesData[skill][category];
                                }
                            });
                            return skill + ' (' + total + ')';
                        }
                    },
                    colors: [
                        '#991AFF', '#1AB399','#791fb5', '#FF1A66', '#3366E6',
                        '#FF6633', '#00B3E6', '#33FFCC',
                        '#99E6E6', '#6666FF','#E6B333',
                    ]
                });
            });
        },
        
        render_location_wise_role_distribution_container_graph: function() {
            var self = this;
            var defskilllocation = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_location_wise_role_ditribution'
            }).done(function(result) {
                self.location_wise_role_count = result;
                var categories = [];
                var seriesData = {};
                var categoryTotals = {};
                var overallTotal = 0; // To store the total count across all categories and roles
        
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category;
                    var role = data.name; 
                    var roleCount = data.data; 
        
                    if (!seriesData[role]) {
                        seriesData[role] = {};
                    }
                    seriesData[role][category] = roleCount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
        
                    // Add to the total for the current category
                    if (!categoryTotals[category]) { 
                        categoryTotals[category] = 0;
                    }
                    categoryTotals[category] += roleCount;
        
                    // Add to the overall total count
                    overallTotal += roleCount;
                }
        
                var series = [];
                for (var role in seriesData) {
                    var roleData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[role][category] || 0;
                        roleData.push(count);
                    }
                    series.push({
                        name: role,
                        data: roleData
                    });
                }
        
                Highcharts.chart('location_wise_role_distribution_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: `Location Wise Role (${overallTotal})`, // Adding the total count to the title
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        }
                    },
                    tooltip: {
                        pointFormat: '<b>{series.name}: {point.y}</b>'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            stacking: 'percent',
                            point: {
                                events: {
                                    click: function(e) {
                                        self.location_wise_role(e, this.series.name, this.category);
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    // To Show Total Count Of Each Category in legend
                    legend: {
                        labelFormatter: function() {
                            var role = this.name;
                            var total = 0;
                            categories.forEach(function(category) {
                                if (seriesData[role] && seriesData[role][category]) {
                                    total += seriesData[role][category];
                                }
                            });
                            return role + ' (' + total + ')';
                        }
                    },
                    colors: [
                        '#66991A','#4D8066','#FF6633','#791fb5',
                        '#FF1A66', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                });
            });
        },
        render_database_wise_resource_container_graph: function() {
            var self = this;
            var defskill = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_dba_wise_resource_distribution'
            }).done(function(result) {
                self.location_wise_skill_count = result;
                var categories = [];
                var seriesData = {};
                var categoryTotals = {};
                var overallTotal = 0; // To store the total count across all categories and roles
        
                // Add static DBA data
                var staticDBAData = {
                    category: 'DBA', // Static category name
                    skills: {
                        'SQL Server': 1,
                        'Oracle': 4,
                    }
                };
        
                // Process static DBA data
                for (var skill in staticDBAData.skills) {
                    var skillCount = staticDBAData.skills[skill];
        
                    if (!seriesData[skill]) {
                        seriesData[skill] = {};
                    }
                    seriesData[skill][staticDBAData.category] = skillCount;
                    overallTotal += skillCount; // Add static DBA count to the overall total
                }
        
                if (!categories.includes(staticDBAData.category)) {
                    categories.push(staticDBAData.category);
                }
        
                // Process dynamic data
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (designation)
                    var skill = data.name; // Skill
                    var skillCount = data.data; // Skill count
        
                    if (!seriesData[skill]) {
                        seriesData[skill] = {};
                    }
                    seriesData[skill][category] = skillCount;
        
                    if (!categoryTotals[category]) {
                        categoryTotals[category] = 0;
                    }
                    categoryTotals[category] += skillCount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
        
                    overallTotal += skillCount; // Add dynamic data count to the overall total
                }
        
                var series = [];
                for (var skill in seriesData) {
                    var skillData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[skill][category] || 0;
                        skillData.push(count);
                    }
                    series.push({
                        name: skill,
                        data: skillData
                    });
                }
        
                // Create legend items with totals
                var legendItems = series.map(function(seriesItem) {
                    var total = 0;
                    for (var i = 0; i < seriesItem.data.length; i++) {
                        var category = categories[i];
                        if (category !== 'DBA') {
                            total += seriesItem.data[i];
                        }
                    }
                    return {
                        name: seriesItem.name,
                        total: total
                    };
                });
        
                Highcharts.chart('database_resource_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: `DBA &nbsp;& &nbsp; DB Developer (${overallTotal})`,
                        align: 'center',
                        useHTML: true 
                    },
                    xAxis: {
                        categories: categories
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        }
                    },
                    tooltip: {
                        pointFormat: ' <b> {series.name}: {point.y}</b>'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            stacking: 'percent',
                            point: {
                                events: {
                                    click: function(e) {
                                        if (this.category === 'DBA') {
                                            self.dba_wise_skill_role(e, this.series.name, this.category);
                                        } else {
                                            self.database_wise_role(e, this.series.name, this.category);
                                        }
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    colors: [
                        '#1AB399', '#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#99E6E6', '#6666FF', '#E6B333'
                    ],
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom',
                        useHTML: true,
                        labelFormatter: function() {
                            var legendItem = legendItems.find(item => item.name === this.name);
                            return this.name + ' (' + legendItem.total + ')';
                        }
                    }
                });
            });
        },
        render_emtech_wise_resource_container_graph: function() {
            var self = this;
            var defskill = this._rpc({
                model: 'work_force_analytics_dashboard',
                method: 'get_emtech_wise_skill_distribution'
            }).done(function(result) {
                self.location_wise_skill_count = result;
                var categories = [];
                var seriesData = {};
                var categoryTotals = {};
                var overallTotal = 0; // To store the total count across all categories and roles
                // Add static EmTech data
                var staticEmTechData = {
                    category: 'EmTech', // Static category name
                    skills: {
                        'AI/ML': 12,
                        'GIS': 5,
                        'IOT': 5,
                        'SAS': 1,
                        'Tableau': 2,
                    }
                };
        
                // Process static EmTech data
                for (var skill in staticEmTechData.skills) {
                    var skillCount = staticEmTechData.skills[skill];
        
                    if (!seriesData[skill]) {
                        seriesData[skill] = {};
                    }
                    seriesData[skill][staticEmTechData.category] = skillCount;
                    overallTotal += skillCount; // Add static EmTech count to the overall total
                }
        
                if (!categories.includes(staticEmTechData.category)) {
                    categories.push(staticEmTechData.category);
                }
        
                // Process dynamic data
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (designation)
                    var skill = data.name; // Skill
                    var skillCount = data.data; // Skill count
        
                    if (!seriesData[skill]) {
                        seriesData[skill] = {};
                    }
                    seriesData[skill][category] = skillCount;
        
                    if (!categoryTotals[category]) {
                        categoryTotals[category] = 0;
                    }
                    categoryTotals[category] += skillCount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                    overallTotal += skillCount; // Add dynamic data count to the overall total
                }
        
                var series = [];
                for (var skill in seriesData) {
                    var skillData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[skill][category] || 0;
                        skillData.push(count);
                    }
                    series.push({
                        name: skill,
                        data: skillData
                    });
                }
        
                // Create legend items with totals
                var legendItems = series.map(function(seriesItem) {
                    var total = 0;
                    for (var i = 0; i < seriesItem.data.length; i++) {
                        var category = categories[i];
                        if (category !== 'EmTech') {
                            total += seriesItem.data[i];
                        }
                    }
                    return {
                        name: seriesItem.name,
                        total: total
                    };
                });
        
                Highcharts.chart('emtech_skill_resource_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: `EmTech Core &nbsp; & &nbsp; SBU (${overallTotal})`, // Adding the total count to the title
                        align: 'center',
                        useHTML: true 
                    },
                    xAxis: {
                        categories: categories
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        }
                    },
                    tooltip: {
                        pointFormat: ' <b>{series.name}: {point.y}</b>'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            stacking: 'percent',
                            point: {
                                events: {
                                    click: function(e) {
                                        if (this.category === 'EmTech') {
                                            self.static_emtech_skill_wise_skill_role(e, this.series.name);
                                        } else {
                                            self.emtech_skill_wise_skill_role(e, this.series.name, this.category);
                                        }
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    colors: [
                        '#4DB380', '#991AFF', '#FF6633', 
                        '#3366E6','#FF1A66', '#FF4D4D','#1AB399','#791fb5',
                        '#FF1A66', '#33FFCC','#E64D66', '#99E6E6', '#6666FF','#E6B333',
                    ], // Add your desired colors here
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom',
                        itemWidth: 150,  // Adjust the width to control the number of items per row
                        useHTML: true,
                        labelFormatter: function() {
                            var legendItem = legendItems.find(item => item.name === this.name);
                            return this.name + ' (' + legendItem.total + ')';
                        }
                    }
                });
            });
        }
    });
    core.action_registry.add('kw_resource_management.rcm_work_force_analytics_dashboard', RCMWorkForceDashboardView);
    return  RCMWorkForceDashboardView;

});