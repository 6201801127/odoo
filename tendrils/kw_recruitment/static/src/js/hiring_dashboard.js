odoo.define('kw_recruitment_hiring_dashboard', function (require) {
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

    var RecruitmentDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        events: {
            'click #filter-fy-button1': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select1').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet1': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data1 = true;
                self.render_ageing_to_joined_ratio_container_graph("refresh_edging_portlet1");
            }, 0, true),
            'click #filter-fy-button2': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select2').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_grade_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_grade_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet2': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data2 = true;
                self.render_ageing_to_joined_ratio_grade_container_graph("refresh_edging_portlet2");
            }, 0, true),
            'click #filter-fy-button3': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select3').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_dept_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_dept_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet3': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data3 = true;
                self.render_ageing_to_joined_ratio_dept_container_graph("refresh_edging_portlet3");
            }, 0, true),
            'click #filter-fy-button4': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select4').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_loc_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_loc_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet4': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data4 = true;
                self.render_ageing_to_joined_ratio_loc_container_graph("refresh_edging_portlet4");
            }, 0, true),
            'click #filter-fy-button5': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select5').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_budget_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_budget_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet5': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data5 = true;
                self.render_ageing_to_joined_ratio_budget_container_graph("refresh_edging_portlet5");
            }, 0, true),
            'click #filter-fy-button6': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select6').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_resource_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_resource_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet6': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data6 = true;
                self.render_ageing_to_joined_ratio_resource_container_graph("refresh_edging_portlet6");
            }, 0, true),
            'click #filter-fy-button7': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select7').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_hire_res_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_hire_res_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet7': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data7 = true;
                self.render_ageing_to_joined_ratio_hire_res_container_graph("refresh_edging_portlet7");
            }, 0, true),
            'click #filter-fy-button8': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select8').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_skill_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_skill_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet8': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data8 = true;
                self.render_ageing_to_joined_ratio_skill_container_graph("refresh_edging_portlet8");
            }, 0, true),
            'click #filter-fy-button9': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select9').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_company_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_company_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet9': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data9 = true;
                self.render_ageing_to_joined_ratio_company_container_graph("refresh_edging_portlet9");
            }, 0, true),
            'click #filter-fy-button10': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select10').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_desig_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_desig_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet10': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data10 = true;
                self.render_ageing_to_joined_ratio_desig_container_graph("refresh_edging_portlet10");
            }, 0, true),
            'click #filter-fy-button11': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-select11').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_joined_ratio_recruiter_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_joined_ratio_recruiter_container_graph('');
            }, 0, true),
        
            'click .refresh_portlet11': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data11 = true;
                self.render_ageing_to_joined_ratio_recruiter_container_graph("refresh_edging_portlet11");
            }, 0, true),

        },
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_hiring_dashboard_tag') {
                self._rpc({
                    model: 'recruitment_data_dashboard',
                    method: 'get_filter_data',
                }, []).then(function (result) {
                    self.edging_fy_filters = result['dashboard_fy_filters'][0];
                }).done(function () {
                    self.render();
                    self.href = window.location.href;
                });
            }
        },
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Hiring Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('HiringDashboard', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(hr_dashboard).prependTo(self.$el);
            self.render_graphs();
            self.renderDashboard();
            return hr_dashboard
        },
        
        render_graphs: function(){
            var self = this;
            self.render_ageing_to_joined_ratio_container_graph();
            self.render_ageing_to_joined_ratio_grade_container_graph();
            self.render_ageing_to_joined_ratio_dept_container_graph();
            self.render_ageing_to_joined_ratio_loc_container_graph();
            self.render_ageing_to_joined_ratio_budget_container_graph();
            self.render_ageing_to_joined_ratio_resource_container_graph();
            self.render_ageing_to_joined_ratio_hire_res_container_graph();
            self.render_ageing_to_joined_ratio_skill_container_graph();
            self.render_ageing_to_joined_ratio_company_container_graph();
            self.render_ageing_to_joined_ratio_desig_container_graph();
            self.render_ageing_to_joined_ratio_recruiter_container_graph();
            
        },

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.fiscal-year-filter-wrapper,.fy-grade-filter-wrapper,.fy-department-filter-wrapper,.fy-location-filter-wrapper,.fy-budget-filter-wrapper,.fy-resource-filter-wrapper,.fy-hiring-filter-wrapper,.fy-skill-filter-wrapper,.fy-company-filter-wrapper,.fy-desg-filter-wrapper,.fy-recruiter-filter-wrapper').css('display', 'none');
            self.$el.find('#fy-level-filter').click(function () {
                self.$el.find('.fiscal-year-filter-wrapper').css('display', '');
            });
            self.$el.find('#ageing_to_join_filter,#filter-fy-button1').click(function () {
                self.$el.find('.fiscal-year-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-grade-filter').click(function () {
                self.$el.find('.fy-grade-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_grade_filter,#filter-fy-button2').click(function () {
                self.$el.find('.fy-grade-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-dept-filter').click(function () {
                self.$el.find('.fy-department-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_department_filter,#filter-fy-button3').click(function () {
                self.$el.find('.fy-department-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-loca-filter').click(function () {
                self.$el.find('.fy-location-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_location_filter,#filter-fy-button4').click(function () {
                self.$el.find('.fy-location-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-edg_budget-filter').click(function () {
                self.$el.find('.fy-budget-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_edg_budget_filter,#filter-fy-button5').click(function () {
                self.$el.find('.fy-budget-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-resource-filter').click(function () {
                self.$el.find('.fy-resource-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_resource_filter,#filter-fy-button6').click(function () {
                self.$el.find('.fy-resource-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-hire-res-filter').click(function () {
                self.$el.find('.fy-hiring-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_hire_res_filter,#filter-fy-button7').click(function () {
                self.$el.find('.fy-hiring-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-skill-filter').click(function () {
                self.$el.find('.fy-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_skill_filter,#filter-fy-button8').click(function () {
                self.$el.find('.fy-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-company-filter').click(function () {
                self.$el.find('.fy-company-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_company_filter,#filter-fy-button9').click(function () {
                self.$el.find('.fy-company-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-desg-filter').click(function () {
                self.$el.find('.fy-desg-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_desg_filter,#filter-fy-button10').click(function () {
                self.$el.find('.fy-desg-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-recruiter-filter').click(function () {
                self.$el.find('.fy-recruiter-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_recruiter_filter,#filter-fy-button11').click(function () {
                self.$el.find('.fy-recruiter-filter-wrapper').css('display', 'none');
            });
            
           
            return true;
        },
       
        render_ageing_to_joined_ratio_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet1') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_level_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
                    var categories = [];
                    var seriesData = [];

                    for (var i = 0; i < fycollectdata.length; i++) {
                        categories.push(fycollectdata[i][0]);
                        seriesData.push({
                            name: fycollectdata[i][0],
                            y: fycollectdata[i][1]
                        });
                    }
                    self.ageing_to_join_ratio_count =  result[0];
                if (self.ageing_to_join_ratio_count && self.ageing_to_join_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_joined_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Level Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Level',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_count,
                            colorByPoint: true,
                            colors: ['#E6B9A6','#365E32','#81A263','#E7D37F','#FD9B63','#26355D','#AF47D2','#FF8F00','#FFDB00',
                                    '#4793AF','#FFC470','#DD5746','#8B322C',],
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
                                
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_grade_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet2') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_grade_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_ratio_grade_count =  result[0];
                if (self.ageing_to_join_ratio_grade_count && self.ageing_to_join_ratio_grade_count.length > 0){
                    Highcharts.chart('ageing_to_joined_grade_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Grade Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Grade',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_grade_count,
                            colorByPoint: true,
                            colors: [
                                '#FFDB00','#4793AF','#FFC470','#DD5746','#8B322C',
                                '#E6B9A6','#365E32','#81A263',
                                '#E7D37F','#FD9B63','#26355D','#AF47D2','#FF8F00',
                            ],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_grade_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_dept_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet3') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_dept_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
               
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_ratio_dept_count =  result[0];
                if (self.ageing_to_join_ratio_dept_count && self.ageing_to_join_ratio_dept_count.length > 0){
                    Highcharts.chart('ageing_to_joined_dept_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Department Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Department',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_dept_count,
                            colorByPoint: true,
                            colors: [
                                '#26355D','#AF47D2','#FF8F00','#FFDB00','#4793AF',
                                '#E6B9A6','#365E32','#81A263',
                                '#E7D37F','#FD9B63','#FFC470','#DD5746','#8B322C',
                            ],
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
                            
                        }],
                                
                    });
                }else {
                var container = document.getElementById('ageing_to_joined_dept_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_loc_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet4') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_loc_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
               
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_ratio_loc_count =  result[0];
                if (self.ageing_to_join_ratio_loc_count && self.ageing_to_join_ratio_loc_count.length > 0){
                    Highcharts.chart('ageing_to_joined_loc_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Location Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Location',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_loc_count,
                            colorByPoint: true,
                            colors: ['#8B322C','#FF8F00','#26355D','#AF47D2','#E7D37F','#FD9B63','#FFC470',
                                '#E6B9A6','#365E32','#81A263',
                                '#DD5746','#FFDB00','#4793AF',],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_loc_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_budget_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet5') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_budget_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
                
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_ratio_budget_count =  result[0];
                if (self.ageing_to_join_ratio_budget_count && self.ageing_to_join_ratio_budget_count.length > 0){
                    Highcharts.chart('ageing_to_joined_budget_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Budget Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Budget',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_budget_count,
                            colorByPoint: true,
                            colors: ['#FFDB00','#4793AF','#8B322C','#E7D37F','#FD9B63','#FFC470',
                                '#E6B9A6','#FF8F00','#26355D','#AF47D2','#365E32','#81A263',
                                '#DD5746',],
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
                        }]
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_budget_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_resource_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet6') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_resource_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
               
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_ratio_resource_count =  result[0];
                if (self.ageing_to_join_ratio_resource_count && self.ageing_to_join_ratio_resource_count.length > 0){
                    Highcharts.chart('ageing_to_joined_resources_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Type of Resource wise (Fresher / Lateral) Ageing(To Join)'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Resource Type',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_resource_count,
                            colorByPoint: true,
                            colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_resources_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_hire_res_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet7') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_hiring_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_ratio_hire_count =  result[0];
                if (self.ageing_to_join_ratio_hire_count && self.ageing_to_join_ratio_hire_count.length > 0){
                    Highcharts.chart('ageing_to_joined_hire_res_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Type of Hiring wise (New / Replacement) Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Hiring',
                            groupPadding: 0,
                            data: self.ageing_to_join_ratio_hire_count,
                            colorByPoint: true,
                            colors: ['#26355D','#AF47D2', '#376e3b','#3366E6', '#fc0328', '#8c03fc','#FF8F00','#4D8066', '#FF6633', '#00B3E6',],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_hire_res_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_skill_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet8') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_skill_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
               
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_skill_count =  result[0];
                if (self.ageing_to_join_skill_count && self.ageing_to_join_skill_count.length > 0){
                    Highcharts.chart('ageing_to_joined_skill_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Skill Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Skill',
                            groupPadding: 0,
                            data: self.ageing_to_join_skill_count,
                            colorByPoint: true,
                            colors: ['#8B322C','#3366E6', '#fc0328', '#8c03fc','#E7D37F','#FD9B63','#FFC470',
                                '#E6B9A6','#FF8F00','#26355D','#AF47D2','#365E32','#81A263',
                                '#DD5746','#FFDB00','#4793AF','#00B3E6',],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_skill_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                    
            });
        },
        render_ageing_to_joined_ratio_company_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet9') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_company_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
                
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_skill_count =  result[0];
                if (self.ageing_to_join_skill_count && self.ageing_to_join_skill_count.length > 0){
                    Highcharts.chart('ageing_to_joined_comapny_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Company Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Company',
                            groupPadding: 0,
                            data: self.ageing_to_join_skill_count,
                            colorByPoint: true,
                            colors: ['#E6B9A6','#FF8F00','#26355D','#AF47D2','#365E32','#81A263','#8B322C','#3366E6',
                                 '#fc0328', '#8c03fc','#E7D37F','#FD9B63','#FFC470',
                                '#DD5746','#FFDB00','#4793AF','#00B3E6',],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_joined_comapny_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_joined_ratio_desig_container_graph: async function (status) {
            var self = this;
            var params = {};
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id };
            if (status == 'refresh_edging_portlet10') params = {};
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_designation_ageing_to_join_ratio_count',
                kwargs: params,
            }).done(function(result) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
        
                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
                self.ageing_to_join_desg_count =  result[0];
                self.desg_name =  result[0][0];
        
                // console.log("R",self.desg_name,"========",fycollectdata )
                if (self.ageing_to_join_desg_count && self.ageing_to_join_desg_count.length > 0) {
                    Highcharts.chart('ageing_to_desg_joined_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text: 'Designation Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Designation',
                            groupPadding: 0,
                            data: self.ageing_to_join_desg_count,
                            colorByPoint: true,
                            colors: ['#81A263','#8B322C','#AF47D2','#365E32','#fc0328', '#8c03fc','#E7D37F','#FD9B63','#FFC470',
                                '#E6B9A6','#FF8F00','#26355D','#3366E6', 
                                '#DD5746','#FFDB00','#4793AF','#00B3E6','#4D8066',],
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
                            
                        }],
                    });
                } else {
                    var container = document.getElementById('ageing_to_desg_joined_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },
        
        render_ageing_to_joined_ratio_recruiter_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet11') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_recruiter_ageing_to_join_ratio_count',
                kwargs: params,
                }).done(function(result) {
                var fycollectdata = result;
                
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < fycollectdata.length; i++) {
                    categories.push(fycollectdata[i][0]);
                    seriesData.push({
                        name: fycollectdata[i][0],
                        y: fycollectdata[i][1]
                    });
                }
           
                self.ageing_to_join_recru_count =  result[0];
                if (self.ageing_to_join_recru_count && self.ageing_to_join_recru_count.length > 0){
                    Highcharts.chart('ageing_to_recruiter_joined_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Recruiter Wise Ageing( To Join )'
                        },
                        accessibility: {
                            announceNewData: {
                                enabled: true
                            }
                        },
                        xAxis: {
                            type: 'category'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: {
                            title: {
                                text: ''
                            }
                    
                        },
                        plotOptions: {
                            series: {
                                borderWidth: 0,
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.y:.1f}%'
                                }
                            },
                            column: {
                                pointWidth: 70 // Adjust the width of the columns as needed
                            }
                        },
                    
                        tooltip: {
                            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
                        },
                        series: [{
                            name: 'Recruiter',
                            groupPadding: 0,
                            data: self.ageing_to_join_recru_count,
                            colorByPoint: true,
                            colors: ['#FF6633', '#00B3E6','#3366E6', '#81A263','#8c03fc','#E7D37F','#FD9B63',
                                '#8B322C','#fc0328', '#376e3b', '#4D8066',],
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
                            
                        }],
                                
                    });
                }else {
                    var container = document.getElementById('ageing_to_recruiter_joined_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        
    });
    core.action_registry.add('kw_recruitment_hiring_dashboard_tag', RecruitmentDashboard);


});