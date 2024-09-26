odoo.define('kw_recruitment_to_offer_dashboard', function (require) {
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

    // var _t = core._t;
    // var _lt = core._lt;

    var RecruitmentDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        events: {
            
            'click #filter-offer-fy-button2': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-offer-fy-select2').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_grade_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_grade_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet2': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data2 = true;
                self.render_ageing_to_offer_ratio_grade_container_graph("refresh_edging_portlet2");
            }, 0, true),

            'click #filter-offer-fy-button3': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-offer-fy-select3').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_dept_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_dept_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet3': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data3 = true;
                self.render_ageing_to_offer_ratio_dept_container_graph("refresh_edging_portlet3");
            }, 0, true),
            'click #filter-offer-fy-button4': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-offer-fy-select4').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_loc_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_loc_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet4': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data4 = true;
                self.render_ageing_to_offer_ratio_loc_container_graph("refresh_edging_portlet4");
            }, 0, true),
            'click #filter-offer-fy-button5': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-offer-fy-select5').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_budget_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_budget_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet5': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data5 = true;
                self.render_ageing_to_offer_ratio_budget_container_graph("refresh_edging_portlet5");
            }, 0, true),

            'click #filter-offer-fy-button6': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-offer-fy-select6').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_resource_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_resource_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet6': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data6 = true;
                self.render_ageing_to_offer_ratio_resource_container_graph("refresh_edging_portlet6");
            }, 0, true),
            'click #filter-offer-fy-button7': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-offer-fy-select7').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_hire_res_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_hire_res_container_graph('');
            }, 0, true),
        
            'click .refresh_offerportlet7': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data7 = true;
                self.render_ageing_to_offer_ratio_hire_res_container_graph("refresh_edging_portlet7");
            }, 0, true),

            'click #filter-fy-offer-button8': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-offer-select8').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_skill_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_skill_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet8': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data8 = true;
                self.render_ageing_to_offer_ratio_skill_container_graph("refresh_edging_portlet8");
            }, 0, true),

            'click #filter-fy-offer-button9': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-offer-select9').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_company_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_company_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet9': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data9 = true;
                self.render_ageing_to_offer_ratio_company_container_graph("refresh_edging_portlet9");
            }, 0, true),

            'click #filter-fy-offer-button10': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-offer-select10').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_desig_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_desig_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet10': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data10 = true;
                self.render_ageing_to_offer_ratio_desig_container_graph("refresh_edging_portlet10");
            }, 0, true),
            'click #filter-fy-offer-button11': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-fy-offer-select11').val();
                if(self.financial_year_id != 0)
                    self.render_ageing_to_offer_ratio_recruiter_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_ageing_to_offer_ratio_recruiter_container_graph('');
            }, 0, true),
        
            'click .refresh_offer_portlet11': _.debounce(function () {
                var self = this;
                self.refresh_edging_portlet_data11 = true;
                self.render_ageing_to_offer_ratio_recruiter_container_graph("refresh_edging_portlet11");
            }, 0, true),

        },
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_hiring_offer_dashboard_tag') {
                self._rpc({
                    model: 'recruitment_data_dashboard',
                    method: 'get_filter_data',
                }, []).then(function (result) {
                    self.ageing_fy_filters = result['dashboard_fy_filters'][0];
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
            this.set("title", 'Aging To Offer Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('AgingOfferDashboard', {
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
            self.render_ageing_to_offer_ratio_grade_container_graph();
            self.render_ageing_to_offer_ratio_dept_container_graph();
            self.render_ageing_to_offer_ratio_loc_container_graph();
            self.render_ageing_to_offer_ratio_budget_container_graph();
            self.render_ageing_to_offer_ratio_resource_container_graph();
            self.render_ageing_to_offer_ratio_hire_res_container_graph();
            self.render_ageing_to_offer_ratio_skill_container_graph();
            self.render_ageing_to_offer_ratio_company_container_graph();
            self.render_ageing_to_offer_ratio_desig_container_graph();
            self.render_ageing_to_offer_ratio_recruiter_container_graph();
            
        },
        

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.fy-grade-offer-filter-wrapper,.fy-dept-filter-wrapper,.fy-loc-offer-filter-wrapper,.fy-budg-offer-filter-wrapper,.fy-res-offer-filter-wrapper,.fy-hir-offer-filter-wrapper,.fy-skill-offer-filter-wrapper,.fy-company-offer-filter-wrapper,.fy-desg-filter-offer-wrapper,.fy-recruiter-offer-filter-wrapper').css('display', 'none');
           
            self.$el.find('#fy-offer-grade-filter').click(function () {
                self.$el.find('.fy-grade-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_offer_grade_filter,#filter-offer-fy-button2').click(function () {
                self.$el.find('.fy-grade-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-offer-dept-filter').click(function () {
                self.$el.find('.fy-dept-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_offer_dept_filter,#filter-offer-fy-button3').click(function () {
                self.$el.find('.fy-dept-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-offer-loca-filter').click(function () {
                self.$el.find('.fy-loc-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_loc_offer_filter,#filter-offer-fy-button4').click(function () {
                self.$el.find('.fy-loc-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-offer_budget-filter').click(function () {
                self.$el.find('.fy-budg-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_offer_budget_filter,#filter-offer-fy-button5').click(function () {
                self.$el.find('.fy-budg-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-res-offer-filter').click(function () {
                self.$el.find('.fy-res-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_res_offer_filter,#filter-offer-fy-button6').click(function () {
                self.$el.find('.fy-res-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-hire-res-offer-filter').click(function () {
                self.$el.find('.fy-hir-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_hire_res_offer_filter,#filter-offer-fy-button7').click(function () {
                self.$el.find('.fy-hir-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-skill-offer-filter').click(function () {
                self.$el.find('.fy-skill-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_offer_skill_filter,#filter-fy-offer-button8').click(function () {
                self.$el.find('.fy-skill-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-company-offer-filter').click(function () {
                self.$el.find('.fy-company-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_company_offer_filter,#filter-fy-offer-button9').click(function () {
                self.$el.find('.fy-company-offer-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-desg-offer-filter').click(function () {
                self.$el.find('.fy-desg-filter-offer-wrapper').css('display', '');
            });
            self.$el.find('#fy_desg_offer_filter,#filter-fy-offer-button10').click(function () {
                self.$el.find('.fy-desg-filter-offer-wrapper').css('display', 'none');
            });
            self.$el.find('#fy-recruiter-offer-filter').click(function () {
                self.$el.find('.fy-recruiter-offer-filter-wrapper').css('display', '');
            });
            self.$el.find('#fy_recruiter_offer_filter,#filter-fy-offer-button11').click(function () {
                self.$el.find('.fy-recruiter-offer-filter-wrapper').css('display', 'none');
            });
            
           
            return true;
        },
       
        render_ageing_to_offer_ratio_grade_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet2') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_grade_ratio_count',
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
                    self.get_aging_offer_grade_ratio_count =  result[0];
                if (self.get_aging_offer_grade_ratio_count && self.get_aging_offer_grade_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_grade_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Grade Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_grade_ratio_count,
                            colorByPoint: true,
                            colors: ['#E7D37F','#FD9B63','#FFC470','#AF47D2','#365E32','#81A263','#8B322C','#3366E6', '#fc0328', 
                                '#E6B9A6','#FF8F00','#26355D','#8c03fc','#DD5746','#FFDB00','#4793AF','#00B3E6',],
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
                    var container = document.getElementById('ageing_to_offer_grade_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_offer_ratio_dept_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet3') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_dept_ratio_count',
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
                self.get_aging_offer_dept_ratio_count =  result[0];
                if (self.get_aging_offer_dept_ratio_count && self.get_aging_offer_dept_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_dept_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Department Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_dept_ratio_count,
                            colorByPoint: true,
                            colors: ['#4793AF','#00B3E6','#AF47D2','#365E32','#81A263','#8B322C','#3366E6', '#fc0328', 
                                '#E6B9A6','#FF8F00','#26355D','#8c03fc','#E7D37F','#FD9B63','#FFC470',
                                '#DD5746','#FFDB00',],
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
                var container = document.getElementById('ageing_to_offer_dept_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_offer_ratio_loc_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet4') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_loc_ratio_count',
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
                self.get_aging_offer_loc_ratio_count =  result[0];
                if (self.get_aging_offer_loc_ratio_count && self.get_aging_offer_loc_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_loc_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Location Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_loc_ratio_count,
                            colorByPoint: true,
                            colors: ['#26355D','#8c03fc','#E7D37F','#fc0328', '#8c03fc', '#376e3b', '#4D8066','#AF47D2','#365E32','#81A263','#8B322C','#3366E6', '#fc0328', 
                                '#E6B9A6','#FF8F00','#FD9B63','#FFC470',
                                '#DD5746','#FFDB00','#4793AF','#00B3E6', ],
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
                    var container = document.getElementById('ageing_to_offer_loc_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_offer_ratio_budget_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet5') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_budget_ratio_count',
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
                self.get_aging_offer_budget_ratio_count =  result[0];
                if (self.get_aging_offer_budget_ratio_count && self.get_aging_offer_budget_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_budget_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Budget Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_budget_ratio_count,
                            colorByPoint: true,
                            colors: ['#26355D','#8c03fc','#E7D37F','#fc0328', '#8c03fc', '#376e3b', '#4D8066','#4D8066', '#FF6633',
                                 '#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#00B3E6'],
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
                    var container = document.getElementById('ageing_to_offer_budget_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_offer_ratio_resource_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet6') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_resource_ratio_count',
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
                self.get_aging_offer_resource_ratio_count =  result[0];
                if (self.get_aging_offer_resource_ratio_count && self.get_aging_offer_resource_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_resources_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Type of Resource wise (Fresher / Lateral) Ageing(To Offer)'
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
                            data: self.get_aging_offer_resource_ratio_count,
                            colorByPoint: true,
                            colors: ['#fc0328', '#8c03fc', '#376e3b', '#4D8066','#AF47D2','#365E32','#81A263','#8B322C','#3366E6', '#fc0328', 
                                '#E6B9A6','#FF8F00','#26355D','#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
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
                    var container = document.getElementById('ageing_to_offer_resources_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_offer_ratio_hire_res_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet7') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_hire_ratio_count',
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
                self.get_aging_offer_hire_ratio_count =  result[0];
                if (self.get_aging_offer_hire_ratio_count && self.get_aging_offer_hire_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_hire_res_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Type of Hiring wise (New / Replacement) Ageing(To Offer)'
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
                            data: self.get_aging_offer_hire_ratio_count,
                            colorByPoint: true,
                            colors: ['#376e3b', '#4D8066','#AF47D2','#365E32','#81A263','#8B322C','#3366E6', '#fc0328', 
                                '#E6B9A6','#FF8F00','#26355D','#8c03fc','#E7D37F','#FD9B63','#FFC470',
                                '#DD5746','#FFDB00','#4793AF','#00B3E6','#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
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
                    var container = document.getElementById('ageing_to_offer_hire_res_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        render_ageing_to_offer_ratio_skill_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet8') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_skill_ratio_count',
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
                self.get_aging_offer_skill_ratio_count =  result[0];
                if (self.get_aging_offer_skill_ratio_count && self.get_aging_offer_skill_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_offer_skill_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Skill Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_skill_ratio_count,
                            colorByPoint: true,
                            colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#fc0328','#AF47D2','#365E32','#81A263', 
                                '#E6B9A6','#FF8F00','#26355D','#8B322C','#3366E6', '#fc0328',
                                '#DD5746','#FFDB00','#4793AF','#00B3E6','#4D8066', '#FF6633', '#00B3E6',],
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
                    var container = document.getElementById('ageing_to_offer_skill_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                    
            });
        },
        render_ageing_to_offer_ratio_company_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet9') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_company_ratio_count',
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
                self.get_aging_offer_company_ratio_count =  result[0];
                if (self.get_aging_offer_company_ratio_count && self.get_aging_offer_company_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_joined_comapny_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Company Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_company_ratio_count,
                            colorByPoint: true,
                            colors: ['#3366E6', '#fc0328', '#8B322C','#3366E6', '#fc0328','#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
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
        render_ageing_to_offer_ratio_desig_container_graph: async function (status) {
            var self = this;
            var params = {};
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id };
            if (status == 'refresh_edging_portlet10') params = {};
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_desgination_ratio_count',
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
                self.get_aging_offer_desgination_ratio_count =  result[0];
                self.desg_name =  result[0][0];
        
                // console.log("R",self.desg_name,"========",fycollectdata )
                if (self.get_aging_offer_desgination_ratio_count && self.get_aging_offer_desgination_ratio_count.length > 0) {
                    Highcharts.chart('ageing_to_desg_offer_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Designation Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_desgination_ratio_count,
                            colorByPoint: true,
                            colors: ['#00B3E6', '#8c03fc','#3366E6', '#fc0328','#4D8066','#AF47D2','#365E32','#81A263','#8B322C','#FF6633', '#376e3b', '#4D8066',],
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
                    var container = document.getElementById('ageing_to_desg_offer_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },
        
        render_ageing_to_offer_ratio_recruiter_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh_edging_portlet11') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_aging_offer_recruiter_ratio_count',
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
           
                self.get_aging_offer_recruiter_ratio_count =  result[0];
                if (self.get_aging_offer_recruiter_ratio_count && self.get_aging_offer_recruiter_ratio_count.length > 0){
                    Highcharts.chart('ageing_to_recruiter_offer_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            align: 'center',
                            text:'Recruiter Wise Ageing(To Offer)'
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
                            data: self.get_aging_offer_recruiter_ratio_count,
                            colorByPoint: true,
                            colors: ['#FF6633', '#00B3E6','#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066','#4D8066','#AF47D2','#365E32','#81A263','#8B322C',],
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
                    var container = document.getElementById('ageing_to_recruiter_offer_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
                
            });
        },
        
    });
    core.action_registry.add('kw_recruitment_hiring_offer_dashboard_tag', RecruitmentDashboard);


});