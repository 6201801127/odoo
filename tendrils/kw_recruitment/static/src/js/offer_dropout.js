odoo.define('kw_recruitment.kw_recruitment_offer_to_dropout_dashboard', function (require) {
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

    var RecruitmentoffertodropoutDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_offer_to_dropout_dashboard_tag') {
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
            'click #filter-offer-to-dropout-grade-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_grade_id = $('#filter-offer-to-dropout-grade').val();
                if(self.offer_to_dropout_grade_id != 0)
                    self.render_offer_to_dropout_grade_container_graph('filter');
                if(self.offer_to_dropout_grade_id == 0)
                    self.render_offer_to_dropout_grade_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_grade_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet1 = true;
                self.render_offer_to_dropout_grade_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-dropout-dept-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_dept_id = $('#filter-offer-to-dropout-dept').val();
                if(self.offer_to_dropout_dept_id != 0)
                    self.render_offer_to_dropout_dept_container_graph('filter');
                if(self.offer_to_dropout_dept_id == 0)
                    self.render_offer_to_dropout_dept_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_dept_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet2 = true;
                self.render_offer_to_dropout_dept_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-dropout-location-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_location_id = $('#filter-offer-to-dropout-location').val();
                if(self.offer_to_dropout_location_id != 0)
                    self.render_offer_to_dropout_location_container_graph('filter');
                if(self.offer_to_dropout_location_id == 0)
                    self.render_offer_to_dropout_location_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_location_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet3 = true;
                self.render_offer_to_dropout_location_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-dropout-budget-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_budget_id = $('#filter-offer-to-dropout-budget').val();
                if(self.offer_to_dropout_budget_id != 0)
                    self.render_offer_to_dropout_budget_container_graph('filter');
                if(self.offer_to_dropout_budget_id == 0)
                    self.render_offer_to_dropout_budget_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_budget_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet4 = true;
                self.render_offer_to_dropout_budget_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-dropout-resource-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_resource_id = $('#filter-offer-to-dropout-resource').val();
                if(self.offer_to_dropout_resource_id != 0)
                    self.render_offer_to_dropout_resource_container_graph('filter');
                if(self.offer_to_dropout_resource_id == 0)
                    self.render_offer_to_dropout_resource_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_resource_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet5= true;
                self.render_offer_to_dropout_resource_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-dropout-hiring-resource-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_hiring_resource_id = $('#filter-offer-to-dropout-hiring-resource').val();
                if(self.offer_to_dropout_hiring_resource_id != 0)
                    self.render_offer_to_dropout_hiring_resource_container_graph('filter');
                if(self.offer_to_dropout_hiring_resource_id == 0)
                    self.render_offer_to_dropout_hiring_resource_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_hiring_resource_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet6= true;
                self.render_offer_to_dropout_hiring_resource_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-dropout-skill-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_skill_id = $('#filter-offer-to-dropout-skill').val();
                if(self.offer_to_dropout_skill_id != 0)
                    self.render_offer_to_dropout_skill_container_graph('filter');
                if(self.offer_to_dropout_skill_id == 0)
                    self.render_offer_to_dropout_skill_container_graph();('');
            }, 0, true),
        
            'click .offer_to_dropout_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet7= true;
                self.render_offer_to_dropout_skill_container_graph();("refresh");
            }, 0, true),


            'click #filter-offer-to-dropout-company-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_company_id = $('#filter-offer-to-dropout-company').val();
                if(self.offer_to_dropout_company_id != 0)
                    self.render_offer_to_dropout_company_container_graph('filter');
                if(self.offer_to_dropout_company_id == 0)
                    self.render_offer_to_dropout_company_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_comapny_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet8= true;
                self.render_offer_to_dropout_company_container_graph("refresh");
            }, 0, true),


            'click #filter-offer-to-dropout-designation-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_designation_id = $('#filter-offer-to-dropout-designation').val();
                if(self.offer_to_dropout_designation_id != 0)
                    self.render_offer_to_dropout_designation_container_graph('filter');
                if(self.offer_to_dropout_designation_id == 0)
                    self.render_offer_to_dropout_designation_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_designation_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet9= true;
                self.render_offer_to_dropout_designation_container_graph("refresh");
            }, 0, true),


            'click #filter-offer-to-dropout-recruiter-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_dropout_recruiter_id = $('#filter-offer-to-dropout-recruiter').val();
                if(self.offer_to_dropout_recruiter_id != 0)
                    self.render_offer_to_dropout_recruiter_container_graph('filter');
                if(self.offer_to_dropout_recruiter_id == 0)
                    self.render_offer_to_dropout_recruiter_container_graph('');
            }, 0, true),
        
            'click .offer_to_dropout_recruiter_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_dropout_portlet10= true;
                self.render_offer_to_dropout_recruiter_container_graph("refresh");
            }, 0, true),
        },
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Offer To Dropout Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('offertodropoutDashboard', {
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
            self.render_offer_to_dropout_grade_container_graph();
            self.render_offer_to_dropout_dept_container_graph();
            self.render_offer_to_dropout_location_container_graph();
            self.render_offer_to_dropout_budget_container_graph();
            self.render_offer_to_dropout_resource_container_graph();
            self.render_offer_to_dropout_hiring_resource_container_graph();
            self.render_offer_to_dropout_skill_container_graph();
            self.render_offer_to_dropout_company_container_graph();
            self.render_offer_to_dropout_designation_container_graph();
            self.render_offer_to_dropout_recruiter_container_graph();
        },

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.get-offer-dropout-grade-ratio-wrapper,.get-offer-dropout-dept-ratio-wrapper,.get-offer-dropout-location-ratio-wrapper,.get-offer-dropout-budget-ratio-wrapper,.get-offer-dropout-resource-ratio-wrapper,.get-offer-dropout-hiring-resource-ratio-wrapper,.get-offer-dropout-skill-ratio-wrapper,.get-offer-dropout-company-ratio-wrapper,.get-offer-dropout-designation-ratio-wrapper,.get-offer-dropout-recruiter-ratio-wrapper').css('display', 'none');
            self.$el.find('#fy-offer-to-dropout-grade-filter').click(function () {
            self.$el.find('.get-offer-dropout-grade-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_grade_ratio_filter,#filter-offer-to-dropout-grade-button').click(function () {
                self.$el.find('.get-offer-dropout-grade-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-dept-filter').click(function () {
                self.$el.find('.get-offer-dropout-dept-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_dept_ratio_filter,#filter-offer-to-dropout-dept-button').click(function () {
                self.$el.find('.get-offer-dropout-dept-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-location-filter').click(function () {
                self.$el.find('.get-offer-dropout-location-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_location_ratio_filter,#filter-offer-to-dropout-location-button').click(function () {
                self.$el.find('.get-offer-dropout-location-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-budget-filter').click(function () {
                self.$el.find('.get-offer-dropout-budget-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_budget_ratio_filter,#filter-offer-to-dropout-budget-button').click(function () {
                self.$el.find('.get-offer-dropout-budget-ratio-wrapper').css('display', 'none');
            });  
            
            self.$el.find('#fy-offer-to-dropout-resource-filter').click(function () {
                self.$el.find('.get-offer-dropout-resource-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_resource_ratio_filter,#filter-offer-to-dropout-resource-button').click(function () {
                self.$el.find('.get-offer-dropout-resource-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-hiring-resource-filter').click(function () {
                self.$el.find('.get-offer-dropout-hiring-resource-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_hiring_resource_ratio_filter,#filter-offer-to-dropout-hiring-resource-button').click(function () {
                self.$el.find('.get-offer-dropout-hiring-resource-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-skill-filter').click(function () {
                self.$el.find('.get-offer-dropout-skill-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_skill_ratio_filter,#filter-offer-to-dropout-skill-button').click(function () {
                self.$el.find('.get-offer-dropout-skill-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-company-filter').click(function () {
                self.$el.find('.get-offer-dropout-company-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_company_ratio_filter,#filter-offer-to-dropout-company-button').click(function () {
                self.$el.find('.get-offer-dropout-company-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-designation-filter').click(function () {
                self.$el.find('.get-offer-dropout-designation-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_designation_ratio_filter,#filter-offer-to-dropout-designation-button').click(function () {
                self.$el.find('.get-offer-dropout-designation-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-dropout-recruiter-filter').click(function () {
                self.$el.find('.get-offer-dropout-recruiter-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_dropout_recruiter_ratio_filter,#filter-offer-to-dropout-recruiter-button').click(function () {
                self.$el.find('.get-offer-dropout-recruiter-ratio-wrapper').css('display', 'none');
            });   



         return true;
        },

        render_offer_to_dropout_grade_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_grade_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_grade_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            console.log(defofferdata,'defofferdata')
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_grade_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_dropout_grade_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Grade Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_dept_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_dept_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_dept_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_dept_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_dept_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Department Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_location_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_location_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_loc_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_location_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_location_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Location Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },


        render_offer_to_dropout_budget_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_budget_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_budget_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_budget_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_budget_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Budget Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_resource_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_resource_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_resource_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_resource_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_resource_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Resource Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_hiring_resource_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_hiring_resource_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_hire_resource_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_hiring_resource_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_hiring_resource_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Hire Resource Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_skill_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_skill_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_skill_resource_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_skill_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_skill_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To DropOut Skill Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_company_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_company_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_company_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_company_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_company_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Company Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_designation_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_designation_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_designation_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_designation_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_designation_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Designation Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_dropout_recruiter_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_dropout_recruiter_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_dropout_recruiter_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_dropout_recruiter_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('get_offer_to_dropout_recruiter_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Dropout Recruiter Wise Ratio',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    // labels: {
                    //     rotation: -90
                    // },
                    accessibility: {
                        description: 'Ratio'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'Offered',
                        data: valdData,
                    },
                    {
                        name: 'Dropped',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },



    });
    core.action_registry.add('kw_recruitment_offer_to_dropout_dashboard_tag', RecruitmentoffertodropoutDashboard);


});
