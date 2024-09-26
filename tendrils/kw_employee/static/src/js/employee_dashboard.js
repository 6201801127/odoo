odoo.define('kw_employee.employee_dashboard', function (require) {
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

    var employeeDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        template: 'employeeDashboard',
        init: function (parent, action) {
            this.actionManager = parent;
            this.action = action;
            this.domain = [];
            // this.selectedYear = 0;
            return this._super.apply(this, arguments);
        },
        events: {
            'click .total_head_count': 'total_head_count',
            'click .total_male_head_count': 'total_male_head_count',
            'click .total_female_head_count': 'total_female_head_count',
            'click .total_csm_head_count': 'total_csm_head_count',
            'click .total_subsidary_head_count': 'total_subsidary_head_count',
            'click .total_offsite_head_count': 'total_offsite_head_count',
            'click .total_outsource_head_count': 'total_outsource_head_count',
            'click .total_onsite_head_count': 'total_onsite_head_count',
            
        },
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },
        start: function () {
            var self = this;
            this.set("title", 'Employee Dashboard');
            this.loadFiscalYears(); // Load fiscal years initially
            this.$('#all-fy-wise-filter').on('click', function () {
                self.toggleFiscalYearFilterWrapper();
            });
            this.$('#refresh-dashborad').on('click', function() {
                self.render();
                self.fetch_data();
            });
            this.$('#fiscal_year_filter').on('click', function () {
                self.GetDashboardDataAccFiscalYear();
            });
            this.$('#fy_wise_filter').on('click', function () {
                self.hideFiscalYearFilterWrapper();
            });
            
            this.$('.fy-filter-wrapper').hide();
            return this._super().then(function () {
                setTimeout(function () {
                    self.render();
                }, 0);
            });
        },
        toggleFiscalYearFilterWrapper: function () {
            var wrapper = this.$('.fy-filter-wrapper');
            if (wrapper.is(':visible')) {
                wrapper.hide();
            } else {
                this.loadFiscalYears();
                wrapper.show();
            }
        },
        loadFiscalYears: function () {
            var self = this;
            rpc.query({
                route: '/get_all_fiscal_years',
                params: {},
            }).then(function (result) {
                var fiscalYears = result.fiscal_years || [];
                self.populateFiscalYears(fiscalYears, '#filter-dashboard-fy');
                self.populateFiscalYears(fiscalYears, '#filter-fy-select');
                $('#filter-dashboard-fy').val('').trigger('change'); // Default to "Select"
            });
        },
        hideFiscalYearFilterWrapper: function () {
            var wrapper = this.$('.fy-filter-wrapper');
            wrapper.hide();
        },
        populateFiscalYears: function (fiscalYears, selector) {
            var selectElement = $(selector);
            selectElement.empty();
            selectElement.append($('<option>', {
                value: '',
                text: 'Select'
            }));
            fiscalYears.forEach(function (fy) {
                selectElement.append($('<option>', {
                    value: fy.id,
                    text: fy.name
                }));
            });
        },
        GetDashboardDataAccFiscalYear: function () {
            var selectedYear = $('#filter-dashboard-fy').val();
            
            if (selectedYear) {
                this.render_graphs(selectedYear);
                this.fetch_data(selectedYear);
            } else {
            }
            this.hideFiscalYearFilterWrapper(); 
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            self.render_graphs();
            var employee_dashboard_qweb = QWeb.render('employeeDashboard', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
        },
        fetch_data: async function(fiscalYearId) {
            var self = this;
        
            function formatDate(date) {
                var options = { day: '2-digit', month: 'short', year: 'numeric' };
                return date.toLocaleDateString('en-GB', options).replace(/ /g, '-');
            }
        
            var currentDate = formatDate(new Date());
            self.currentDate = currentDate;
        
            var params = { 'fy_value': fiscalYearId };
        
            var def0 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_total_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.total_head_count_value = result[0];
            });
        
            var def1 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_total_male_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.total_male_count_value = result[0];
            });
        
            var def2 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_total_female_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.total_female_count_value = result[0];
            });
        
            var def3 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_csm_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.csm_head_count_value = result[0];
            });
        
            var def4 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_susidary_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.susidary_head_count_value = result[0];
            });
        
            var def5 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_offsite_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.offsite_head_count_value = result[0];
            });
        
            var def6 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_outsource_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.outsource_head_count_value = result[0];
            });
        
            var def7 = this._rpc({
                model: 'employee_dashboard',
                method: 'get_onsite_head_count',
                args: [],
                kwargs: params
            }).done(function(result) {
                self.onsite_head_count_value = result[0];
            });
        
            return $.when(def0, def1, def2, def3, def4, def5, def6, def7).then(function() {
                $('.total_head_count .rcm-h2').text(self.total_head_count_value);
                $('.total_male_head_count .text-sucess').text(self.total_male_count_value);
                $('.total_female_head_count .text-sucess').text(self.total_female_count_value);
                $('.total_csm_head_count .text-sucess').text(self.csm_head_count_value);
                $('.total_subsidary_head_count .text-sucess').text(self.susidary_head_count_value);
                $('.total_outsource_head_count .text-sucess').text(self.outsource_head_count_value);
                $('.total_offsite_head_count .text-sucess').text(self.offsite_head_count_value);
                $('.total_onsite_head_count .text-sucess').text(self.onsite_head_count_value);
            });
        },        
        render_graphs: function(fiscalYearId){
            var self = this;
            self.renderLevelWiseMaleFemaleCount(fiscalYearId);
            self.renderDepartmentWiseMaleFemaleCount(fiscalYearId);
            self.renderDesignationWiseMaleFemaleCount(fiscalYearId);
            self.renderLocationWiseMaleFemaleCount(fiscalYearId);
            self.renderAgeWiseMaleFemaleCount(fiscalYearId);
            self.renderTenureWiseMaleFemaleCount(fiscalYearId);
            self.renderFYWiseResourceAdditionCount(fiscalYearId);
            self.render_sbu_wise_resource_countcontainer_graph(fiscalYearId);
            self.render_emp_role_wise_resourcecontainer_graph(fiscalYearId);
            self.renderQuaterWiseResourceAdditionCount(fiscalYearId);
            self.render_Outsource_wise_resource_countcontainer_graph(fiscalYearId);
            self.render_DayStatus_wise_resourcecontainer_graph(fiscalYearId);
            self.render_CompanyWise_wise_resourcecontainer_graph(fiscalYearId);

        },
        total_head_count: function(e){
            var self = this;
            var selectedFiscalYearId = $('#filter-dashboard-fy').val();
            var domain = [['active_rec','=',true]];
            if (selectedFiscalYearId) {
                console.log("selectedFiscalYearId===",selectedFiscalYearId,"***",selectedFiscalYearId.date_start)
                domain.push(['date_of_joining', '=', selectedFiscalYearId]);
            }
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['active_rec','=',true]],
                target: 'current'
            })
        },
        total_male_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Male Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['gender','=','male'],['employement_type.code','!=','O'],['active_rec','=',true]],
                target: 'current'
            })
        },
        total_female_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Female Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['gender','=','female'],['employement_type.code','!=','O'],['active_rec','=',true]],
                target: 'current'
            })
        },
        total_csm_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total CSM Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['employement_type.code','!=','O'],['active_rec','=',true]],
                target: 'current'
            })
        },
        total_subsidary_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Subsidiary Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['company_id','!=',1],['active_rec','=',true]],
                target: 'current'
            })
        },
        total_offsite_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Offsite Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['employement_type.code','!=','O'],['location','=','offsite'],['active_rec','=',true]],
                target: 'current'
            })
        },
        total_outsource_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Outsource Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['employement_type.code','=','O'],['active_rec','=',true]],
                target: 'current'
            })
        },
        total_onsite_head_count: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Onsite Head Count"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['employement_type.code','!=','O'],['location','=','onsite'],['active_rec','=',true]],
                target: 'current'
            })
        },
        department_wise_gender: function(e, select_gender,select_dept) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var WhiteSpace = ' '
            var actionName = `${select_dept} ${WhiteSpace} Department ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`;
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['gender', '=', select_gender], ['department_id', '=', select_dept],['active_rec','=',true]],
                target: 'current'
            });
        },
        designation_wise_gender: function(e, select_gender,select_desig) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var WhiteSpace = ' '
            var actionName = _t(`${select_desig} ${WhiteSpace} Designation ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`);
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['gender', '=', select_gender], ['job_id', '=', select_desig],['active_rec','=',true]],
                target: 'current'
            });
        },
        level_wise_gender: function(e, select_gender,select_level) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var WhiteSpace = ' '
            var actionName = _t(`Level - ${select_level} ${WhiteSpace} ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`);
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['gender','=', select_gender], ['emp_level','=', select_level],['active_rec','=',true]],
                target: 'current'
            });
        },
        location_wise_gender: function(e, select_gender,select_location) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var WhiteSpace = ' '
            var actionName = _t(`${select_location} ${WhiteSpace} Location  ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`);
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['gender','=', select_gender], ['job_branch_id','=', select_location],['active_rec','=',true]],
                target: 'current'
            });
        },
        age_wise_gender: function (e, select_gender, select_age_group) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var currentYear = new Date().getFullYear();
            const calculateDateRange = (minAge, maxAge) => {
                const startYear = currentYear - maxAge;
                const endYear = currentYear - minAge;
                return [`${startYear}-01-01`, `${endYear}-12-31`];
            };
            const ageGroupRanges = {
                '18-24': calculateDateRange(18, 24),
                '25-30': calculateDateRange(25, 30),
                '31-35': calculateDateRange(31, 35),
                '36-40': calculateDateRange(36, 40),
                '41-50': calculateDateRange(41, 50),
                '50+': ['1900-01-01', `${currentYear - 50}-12-31`]  // up to 50 years ago
            };
            const dateRange = ageGroupRanges[select_age_group] || [];
            const [startDate, endDate] = dateRange;
            var WhiteSpace = ' ';
            var actionName = _t(`${select_age_group} ${WhiteSpace} Age Group ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`);
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [
                    ['gender', '=', select_gender],
                    ['birthday', '>=', startDate],
                    ['birthday', '<=', endDate],
                    ['active_rec', '=', true]
                ],
                target: 'current'
            });
        },
        fy_wise_gender: function(e, select_gender,select_fy) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var fyYearParts = select_fy.split('-');
            if (fyYearParts.length !== 2) {
                return;
            }
            var startYear = parseInt(fyYearParts[0]);
            var endYear = parseInt(fyYearParts[1]);
            var startDate = `${startYear}-04-01`;
            var endDate = `${endYear}-03-31`;
            var WhiteSpace = ' '
            var actionName = _t(`FY - ${select_fy} ${WhiteSpace}  ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`);
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [
                    ['gender', '=', select_gender],
                    ['date_of_joining', '>=', startDate],
                    ['date_of_joining', '<=', endDate],
                    ['active_rec', '=', true]
                ],
                target: 'current'
            });
        },
        tenure_wise_gender_count: function (e, select_gender, tenure_range) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var currentDate = new Date();
            var startDate, endDate;
            tenure_range = tenure_range.trim();
            switch (tenure_range) {
                case 'Less than 1 year':
                    startDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), currentDate.getDate() + 1).toISOString().split('T')[0];
                    endDate = currentDate.toISOString().split('T')[0];
                    break;
                case '1-5 years':
                    startDate = new Date(currentDate.getFullYear() - 5, currentDate.getMonth(), currentDate.getDate() + 1).toISOString().split('T')[0];
                    endDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), currentDate.getDate()).toISOString().split('T')[0];
                    break;
                case '6-10 years':
                    startDate = new Date(currentDate.getFullYear() - 10, currentDate.getMonth(), currentDate.getDate() + 1).toISOString().split('T')[0];
                    endDate = new Date(currentDate.getFullYear() - 6, currentDate.getMonth(), currentDate.getDate()).toISOString().split('T')[0];
                    break;
                case 'More than 10 years':
                    startDate = new Date(currentDate.getFullYear() - 20, currentDate.getMonth(), currentDate.getDate()).toISOString().split('T')[0];
                    endDate = new Date(currentDate.getFullYear() - 11, currentDate.getMonth(), currentDate.getDate()).toISOString().split('T')[0];
                    break;
                default:
                    return;
            }
            var WhiteSpace = ' ';
            var actionName = _t(`${tenure_range} ${WhiteSpace} Tenure ${select_gender.charAt(0).toUpperCase() + select_gender.slice(1)} ${WhiteSpace} Count`);
            self.do_action({
                name: actionName,
                type: 'ir.actions.act_window',
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [
                    ['gender', '=', select_gender],
                    ['date_of_joining', '>=', startDate],
                    ['date_of_joining', '<=', endDate],
                    ['active_rec', '=', true]
                ],
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
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['sbu_type', '=', 'sbu'],['sbu_master_id.name', '=', select_sbu_bar],['active_rec','=',true]],
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
                res_model: 'hr.employee.mis.report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['emp_category', '=', emp_role],['employement_type.code','!=','O'],['active_rec','=',true]],
                target: 'current'
            });
        },
        renderLevelWiseMaleFemaleCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            try {
                var LevelGenderData = await this._rpc({
                    model: 'employee_dashboard',
                    method: 'level_wise_male_female_count',
                    kwargs: params,
                });
                if (Array.isArray(LevelGenderData) && LevelGenderData.length > 0) {
                    var categories = [];
                    var maleData = [];
                    var femaleData = [];
                    LevelGenderData.forEach(function (item) {
                        categories.push(item.name);
                        maleData.push(item.male_count);
                        femaleData.push(item.female_count);
                    });
                    Highcharts.chart('level_wise_male_female_count_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Level-Wise Count',
                            align: 'center'
                        },
                        xAxis: {
                            categories: categories,
                            crosshair: true,
                            accessibility: {
                                description: 'Level'
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: 'Count'
                            }
                        },
                        tooltip: {
                            valueSuffix: ' (Resource)'
                        },
                        plotOptions: {
                            column: { 
                                depth: 35,
                                borderRadius: 5,
                                dataLabels: {
                                    enabled: true,
                                    format: '{y}',
                                    style: {
                                        fontWeight: 'bold'
                                    }
                                },
                                shadow: {
                                    color: 'rgba(0, 0, 0, 0.3)',
                                    offsetX: 1,
                                    offsetY: 1,
                                    width: 3
                                }, point: {
                                    events: {
                                        click: function (e) {
                                            var gender = this.series.name.toLowerCase();
                                            var level = this.category;
                                            self.level_wise_gender(e, gender, level);
                                        }
                                    }
                                }
                            },
                        },
                        credits: {
                            enabled: false
                        },
                        series: [
                            {
                                name: 'Female',
                                data: femaleData,
                                color: '#FA7070'
                            },
                            {
                                name: 'Male',
                                data: maleData,
                                color: '#77E4C8'
                            },
                            
                        ]
                    });
                } else {
                    var container = document.getElementById('level_wise_male_female_count_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            } catch (error) {
                var container = document.getElementById('level_wise_male_female_count_container');
                container.innerHTML = 'Error fetching data';
                container.style.textAlign = 'center';
            }
        },
        renderDepartmentWiseMaleFemaleCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            var DeptGenderData = this._rpc({
                model: 'employee_dashboard',
                method: 'department_wise_male_female_count',
                kwargs: params,
            }).done(function (result) {
                self.location_wise_skill_count = result;
                if(result && result.length >0) {
                var categories = [];
                var seriesData = {};

                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category;
                    var Gender = data.name;
                    var GenderCount = data.data;

                    if (!seriesData[Gender]) {
                        seriesData[Gender] = {};
                    }
                    seriesData[Gender][category] = GenderCount;

                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                for (var Gender in seriesData) {
                    var GenderData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[Gender][category] || 0;
                        GenderData.push(count);
                    }
                    series.push({
                        name: Gender,
                        data: GenderData
                    });
                }
                Highcharts.chart('dept_wise_male_fenale_count_container', {
                    chart: {
                        type: 'bar'
                    },
                    title: {
                        text: 'Department Wise Count',
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories,
                        title: {
                            text: null
                        },
                        gridLineWidth: 1,
                        lineWidth: 0
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Count',
                            align: 'high'
                        },
                        labels: {
                            overflow: 'justify'
                        },
                        gridLineWidth: 0
                    },

                    plotOptions: {
                        bar: {
                            point: {
                                events: {
                                    click: function (e) {
                                            var gender = this.series.name.toLowerCase();
                                            var dept = this.category;
                                            self.department_wise_gender(e, gender, dept);
                                        }
                                }
                            },
                            groupPadding: 0.1,
                            showInLegend: true,
                            stacking: 'normal'
                        }
                    },
                    
                    credits: {
                        enabled: false
                    },
                    series: series,
                    colors: [
                        '#A2CA71','#5B99C2'
                    ], 
                });
            }else {
                var container = document.getElementById('dept_wise_male_fenale_count_container');
                container.innerHTML = 'No Data Available.';
                container.style.textAlign = 'center';

            }
        });
        },
        renderDesignationWiseMaleFemaleCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            var DeptGenderData = this._rpc({
                model: 'employee_dashboard',
                method: 'designation_wise_male_female_count',
                kwargs: params,
            }).done(function (result) {
                self.location_wise_skill_count = result;
                if(result && result.length >0) {
                var categories = [];
                var seriesData = {};

                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category;
                    var Gender = data.name;
                    var GenderCount = data.data;

                    if (!seriesData[Gender]) {
                        seriesData[Gender] = {};
                    }
                    seriesData[Gender][category] = GenderCount;

                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                for (var Gender in seriesData) {
                    var GenderData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[Gender][category] || 0;
                        GenderData.push(count);
                    }
                    series.push({
                        name: Gender,
                        data: GenderData
                    });
                }
                Highcharts.chart('desg_wise_male_female_count_container', {
                    chart: {
                        type: 'bar'
                    },
                    title: {
                        text: 'Designation Wise Count',
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories,
                        title: {
                            text: null
                        },
                        gridLineWidth: 1,
                        lineWidth: 0
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Count',
                            align: 'high'
                        },
                        labels: {
                            overflow: 'justify'
                        },
                        gridLineWidth: 0
                    },

                    plotOptions: {
                        bar: {
                            point: {
                                events: {
                                    click: function (e) {
                                        var gender = this.series.name.toLowerCase();
                                        self.designation_wise_gender(e, gender, this.category);
                                    }
                                }
                            },
                            groupPadding: 0.1,
                            showInLegend: true,
                            stacking: 'normal'
                        }
                    },
                    
                    credits: {
                        enabled: false
                    },
                    series: series,
                    colors: [
                        '#FF8A8A','#41B3A2'
                    ], 
                });
            }else {
                var container = document.getElementById('desg_wise_male_female_count_container');
                container.innerHTML = 'No Data Available.';
                container.style.textAlign = 'center';
            }
        });
        },
        renderLocationWiseMaleFemaleCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            try {
                var LocationGenderData = await this._rpc({
                    model: 'employee_dashboard',
                    method: 'location_wise_male_female_count',
                    kwargs: params,
                });
                if (Array.isArray(LocationGenderData) && LocationGenderData.length > 0) {
                    var categories = [];
                    var maleData = [];
                    var femaleData = [];
                    LocationGenderData.forEach(function (item) {
                        categories.push(item.name);
                        maleData.push(item.male_count);
                        femaleData.push(item.female_count);
                    });
                    Highcharts.chart('location_wise_male_female_count_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Location-Wise Count',
                            align: 'center'
                        },
                        xAxis: {
                            categories: categories,
                            crosshair: true,
                            accessibility: {
                                description: 'Location'
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: 'Count'
                            }
                        },
                        tooltip: {
                            valueSuffix: ' (Resources)'
                        },
                        plotOptions: {
                            column: {
                                pointPadding: 0.2,
                                borderWidth: 0,
                                point: {
                                    events: {
                                        click: function (e) {
                                            var gender = this.series.name.toLowerCase(); // Convert to lowercase
                                            var location = this.category
                                            self.location_wise_gender(e, gender, location);
                                        }
                                    }
                                }
                            }
                        },
                        credits: {
                                enabled: false
                            },
                        series: [
                            {
                                name: 'Female',
                                data: femaleData,
                                color: '#FF9800'
                            },
                            {
                                name: 'Male',
                                data: maleData,
                                color: '#2C7865'
                            },
                            
                        ]
                    });
                } else {
                    var container = document.getElementById('location_wise_male_female_count_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            } catch (error) {
                var container = document.getElementById('location_wise_male_female_count_container');
                container.innerHTML = 'Error fetching data';
                container.style.textAlign = 'center';
            }
        },
        renderAgeWiseMaleFemaleCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            try {
                var AgeGenderData = await this._rpc({
                    model: 'employee_dashboard',
                    method: 'age_wise_male_female_count',
                    kwargs: params,
                });
        
        
                if (Array.isArray(AgeGenderData) && AgeGenderData.length > 0) {
                    var ageGroups = [];
                    var maleData = [];
                    var femaleData = [];
        
                    AgeGenderData.forEach(function (item) {
                        ageGroups.push(item.age_group);
                        maleData.push(item.male_count);
                        femaleData.push(item.female_count);
                    });
                    Highcharts.chart('age_wise_male_female_count_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Age-Wise Count',
                            align: 'center'
                        },
                        xAxis: {
                            categories: ageGroups,
                            crosshair: true,
                            accessibility: {
                                description: 'Age Group'
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: 'Count'
                            }
                        },
                        tooltip: {
                            valueSuffix: ' (Resources)'
                        },
                        plotOptions: {
                            column: {
                                pointPadding: 0.2,
                                borderWidth: 0,
                                point: {
                                    events: {
                                        click: function (e) {
                                            var gender = this.series.name.toLowerCase(); 
                                            var ageGroup = this.category; 
                                            self.age_wise_gender(e, gender, ageGroup);
                                        }
                                    }
                                }
                            }
                        },
                        credits: {
                            enabled: false
                        },
                        series: [
                            {
                                name: 'Female',
                                data: femaleData,
                                color: '#893BFF'
                            },
                            {
                                name: 'Male',
                                data: maleData,
                                color: '#FF0000'
                            },
                            
                        ]
                    });
                } else {
                    var container = document.getElementById('age_wise_male_female_count_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            } catch (error) {
                var container = document.getElementById('age_wise_male_female_count_container');
                container.innerHTML = 'Error fetching data';
                container.style.textAlign = 'center';
            }
        },
        renderFYWiseResourceAdditionCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            try {
                var FYWiseGenderData = await this._rpc({
                    model: 'employee_dashboard',
                    method: 'fy_wise_male_female_count',
                    kwargs: params,
                });
                if (Array.isArray(FYWiseGenderData) && FYWiseGenderData.length > 0) {
                    var categories = [];
                    var maleData = [];
                    var femaleData = [];
                    FYWiseGenderData.forEach(function (item) {
                        categories.push(item.name);
                        maleData.push(item.male_count);
                        femaleData.push(item.female_count);
                    });
        
                    Highcharts.chart('fy_wise_resource_addition_count_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Resource Addition FY-Wise Count',
                            align: 'center'
                        },
                        xAxis: {
                            categories: categories,
                            crosshair: true,
                            accessibility: {
                                description: 'FY'
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: 'Count'
                            }
                        },
                        tooltip: {
                            valueSuffix: ' (Resources)'
                        },
                        plotOptions: {
                            column: {
                                pointPadding: 0.2,
                                borderWidth: 0,
                                stacking: 'normal',
                                point: {
                                    events: {
                                        click: function (e) {
                                            var gender = this.series.name.toLowerCase();
                                            var fydata = this.category;
                                            self.fy_wise_gender(e, gender, fydata);
                                        }
                                    }
                                }
                            }
                        },
                        credits: {
                            enabled: false
                        },
                        series: [
                            {
                                name: 'Female',
                                data: femaleData,
                                color: '#B33030'
                            },
                            {
                                name: 'Male',
                                data: maleData,
                                color: '#D3ECA7'
                            },
                            
                        ]
                    });
                } else {
                    var container = document.getElementById('fy_wise_resource_addition_count_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            } catch (error) {
                var container = document.getElementById('fy_wise_resource_addition_count_container');
                container.innerHTML = 'Error fetching data';
                container.style.textAlign = 'center';
            }
        },
        renderTenureWiseMaleFemaleCount: function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            rpc.query({
                model: 'employee_dashboard',
                method: 'headcount_by_tenure_range',
                kwargs: params,
            }).then(function (data) {
        
                if (!data || Object.keys(data).length === 0) {
                    var container = document.getElementById('tenure_wise_male_female_count_container');
                    container.innerHTML = 'No Data Available.';
                    container.style.textAlign = 'center';
                    return;
                }
        
                var categories = Object.keys(data);
                var seriesDataMale = [];
                var seriesDataFemale = [];
        
                categories.forEach(function (category) {
                    seriesDataMale.push(data[category]['Male'] || 0);
                    seriesDataFemale.push(data[category]['Female'] || 0);
                });
        
                Highcharts.chart('tenure_wise_male_female_count_container', {
                    chart: {
                        type: 'bar'
                    },
                    title: {
                        text: 'Headcount by Tenure Range'
                    },
                    xAxis: {
                        categories: categories,
                        title: {
                            text: null
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Count',
                            align: 'high'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    plotOptions: {
                        bar: {
                            dataLabels: {
                                enabled: true
                            },
                            events: {
                                click: function (event) {
                                    var category = event.point.category;
                                    var gender = event.point.series.name.toLowerCase();
                                    self.tenure_wise_gender_count(event, gender, category);
                                }
                            }
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    series: [
                        {
                            name: 'Female',
                            data: seriesDataFemale
                        },{
                        name: 'Male',
                        data: seriesDataMale
                    },
                   
                ],
                    colors: ['#6F2DA8', '#16F529'],
                });
            }).fail(function (error) {
                var container = document.getElementById('tenure_wise_male_female_count_container');
                container.innerHTML = '<p>Error fetching data. Please try again later.</p>';
            });
        },
        render_sbu_wise_resource_countcontainer_graph: function(fiscalYearId) {
            var self = this;
            var params = { 'fy_value': fiscalYearId };
        
            var defsbu = this._rpc({
                model: 'employee_dashboard',
                method: 'get_sbu_wise_data',
                kwargs: params,
            }).done(function(result) {
                var data = result[0];
        
                if (!data || data.length === 0) {
                    var container = document.getElementById('sbu_wise_resource_count_container');
                    container.innerHTML = 'No Data Available.';
                    container.style.textAlign = 'center';
                    return;
                }
        
                var categories = data.map(item => item[0]); 
                var seriesData = data.map(item => item[1]); 
        
                Highcharts.chart('sbu_wise_resource_count_container', {
                    chart: {
                        type: 'line'
                    },
                    title: {
                        text: 'SBU Count',
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
            }).fail(function(error) {
                var container = document.getElementById('sbu_wise_resource_count_container');
                container.innerHTML = '<p>Error fetching data. Please try again later.</p>';
                container.style.textAlign = 'center';
            });
        },        
        render_emp_role_wise_resourcecontainer_graph: function(fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            var defhorizontal = this._rpc({
                model: 'employee_dashboard',
                method: 'get_role_wise_data',
                kwargs: params,
            }).done(function(result) {
                self.role_wise_resource_count =  result[0];
                if (!self.role_wise_resource_count || self.role_wise_resource_count.length === 0) {
                    var container = document.getElementById('role_wise_resource_count_container');
                    container.innerHTML = 'No Data Available.';
                    container.style.textAlign = 'center';
                    return;
                }
                Highcharts.chart('role_wise_resource_count_container', {
                    chart: {
                        type: 'pie',
                    },
                    title: {
                        text: 'Employee Role',
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
                            ],
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
            }).fail(function(error) {
                var container = document.getElementById('role_wise_resource_count_container');
                container.innerHTML = '<p>Error fetching data. Please try again later.</p>';
                container.style.textAlign = 'center';
            });
        },
        renderQuaterWiseResourceAdditionCount: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            try {
                var FYWiseGenderData = await this._rpc({
                    model: 'employee_dashboard',
                    method: 'quater_wise_resource_addition_count',
                    kwargs: params,
                });
                if (Array.isArray(FYWiseGenderData) && FYWiseGenderData.length > 0) {
                    var categories = [];
                    var maleData = [];
                    var femaleData = [];
                    FYWiseGenderData.forEach(function (item) {
                        categories.push(item.name);
                        maleData.push(item.male_count);
                        femaleData.push(item.female_count);
                    });
        
                    Highcharts.chart('quater_wise_resource_addition_count_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Resource Addition Quater-Wise Count',
                            align: 'center'
                        },
                        xAxis: {
                            categories: categories,
                            crosshair: true,
                            accessibility: {
                                description: 'FY'
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: 'Count'
                            }
                        },
                        tooltip: {
                            valueSuffix: ' (Resources)'
                        },
                        plotOptions: {
                            column: {
                                pointPadding: 0.2,
                                borderWidth: 0,
                                stacking: 'normal',
                                point: {
                                    events: {
                                        click: function (e) {
                                            var gender = this.series.name.toLowerCase();
                                            var fydata = this.category;
                                            self.fy_wise_gender(e, gender, fydata);
                                        }
                                    }
                                }
                            }
                        },
                        credits: {
                            enabled: false
                        },
                        series: [
                            {
                                name: 'Female',
                                data: femaleData,
                                color: '#B33030'
                            },
                            {
                                name: 'Male',
                                data: maleData,
                                color: '#D3ECA7'
                            },
                            
                        ]
                    });
                } else {
                    var container = document.getElementById('quater_wise_resource_addition_count_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            } catch (error) {
                var container = document.getElementById('quater_wise_resource_addition_count_container');
                container.innerHTML = 'Error fetching data';
                container.style.textAlign = 'center';
            }
        },
        render_Outsource_wise_resource_countcontainer_graph: async function (fiscalYearId) {
            var self = this;
            var params
            params = { 'fy_value':fiscalYearId}
            
            try {
                var FYWiseGenderData = await this._rpc({
                    model: 'employee_dashboard',
                    method: 'outsource_wise_male_female_count',
                    kwargs: params,
                });
                if (Array.isArray(FYWiseGenderData) && FYWiseGenderData.length > 0) {
                    var categories = [];
                    var maleData = [];
                    var femaleData = [];
                    FYWiseGenderData.forEach(function (item) {
                        categories.push(item.name);
                        maleData.push(item.male_count);
                        femaleData.push(item.female_count);
                    });
                    
                    Highcharts.chart('outsource_wise_resource_count_container', {
                        
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Outsource Resource Count',
                            align: 'center'
                        },
                        xAxis: {
                            categories: categories,
                            crosshair: true,
                            accessibility: {
                                description: 'FY'
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: 'Count'
                            }
                        },
                        tooltip: {
                            
                            valueSuffix: ' (Resources)'
                        },
                        plotOptions: {
                            column: {
                                pointPadding: 0.2,
                                borderWidth: 0,
                                point: {
                                    events: {
                                        click: function (e) {
                                            var gender = this.series.name.toLowerCase();
                                            // var fydata = this.category;
                                            self.outsource_wise_gender(e, gender);
                                        }
                                    }
                                }
                            }
                        },
                        credits: {
                            enabled: false
                        },
                        series: [
                            {
                                name: 'Female',
                                data: femaleData,
                                color: '#B73030'
                            },
                            {
                                name: 'Male',
                                data: maleData,
                                color: '#D9ECA7'
                            },
                            
                        ]
                    });
                } else {
                    var container = document.getElementById('outsource_wise_resource_count_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            } catch (error) {
                
                var container = document.getElementById('outsource_wise_resource_count_container');
                container.innerHTML = 'Error Fetching data';
                container.style.textAlign = 'center';
            }
        },
        
        
        
    });

    core.action_registry.add('employee_dashboard', employeeDashboard);
});



        // render_sbu_wise_role_container_graph: function() {
            //     var self = this;
            //     var defskill = this._rpc({
                //         model: 'work_force_analytics_dashboard',
        //         method: 'get_sbu_wise_role_distribution'
        //     }).done(function(result) {
        //         self.location_wise_skill_count = result;
        //         var categories = [];
        //         var seriesData = {};
        //         var categoryTotals = {};
        //         var overallTotal = 0; // To store the total count across all categories and skills
        
        //         for (var i = 0; i < result.length; i++) {
        //             var data = result[i];
        //             var category = data.category; 
        //             var skill = data.name; 
        //             var skillCount = data.data; 
                    
        //             if (!seriesData[skill]) {
        //                 seriesData[skill] = {};
        //             }
        //             seriesData[skill][category] = skillCount;
        
        //             if (!categories.includes(category)) {
        //                 categories.push(category);
        //             }
        
        //             // Add to the total for the current category
        //             if (!categoryTotals[category]) {
        //                 categoryTotals[category] = 0;
        //             }
        //             categoryTotals[category] += skillCount;
        
        //             // Add to the overall total count
        //             overallTotal += skillCount;
        //         }
        
        //         var series = [];
        //         for (var skill in seriesData) {
        //             var skillData = [];
        //             for (var i = 0; i < categories.length; i++) {
        //                 var category = categories[i];
        //                 var count = seriesData[skill][category] || 0;
        //                 skillData.push(count);
        //             }
        //             series.push({
        //                 name: skill,
        //                 data: skillData
        //             });
        //         }
        
        //         Highcharts.chart('sbu_wise_role_distribution_container', {
        //             chart: {
        //                 type: 'column'
        //             },
        //             title: {
        //                 text: `SBU Wise Role (${overallTotal})`, // Adding the total count to the title
        //                 align: 'center'
        //             },
        //             xAxis: {
        //                 categories: categories
        //             },
        //             yAxis: {
        //                 min: 0,
        //                 title: {
        //                     text: ''
        //                 }
        //             },
        //             tooltip: {
        //                 pointFormat: ' <b>{series.name}: {point.y}</b>'
        //             },
        //             credits: {
        //                 enabled: false
        //             },
        //             plotOptions: {
        //                 column: {
        //                     stacking: 'percent',
        //                     point: {
        //                         events: {
        //                             click: function(e) {
        //                                 self.sbu_wise_role(e, this.series.name, this.category);
        //                             }
        //                         }
        //                     }
        //                 }
        //             },
        //             series: series,
        //             // To Show Total Count Of Each Category in legend
        //             legend: {
        //                 labelFormatter: function() {
        //                     var total = 0;
        //                     var skill = this.name;
        //                     categories.forEach(function(category) {
        //                         if (seriesData[skill] && seriesData[skill][category]) {
        //                             total += seriesData[skill][category];
        //                         }
        //                     });
        //                     return skill + ' (' + total + ')';
        //                 }
        //             },
        //             colors: [
        //                 '#991AFF', '#1AB399','#791fb5', '#FF1A66', '#3366E6',
        //                 '#FF6633', '#00B3E6', '#33FFCC',
        //                 '#99E6E6', '#6666FF','#E6B333',
        //             ]
        //         });
        //     });
        // },
