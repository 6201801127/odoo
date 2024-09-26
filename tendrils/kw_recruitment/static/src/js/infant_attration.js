odoo.define('kw_recruitment.kw_recruitment_infant_attration_dashboard', function (require) {
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

    var RecruitmentinfantattrationDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_infant_attration_dashboard_tag') {
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
            'click #filter-infant-attration-level-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_level_id = $('#filter-infant-attration-level').val();
                if(self.infant_attration_level_id != 0)
                    self.render_infant_attration_level_container_graph('filter_fy');
                if(self.infant_attration_level_id == 0)
                    self.render_infant_attration_level_container_graph('');
            }, 0, true),
        
            'click .infant_attration_level_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet1 = true;
                self.render_infant_attration_level_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-grade-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_grade_id = $('#filter-infant-attration-grade').val();
                if(self.infant_attration_grade_id != 0)
                    self.render_infant_attration_grade_container_graph('filter_fy');
                if(self.infant_attration_grade_id == 0)
                    self.render_infant_attration_grade_container_graph('');
            }, 0, true),
        
            'click .infant_attration_grade_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet2 = true;
                self.render_infant_attration_grade_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-dept-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_dept_id = $('#filter-infant-attration-dept').val();
                if(self.infant_attration_dept_id != 0)
                    self.render_infant_attration_dept_container_graph('filter_fy');
                if(self.infant_attration_dept_id == 0)
                    self.render_infant_attration_dept_container_graph('');
            }, 0, true),
        
            'click .infant_attration_dept_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet3 = true;
                self.render_infant_attration_dept_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-location-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_location_id = $('#filter-infant-attration-location').val();
                if(self.infant_attration_location_id != 0)
                    self.render_infant_attration_location_container_graph('filter_fy');
                if(self.infant_attration_location_id == 0)
                    self.render_infant_attration_location_container_graph('');
            }, 0, true),
        
            'click .infant_attration_location_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet4 = true;
                self.render_infant_attration_location_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-budget-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_budget_id = $('#filter-infant-attration-budget').val();
                if(self.infant_attration_budget_id != 0)
                    self.render_infant_attration_budget_container_graph('filter_fy');
                if(self.infant_attration_budget_id == 0)
                    self.render_infant_attration_budget_container_graph('');
            }, 0, true),
        
            'click .infant_attration_budget_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet5 = true;
                self.render_infant_attration_budget_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-resource-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_resource_id = $('#filter-infant-attration-resource').val();
                if(self.infant_attration_resource_id != 0)
                    self.render_infant_attration_resource_container_graph('filter_fy');
                if(self.infant_attration_resource_id == 0)
                    self.render_infant_attration_resource_container_graph('');
            }, 0, true),
        
            'click .infant_attration_resource_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet6 = true;
                self.render_infant_attration_resource_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-hiring-type-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_hiring_type_id = $('#filter-infant-attration-hiring-type').val();
                if(self.infant_attration_hiring_type_id != 0)
                    self.render_infant_attration_hiring_type_container_graph('filter_fy');
                if(self.infant_attration_hiring_type_id == 0)
                    self.render_infant_attration_hiring_type_container_graph('');
            }, 0, true),
        
            'click .infant_attration_hiring_type_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet7 = true;
                self.render_infant_attration_hiring_type_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-skill-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_skill_id = $('#filter-infant-attration-skill').val();
                if(self.infant_attration_skill_id != 0)
                    self.render_infant_attration_skill_container_graph('filter_fy');
                if(self.infant_attration_skill_id == 0)
                    self.render_infant_attration_skill_container_graph('');
            }, 0, true),
        
            'click .infant_attration_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet8 = true;
                self.render_infant_attration_skill_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-company-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_company_id = $('#filter-infant-attration-company').val();
                if(self.infant_attration_company_id != 0)
                    self.render_infant_attration_company_container_graph('filter_fy');
                if(self.infant_attration_company_id == 0)
                    self.render_infant_attration_company_container_graph('');
            }, 0, true),
        
            'click .infant_attration_company_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet9 = true;
                self.render_infant_attration_company_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-designation-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_designation_id = $('#filter-infant-attration-designation').val();
                if(self.infant_attration_designation_id != 0)
                    self.render_infant_attration_designation_container_graph('filter_fy');
                if(self.infant_attration_designation_id == 0)
                    self.render_infant_attration_designation_container_graph('');
            }, 0, true),
        
            'click .infant_attration_designation_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet10 = true;
                self.render_infant_attration_designation_container_graph("refresh");
            }, 0, true),

            'click #filter-infant-attration-recruiter-button': _.debounce(function (ev) {
                var self = this;
                self.infant_attration_recruiter_id = $('#filter-infant-attration-recruiter').val();
                if(self.infant_attration_recruiter_id != 0)
                    self.render_infant_attration_recruiter_container_graph('filter_fy');
                if(self.infant_attration_recruiter_id == 0)
                    self.render_infant_attration_recruiter_container_graph('');
            }, 0, true),
        
            'click .infant_attration_recruiter_portlet': _.debounce(function () {
                var self = this;
                self.refresh_infant_attration_portlet11 = true;
                self.render_infant_attration_recruiter_container_graph("refresh");
            }, 0, true),


        },
        
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Infant Attrition Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('infantattrationDashboard', {
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
            self.render_infant_attration_level_container_graph();
            self.render_infant_attration_grade_container_graph();
            self.render_infant_attration_dept_container_graph();
            self.render_infant_attration_location_container_graph();
            self.render_infant_attration_budget_container_graph();
            self.render_infant_attration_resource_container_graph();
            self.render_infant_attration_hiring_type_container_graph();
            self.render_infant_attration_skill_container_graph();
            self.render_infant_attration_company_container_graph();
            self.render_infant_attration_designation_container_graph();
            self.render_infant_attration_recruiter_container_graph();
        },

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.infant-attraion-level-wrapper,.infant-attraion-grade-wrapper,.infant-attraion-dept-wrapper,.infant-attraion-location-wrapper,.infant-attraion-budget-wrapper,.infant-attraion-resource-wrapper,.infant-attraion-hiring-type-wrapper,.infant-attraion-skill-wrapper,.infant-company-wrapper,.infant-attration-designation-wrapper,.infant-attration-recruiter-wrapper').css('display', 'none');
            self.$el.find('#fy-infant-attration-level-filter').click(function () {
            self.$el.find('.infant-attraion-level-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_level_ratio_filter,#filter-infant-attration-level-button').click(function () {
                self.$el.find('.infant-attraion-level-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-infant-attration-grade-filter').click(function () {
            self.$el.find('.infant-attraion-grade-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_grade_ratio_filter,#filter-infant-attration-grade-button').click(function () {
                self.$el.find('.infant-attraion-grade-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-infant-attration-dept-filter').click(function () {
            self.$el.find('.infant-attraion-dept-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_dept_ratio_filter,#filter-infant-attration-dept-button').click(function () {
                self.$el.find('.infant-attraion-dept-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-infant-attration-location-filter').click(function () {
            self.$el.find('.infant-attraion-location-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_location_ratio_filter,#filter-infant-attration-location-button').click(function () {
                self.$el.find('.infant-attraion-location-wrapper').css('display', 'none');
            });  

            self.$el.find('#fy-infant-attration-budget-filter').click(function () {
            self.$el.find('.infant-attraion-budget-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_budget_ratio_filter,#filter-infant-attration-budget-button').click(function () {
                self.$el.find('.infant-attraion-budget-wrapper').css('display', 'none');
            });  

            self.$el.find('#fy-infant-attration-resource-filter').click(function () {
            self.$el.find('.infant-attraion-resource-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_resource_ratio_filter,#filter-infant-attration-resource-button').click(function () {
                self.$el.find('.infant-attraion-resource-wrapper').css('display', 'none');
            });
            
            self.$el.find('#fy-infant-attration-hiring-type-filter').click(function () {
            self.$el.find('.infant-attraion-hiring-type-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_hiring_type_ratio_filter,#filter-infant-attration-hiring-type-button').click(function () {
                self.$el.find('.infant-attraion-hiring-type-wrapper').css('display', 'none');
            }); 

            self.$el.find('#fy-infant-attration-skill-filter').click(function () {
            self.$el.find('.infant-attraion-skill-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_skill_ratio_filter,#filter-infant-attration-skill-button').click(function () {
                self.$el.find('.infant-attraion-skill-wrapper').css('display', 'none');
            }); 

            self.$el.find('#fy-infant-attration-company-filter').click(function () {
            self.$el.find('.infant-company-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_company_ratio_filter,#filter-infant-attration-company-button').click(function () {
                self.$el.find('.infant-company-wrapper').css('display', 'none');
            }); 

            self.$el.find('#fy-infant-attration-designation-filter').click(function () {
            self.$el.find('.infant-attration-designation-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_designation_ratio_filter,#filter-infant-attration-designation-button').click(function () {
                self.$el.find('.infant-attration-designation-wrapper').css('display', 'none');
            }); 

            self.$el.find('#fy-infant-attration-recruiter-filter').click(function () {
            self.$el.find('.infant-attration-recruiter-wrapper').css('display', '');
            });
            self.$el.find('#close_infant_attration_recruiter_ratio_filter,#filter-infant-attration-recruiter-button').click(function () {
                self.$el.find('.infant-attration-recruiter-wrapper').css('display', 'none');
            }); 
    


            return true;
        },

        render_infant_attration_level_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_level_id }
            if (status == 'refresh') params = {}

            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_level_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);

            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_level_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Level Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Level'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#00B3E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_level_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },
        


        

        render_infant_attration_grade_container_graph: async function (status) {
            var self = this;
            var params = {};
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_grade_id };
            if (status == 'refresh') params = {};
            
            var result = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_grade_ratio',
                kwargs: params,
            });
        
            var categories = result.map(item => item.name);
            var joinedData = result.map(item => item.data[0]); // Extracting joined count
            var leftData = result.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = result.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_grade_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Grade Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Grade'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#3366E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_grade_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },
        
        
        

        render_infant_attration_dept_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_dept_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_dept_ratio',
                kwargs: params,

            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_dept_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Department Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Department'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#00B3E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_dept_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },
        
        render_infant_attration_location_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_location_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_loc_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_location_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Location Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Location'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#4D8066' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_location_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },


        render_infant_attration_budget_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_budget_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_budget_type_ratio',
                kwargs: params,

            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_budget_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Budget Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Budget'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#00B3E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_budget_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },


        render_infant_attration_resource_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_resource_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_resource_ratio',
                kwargs: params,
            
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_resource_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Resource Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Resource'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#376e3b' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_resource_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },

        render_infant_attration_hiring_type_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_hiring_type_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_hiring_typ_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_hiring_type_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Hiring Type Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Hiring Type'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#00B3E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_hiring_type_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },

        render_infant_attration_skill_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_skill_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_skill_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_skill_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Skill  Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: 'Skill'
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#3366E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_skill_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },

        render_infant_attration_company_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_company_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_company_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_company_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Company Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: ' Company '
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#376e3b' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_company_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },

        render_infant_attration_designation_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_designation_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_designation_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_designation_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Designation Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: ' Designation '
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{                              
                        name: 'Joined',
                        data: joinedData,
                        color: '#3366E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_designation_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },

        render_infant_attration_recruiter_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_fy') params = { 'fy_id': self.infant_attration_recruiter_id }
            if (status == 'refresh') params = {}
            var defloc = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_infant_attration_recruiter_ratio',
                kwargs: params,
            });
        
            var categories = defloc.map(item => item.name);
            var joinedData = defloc.map(item => item.data[0]); // Extracting joined count
            var leftData = defloc.map(item => item.data[1]); // Extracting left count
            // var infraRatioData = defloc.map(item => item.infra_ratio);
        
            if (categories.length > 0 && joinedData.length > 0 && leftData.length > 0) {
                Highcharts.chart('infant_attration_recruiter_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        align: 'center',
                        text: 'Recruiter Wise Infant Attrition'
                    },
                    accessibility: {
                        announceNewData: {
                            enabled: true
                        }
                    },
                    xAxis: {
                        // title: {
                        //     text: ' Recruiter '
                        // },
                        categories: categories,
                        type: 'category'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: {
                        title: {
                            text: 'Count'
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal', // Stack the data
                            borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.0f}' // Display y value (data) on top of each bar
                            }
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>' + this.point.category + '</b><br/>' +
                                this.series.name + ': ' + this.point.y + '<br/>' 
                                // 'Infra Ratio: ' + infraRatioData[this.point.index]; // Display infra_ratio on hover
                        }
                    },
                    series: [{
                        name: 'Joined',
                        data: joinedData,
                        color: '#00B3E6' // Set color for joined count
                    }, {
                        name: 'Left',
                        data: leftData,
                        color: '#FF6633' // Set color for left count
                    }],
                });
            } else {
                var container = document.getElementById('infant_attration_recruiter_container');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        },
            
    });
    core.action_registry.add('kw_recruitment_infant_attration_dashboard_tag', RecruitmentinfantattrationDashboard);


});
