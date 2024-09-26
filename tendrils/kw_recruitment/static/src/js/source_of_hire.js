odoo.define('kw_recruitment.kw_recruitment_source_dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;

    var RecruitmentSourceDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_source_of_hire_dashboard_tag') {
                self._rpc({
                    model: 'recruitment_data_dashboard',
                    method: 'get_filter_data',
                }, []).then(function (result) {
                    self.source_fy_filters = result['dashboard_fy_filters'][0];
                }).done(function () {
                    self.render();
                    self.href = window.location.href;
                });
            }
        },
        events: {
            'click #filter-source-fy-button1': _.debounce(function (ev) {
                var self = this;
                self.financial_year_id = $('#filter-source-fy-select1').val();
                if(self.financial_year_id != 0)
                    self.render_source_of_hire_level_container_graph('filter_fy');
                if(self.financial_year_id == 0)
                    self.render_source_of_hire_level_container_graph('');
            }, 0, true),
        
            'click .refresh_source_portlet1': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data1 = true;
                self.render_source_of_hire_level_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hire-grade': _.debounce(function (ev) {
                var self = this;
                self.financial_year_grade_id = $('#filter-source-fy-select2').val();
                if(self.financial_year_grade_id != 0)
                    self.render_source_hire_grade_container_graph('filter_fy');
                if(self.financial_year_grade_id == 0)
                    self.render_source_hire_grade_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_grade_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data2 = true;
                self.render_source_hire_grade_container_graph("refresh");
            }, 0, true),
            
            'click #filter-source-hire-depart': _.debounce(function (ev) {
                var self = this;
                self.financial_year_depart_id = $('#filter-source-fy-select3').val();
                if(self.financial_year_depart_id != 0)
                    self.render_source_hire_depart_container_graph('filter_fy');
                if(self.financial_year_depart_id == 0)
                    self.render_source_hire_depart_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_depart_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data3 = true;
                self.render_source_hire_depart_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hire-location': _.debounce(function (ev) {
                var self = this;
                self.financial_year_location_id = $('#filter-source-fy-select4').val();
                if(self.financial_year_location_id != 0)
                    self.render_source_hire_location_container_graph('filter_fy');
                if(self.financial_year_location_id == 0)
                    self.render_source_hire_location_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_location_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data4 = true;
                self.render_source_hire_location_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hire-budget': _.debounce(function (ev) {
                var self = this;
                self.financial_year_budget_id = $('#filter-source-fy-select5').val();
                if(self.financial_year_budget_id != 0)
                    self.render_source_hire_budget_container_graph('filter_fy');
                if(self.financial_year_budget_id == 0)
                    self.render_source_hire_budget_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_budget_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data5 = true;
                self.render_source_hire_budget_container_graph("refresh");
            }, 0, true),
            
            'click #filter-source-hire-resource': _.debounce(function (ev) {
                var self = this;
                self.financial_year_resource_id = $('#filter-source-fy-select6').val();
                if(self.financial_year_resource_id != 0)
                    self.render_source_hire_resource_container_graph('filter_fy');
                if(self.financial_year_resource_id == 0)
                    self.render_source_hire_resource_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_resource_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data6 = true;
                self.render_source_hire_resource_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hiring-res-resource': _.debounce(function (ev) {
                var self = this;
                self.financial_year_hiring_res_id = $('#filter-source-fy-select7').val();
                if(self.financial_year_hiring_res_id != 0)
                    self.render_source_hire_hiring_res_container_graph('filter_fy');
                if(self.financial_year_hiring_res_id == 0)
                    self.render_source_hire_hiring_res_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hiring_res_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data7 = true;
                self.render_source_hire_hiring_res_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hire-skill-resource': _.debounce(function (ev) {
                var self = this;
                self.financial_year_hire_skill_id = $('#filter-source-fy-select8').val();
                if(self.financial_year_hire_skill_id != 0)
                    self.render_source_hire_skill_container_graph('filter_fy');
                if(self.financial_year_hire_skill_id == 0)
                    self.render_source_hire_skill_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data8 = true;
                self.render_source_hire_skill_container_graph("refresh");
            }, 0, true),
            
            'click #filter-source-hire-company-rate': _.debounce(function (ev) {
                var self = this;
                self.financial_year_hire_company_id = $('#filter-source-fy-select9').val();
                if(self.financial_year_hire_company_id != 0)
                    self.render_source_hire_company_container_graph('filter_fy');
                if(self.financial_year_hire_company_id == 0)
                    self.render_source_hire_company_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_company_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data9 = true;
                self.render_source_hire_company_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hire-designation-rate': _.debounce(function (ev) {
                var self = this;
                self.financial_year_hire_designation_id = $('#filter-source-fy-select10').val();
                if(self.financial_year_hire_designation_id != 0)
                    self.render_source_hire_designation_container_graph('filter_fy');
                if(self.financial_year_hire_designation_id == 0)
                    self.render_source_hire_designation_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_designation_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data10 = true;
                self.render_source_hire_designation_container_graph("refresh");
            }, 0, true),

            'click #filter-source-hire-recruiter-rate': _.debounce(function (ev) {
                var self = this;
                self.financial_year_hire_recruiter_id = $('#filter-source-fy-select11').val();
                if(self.financial_year_hire_recruiter_id != 0)
                    self.render_source_hire_recruiter_container_graph('filter_fy');
                if(self.financial_year_hire_recruiter_id == 0)
                    self.render_source_hire_recruiter_container_graph('');
            }, 0, true),
        
            'click .refresh_source_hire_recruiter_portlet': _.debounce(function () {
                var self = this;
                self.refresh_source_portlet_data11 = true;
                self.render_source_hire_recruiter_container_graph("refresh");
            }, 0, true),

        },
        
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Source of hire rate Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('SourceRateDashboard', {
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
            self.render_source_of_hire_level_container_graph();
            self.render_source_hire_grade_container_graph();
            self.render_source_hire_depart_container_graph();
            self.render_source_hire_location_container_graph();
            self.render_source_hire_budget_container_graph();
            self.render_source_hire_resource_container_graph();
            self.render_source_hire_hiring_res_container_graph();
            self.render_source_hire_skill_container_graph();
            self.render_source_hire_company_container_graph();
            self.render_source_hire_designation_container_graph();
            self.render_source_hire_recruiter_container_graph();
        },
        

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.fy-source-lv-filter-wrapper,.fy-source-hire-grade-rate-wrapper,.fy-source-hire-depart-rate-wrapper,.fy-source-hire-location-rate-wrapper,.fy-source-hire-budget-rate-wrapper,.fy-source-hire-resource-rate-wrapper,.fy-source-hiring-res-rate-wrapper,.fy-source-hire-skill-rate-wrapper,.fy-source-hire-company-rate-wrapper,.fy-source-hire-designation-wrapper,.fy-source-hire-recruiter-wrapper').css('display', 'none');
            self.$el.find('#fy-source-level-filter').click(function () {
            self.$el.find('.fy-source-lv-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_lv_filter,#filter-source-fy-button1').click(function () {
                self.$el.find('.fy-source-lv-filter-wrapper').css('display', 'none');
            });   
            
            self.$el.find('#fy-source-grade-filter').click(function () {
            self.$el.find('.fy-source-hire-grade-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_grade_filter,#filter-source-hire-grade').click(function () {
                self.$el.find('.fy-source-hire-grade-rate-wrapper').css('display', 'none');
            });      
            
            self.$el.find('#fy-source-depart-filter').click(function () {
            self.$el.find('.fy-source-hire-depart-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_depart_filter,#filter-source-hire-depart').click(function () {
                self.$el.find('.fy-source-hire-depart-rate-wrapper').css('display', 'none');
            });   
            
            self.$el.find('#fy-source-location-filter').click(function () {
            self.$el.find('.fy-source-hire-location-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_location_filter,#filter-source-hire-location').click(function () {
                self.$el.find('.fy-source-hire-location-rate-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-source-budget-filter').click(function () {
            self.$el.find('.fy-source-hire-budget-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_location_filter,#filter-source-hire-budget').click(function () {
                self.$el.find('.fy-source-hire-budget-rate-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-source-resource-filter').click(function () {
            self.$el.find('.fy-source-hire-resource-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_resource_filter,#filter-source-hire-resource').click(function () {
                self.$el.find('.fy-source-hire-resource-rate-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-source-hiring-res-filter').click(function () {
            self.$el.find('.fy-source-hiring-res-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hiring_res_filter,#filter-source-hiring-res-resource').click(function () {
                self.$el.find('.fy-source-hiring-res-rate-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-source-hire-skill-filter').click(function () {
            self.$el.find('.fy-source-hire-skill-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_skill_rate_filter,#filter-source-hire-skill-resource').click(function () {
                self.$el.find('.fy-source-hire-skill-rate-wrapper').css('display', 'none');
            }); 

            self.$el.find('#fy-source-hire-company-filter').click(function () {
            self.$el.find('.fy-source-hire-company-rate-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_company_rate_filter,#filter-source-hire-company-rate').click(function () {
                self.$el.find('.fy-source-hire-company-rate-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-source-hire-designation-filter').click(function () {
            self.$el.find('.fy-source-hire-designation-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_designation_rate_filter,#filter-source-hire-designation-rate').click(function () {
                self.$el.find('.fy-source-hire-designation-wrapper').css('display', 'none');
            });   
            
            self.$el.find('#fy-source-hire-recruiter-filter').click(function () {
            self.$el.find('.fy-source-hire-recruiter-wrapper').css('display', '');
            });
            self.$el.find('#close_source_hire_recruiter_rate_filter,#filter-source-hire-recruiter-rate').click(function () {
                self.$el.find('.fy-source-hire-recruiter-wrapper').css('display', 'none');
            });   
                
            return true;
        },
       
        render_source_of_hire_level_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_level_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (level)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_level_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Level Distribution',
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
                               
                            }
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_level_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },
        render_source_hire_grade_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_grade_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_grade_rate',
                kwargs: params,
            }).done(function(result) {
            if(result && result.length >0) {
            var fycollectdata = result;
            var categories = [];
            var seriesData = [];

            for (var i = 0; i < result.length; i++) {
                var data = result[i];
                var category = data.category; // Category (grade)
                var source = data.name; // source
                var sourcecount = data.data; //  count
    
                if (!seriesData[source]) {
                    seriesData[source] = {};
                }
                seriesData[source][category] = sourcecount;
    
                if (!categories.includes(category)) {
                    categories.push(category);
                }
            }
            var series = [];
            console.log()
            for (var source in seriesData) {
                var sourceData = [];
                for (var i = 0; i < categories.length; i++) {
                    var category = categories[i];
                    var count = seriesData[source][category] || 0;
                    sourceData.push(count);
                }
                series.push({
                    name: source,
                    data: sourceData
                });
            }
                Highcharts.chart('source_hire_grade_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Source Wise Grade Distribution',
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
                           
                        }
                    },
                    series: series,
                    colors: [
                     '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                    '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                    '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                ],
                });
            } else {
                var container = document.getElementById('source_hire_grade_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        });
        },

        render_source_hire_depart_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_depart_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_depart_rate',
                kwargs: params,
                }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (dept)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_depart_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Department Distribution',
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
                               
                            }
                        },
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom',
                            itemWidth: 70,
                            itemStyle: {
                                width: '40px'
                            },
                            labelFormatter: function () {
                                return this.name;
                            },
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_depart_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_location_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_location_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_location_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (location)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_location_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Location Distribution',
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
                               
                            }
                        },
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom',
                            itemWidth: 70,
                            itemStyle: {
                                width: '40px'
                            },
                            labelFormatter: function () {
                                return this.name;
                            },
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_location_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_budget_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_budget_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_budget_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (budget)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_budget_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Budget type Distribution',
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
                               
                            }
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_budget_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_resource_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_resource_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_resource_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (budget)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_resource_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Hire Resource type Distribution',
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
                               
                            }
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_resource_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_hiring_res_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_hiring_res_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_hiring_res_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (budget)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hiring_res_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Resource type Distribution',
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
                               
                            }
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hiring_res_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_skill_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_hire_skill_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_skill_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (skill)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_skill_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise skill type Distribution',
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
                               
                            }
                        },
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom',
                            itemWidth: 70,
                            itemStyle: {
                                width: '40px'
                            },
                            labelFormatter: function () {
                                return this.name;
                            },
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_skill_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_company_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_hire_company_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_company_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (company)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_company_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Company  Distribution',
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
                               
                            }
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_company_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_designation_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_hire_designation_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_designation_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (desig)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                Highcharts.chart('source_hire_designation_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Source Wise Designation ',
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
                        }
                    },
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom',
                        itemWidth: 70,
                        itemStyle: {
                            width: '40px'
                        },
                        labelFormatter: function () {
                            return this.name;
                        },
                    },
                    series: series,
                    colors: [
                        '#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066',
                        '#FF6633', '#00B3E6', '#991AFF', '#1AB399', '#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF', '#E6B333',
                    ],
                });
                
                } else {
                    var container = document.getElementById('source_hire_designation_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },

        render_source_hire_recruiter_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.financial_year_hire_recruiter_id }
            if (status == 'refresh') params = {}
            var defloc = this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_source_hire_success_recruiter_rate',
                kwargs: params,
            }).done(function(result) {
                if(result && result.length >0) {
                var fycollectdata = result;
                var categories = [];
                var seriesData = [];
    
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (recruiter)
                    var source = data.name; // source
                    var sourcecount = data.data; //  count
        
                    if (!seriesData[source]) {
                        seriesData[source] = {};
                    }
                    seriesData[source][category] = sourcecount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                console.log()
                for (var source in seriesData) {
                    var sourceData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[source][category] || 0;
                        sourceData.push(count);
                    }
                    series.push({
                        name: source,
                        data: sourceData
                    });
                }
                    Highcharts.chart('source_hire_recruiter_container', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Source Wise Recruiter  Distribution',
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
                               
                            }
                        },
                        series: series,
                        colors: [
                         '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
                    ],
                    });
                } else {
                    var container = document.getElementById('source_hire_recruiter_container');
                    container.innerHTML = 'No Data Available';
                    container.style.textAlign = 'center';
                }
            });
        },




        // render_ageing_to_offer_ratio_grade_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet2') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_grade_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
        //             var categories = [];
        //             var seriesData = [];

        //             for (var i = 0; i < fycollectdata.length; i++) {
        //                 categories.push(fycollectdata[i][0]);
        //                 seriesData.push({
        //                     name: fycollectdata[i][0],
        //                     y: fycollectdata[i][1]
        //                 });
        //             }
        //             self.get_aging_offer_grade_ratio_count =  result[0];
        //         if (self.get_aging_offer_grade_ratio_count && self.get_aging_offer_grade_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_grade_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Grade Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Level',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_grade_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                                
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_offer_grade_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_dept_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet3') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_dept_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
               
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_dept_ratio_count =  result[0];
        //         if (self.get_aging_offer_dept_ratio_count && self.get_aging_offer_dept_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_dept_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Department Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Department',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_dept_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //         var container = document.getElementById('ageing_to_offer_dept_container');
        //         container.innerHTML = 'No Data Available';
        //         container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_loc_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet4') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_loc_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
               
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_loc_ratio_count =  result[0];
        //         if (self.get_aging_offer_loc_ratio_count && self.get_aging_offer_loc_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_loc_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Location Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Location',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_loc_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#FF6633', '#00B3E6','#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_offer_loc_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_budget_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet5') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_budget_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
                
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_budget_ratio_count =  result[0];
        //         if (self.get_aging_offer_budget_ratio_count && self.get_aging_offer_budget_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_budget_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Budget Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Budget',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_budget_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#4D8066', '#FF6633', '#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#00B3E6'],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
        //                 }]
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_offer_budget_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_resource_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet6') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_resource_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
               
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_resource_ratio_count =  result[0];
        //         if (self.get_aging_offer_resource_ratio_count && self.get_aging_offer_resource_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_resources_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Type of Resource wise (Fresher / Lateral) Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Resource Type',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_resource_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_offer_resources_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_hire_res_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet7') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_hire_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_hire_ratio_count =  result[0];
        //         if (self.get_aging_offer_hire_ratio_count && self.get_aging_offer_hire_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_hire_res_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Type of Hiring wise (New / Replacement) Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Hiring',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_hire_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_offer_hire_res_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_skill_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet8') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_skill_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
               
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_skill_ratio_count =  result[0];
        //         if (self.get_aging_offer_skill_ratio_count && self.get_aging_offer_skill_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_offer_skill_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Skill Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Skill',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_skill_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_offer_skill_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                    
        //     });
        // },
        // render_ageing_to_offer_ratio_company_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet9') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_company_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
                
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_company_ratio_count =  result[0];
        //         if (self.get_aging_offer_company_ratio_count && self.get_aging_offer_company_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_joined_comapny_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Comapny Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Skill',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_company_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066', '#FF6633', '#00B3E6',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_joined_comapny_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        // render_ageing_to_offer_ratio_desig_container_graph: async function (status) {
        //     var self = this;
        //     var params = {};
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id };
        //     if (status == 'refresh_edging_portlet10') params = {};
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_desgination_ratio_count',
        //         kwargs: params,
        //     }).done(function(result) {
        //         var fycollectdata = result;
        //         var categories = [];
        //         var seriesData = [];
        
        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
        //         self.get_aging_offer_desgination_ratio_count =  result[0];
        //         self.desg_name =  result[0][0];
        
        //         // console.log("R",self.desg_name,"========",fycollectdata )
        //         if (self.get_aging_offer_desgination_ratio_count && self.get_aging_offer_desgination_ratio_count.length > 0) {
        //             Highcharts.chart('ageing_to_desg_offer_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Designation Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Designation',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_desgination_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#00B3E6', '#8c03fc','#3366E6', '#fc0328','#FF6633', '#376e3b', '#4D8066',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
        //             });
        //         } else {
        //             var container = document.getElementById('ageing_to_desg_offer_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
        //     });
        // },
        
        // render_ageing_to_offer_ratio_recruiter_container_graph: async function (status) {
        //     var self = this;
        //     var params = {}
        //     if (status == 'filter_fy') params = { 'fy_id': self.financial_year_id }
        //     if (status == 'refresh_edging_portlet11') params = {}
        //     var defloc = this._rpc({
        //         model: 'recruitment_data_dashboard',
        //         method: 'get_aging_offer_recruiter_ratio_count',
        //         kwargs: params,
        //         }).done(function(result) {
        //         var fycollectdata = result;
                
        //         var categories = [];
        //         var seriesData = [];

        //         for (var i = 0; i < fycollectdata.length; i++) {
        //             categories.push(fycollectdata[i][0]);
        //             seriesData.push({
        //                 name: fycollectdata[i][0],
        //                 y: fycollectdata[i][1]
        //             });
        //         }
           
        //         self.get_aging_offer_recruiter_ratio_count =  result[0];
        //         if (self.get_aging_offer_recruiter_ratio_count && self.get_aging_offer_recruiter_ratio_count.length > 0){
        //             Highcharts.chart('ageing_to_recruiter_offer_container', {
        //                 chart: {
        //                     type: 'column'
        //                 },
        //                 title: {
        //                     align: 'center',
        //                     text:'Recruiter Wise Ageing(To Offer)'
        //                 },
        //                 accessibility: {
        //                     announceNewData: {
        //                         enabled: true
        //                     }
        //                 },
        //                 xAxis: {
        //                     type: 'category'
        //                 },
        //                 credits: {
        //                     enabled: false
        //                 },
        //                 yAxis: {
        //                     title: {
        //                         text: ''
        //                     }
                    
        //                 },
        //                 plotOptions: {
        //                     series: {
        //                         borderWidth: 0,
        //                         dataLabels: {
        //                             enabled: true,
        //                             format: '{point.y:.1f}%'
        //                         }
        //                     },
        //                     column: {
        //                         pointWidth: 70 // Adjust the width of the columns as needed
        //                     }
        //                 },
                    
        //                 tooltip: {
        //                     headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        //                     pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of Total<br/>'
        //                 },
        //                 series: [{
        //                     name: 'Recruiter',
        //                     groupPadding: 0,
        //                     data: self.get_aging_offer_recruiter_ratio_count,
        //                     colorByPoint: true,
        //                     colors: ['#FF6633', '#00B3E6','#3366E6', '#fc0328', '#8c03fc', '#376e3b', '#4D8066',],
        //                     dataLabels: {
        //                         enabled: true,
        //                         color: '#FFFFFF',
        //                         align: 'center',
        //                         format: '{point.y}', // one int
        //                         y: 10, // 10 pixels down from the top
        //                         style: {
                
        //                             fontSize: '13px',
        //                             fontFamily: 'Verdana, sans-serif'
        //                         }
        //                     },
                            
        //                 }],
                                
        //             });
        //         }else {
        //             var container = document.getElementById('ageing_to_recruiter_offer_container');
        //             container.innerHTML = 'No Data Available';
        //             container.style.textAlign = 'center';
        //         }
                
        //     });
        // },
        
    });
    core.action_registry.add('kw_recruitment_source_of_hire_dashboard_tag', RecruitmentSourceDashboard);


});