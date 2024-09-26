odoo.define('kw_recruitment.kw_recruitment_offer_to_join_dashboard', function (require) {
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

    var RecruitmentoffertojoinDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_offer_to_join_dashboard_tag') {
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
            'click #filter-offer-to-join-grade-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_grade_id = $('#filter-offer-to-join-grade').val();
                console.log(self.offer_to_join_grade_id,"=======grade===========")
                if(self.offer_to_join_grade_id != 0)
                    self.render_offer_to_join_grade_container_graph('filter');
                if(self.offer_to_join_grade_id == 0)
                    self.render_offer_to_join_grade_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_grade_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet1 = true;
                self.render_offer_to_join_grade_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-dept-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_dept_id = $('#filter-offer-to-join-dept').val();
                if(self.offer_to_join_dept_id != 0)
                    self.render_offer_to_join_dept_container_graph('filter');
                if(self.offer_to_join_dept_id == 0)
                    self.render_offer_to_join_dept_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_dept_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet2 = true;
                self.render_offer_to_join_dept_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-loc-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_loc_id = $('#filter-offer-to-join-loc').val();
                if(self.offer_to_join_loc_id != 0)
                    self.render_offer_to_join_location_container_graph('filter');
                if(self.offer_to_join_loc_id == 0)
                    self.render_offer_to_join_location_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_loc_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet3 = true;
                self.render_offer_to_join_location_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-budget-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_budget_id = $('#filter-offer-to-join-budget').val();
                if(self.offer_to_join_budget_id != 0)
                    self.render_offer_to_join_budget_container_graph('filter');
                if(self.offer_to_join_budget_id == 0)
                    self.render_offer_to_join_budget_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_budget_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet4 = true;
                self.render_offer_to_join_budget_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-resource-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_resource_id = $('#filter-offer-to-join-resource').val();
                if(self.offer_to_join_resource_id != 0)
                    self.render_offer_to_join_resource_container_graph('filter');
                if(self.offer_to_join_resource_id == 0)
                    self.render_offer_to_join_resource_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_resource_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet5 = true;
                self.render_offer_to_join_resource_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-hire-res-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_hire_res_id = $('#filter-offer-to-join-hire-res').val();
                if(self.offer_to_join_hire_res_id != 0)
                    self.render_offer_to_join_hire_res_container_graph('filter');
                if(self.offer_to_join_hire_res_id == 0)
                    self.render_offer_to_join_hire_res_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_hire_res_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet6 = true;
                self.render_offer_to_join_hire_res_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-skill-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_skill_id = $('#filter-offer-to-join-skill').val();
                if(self.offer_to_join_skill_id != 0)
                    self.render_offer_to_join_skill_container_graph('filter');
                if(self.offer_to_join_skill_id == 0)
                    self.render_offer_to_join_skill_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet7 = true;
                self.render_offer_to_join_skill_container_graph("refresh");
            }, 0, true),
            

            'click #filter-offer-to-join-company-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_company_id = $('#filter-offer-to-join-company').val();
                if(self.offer_to_join_company_id != 0)
                    self.render_offer_to_join_comapny_container_graph('filter');
                if(self.offer_to_join_company_id == 0)
                    self.render_offer_to_join_comapny_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_company_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet8 = true;
                self.render_offer_to_join_comapny_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-designation-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_designation_id = $('#filter-offer-to-join-designation').val();
                if(self.offer_to_join_designation_id != 0)
                    self.render_offer_to_join_designation_container_graph('filter');
                if(self.offer_to_join_designation_id == 0)
                    self.render_offer_to_join_designation_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_designation_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet9 = true;
                self.render_offer_to_join_designation_container_graph("refresh");
            }, 0, true),

            'click #filter-offer-to-join-recruiter-button': _.debounce(function (ev) {
                var self = this;
                self.offer_to_join_recruiter_id = $('#filter-offer-to-join-recruiter').val();
                if(self.offer_to_join_recruiter_id != 0)
                    self.render_offer_to_join_recruiter_container_graph('filter');
                if(self.offer_to_join_recruiter_id == 0)
                    self.render_offer_to_join_recruiter_container_graph('');
            }, 0, true),
        
            'click .offer_to_join_recruiter_portlet': _.debounce(function () {
                var self = this;
                self.refresh_offer_to_join_portlet10 = true;
                self.render_offer_to_join_recruiter_container_graph("refresh");
            }, 0, true),



        },

        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Offer To Join Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('offertojoinDashboard', {
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
            self.render_offer_to_join_grade_container_graph();
            self.render_offer_to_join_dept_container_graph();
            self.render_offer_to_join_location_container_graph();
            self.render_offer_to_join_budget_container_graph();
            self.render_offer_to_join_resource_container_graph();
            self.render_offer_to_join_hire_res_container_graph();
            self.render_offer_to_join_skill_container_graph();
            self.render_offer_to_join_comapny_container_graph();
            self.render_offer_to_join_designation_container_graph();
            self.render_offer_to_join_recruiter_container_graph();
        },

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.get-offer-to-join-grade-ratios-wrapper,.get-offer-to-join-dept-ratio-wrapper,.get-offer-to-join-loc-ratio-wrapper,.get-offer-to-join-budget-wrapper,.get-offer-to-join-resource-ratio-wrapper,.get-offer-to-join-hire-res-ratio-wrapper,.get-offer-to-join-skill-ratio-wrapper,.get-offer-to-join-company-ratio-wrapper,.get-offer-to-join-designation-ratio-wrapper,.get-offer-to-join-recruiter-ratio-wrapper').css('display', 'none');
            self.$el.find('#fy-offer-to-join-grade-filter').click(function () {
            self.$el.find('.get-offer-to-join-grade-ratios-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_grade_ratio_filter,#filter-offer-to-join-grade-button').click(function () {
                self.$el.find('.get-offer-to-join-grade-ratios-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-dept-filter').click(function () {
            self.$el.find('.get-offer-to-join-dept-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_dept_ratio_filter,#filter-offer-to-join-dept-button').click(function () {
                self.$el.find('.get-offer-to-join-dept-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-loc-filter').click(function () {
            self.$el.find('.get-offer-to-join-loc-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_loc_ratio_filter,#filter-offer-to-join-loc-button').click(function () {
                self.$el.find('.get-offer-to-join-loc-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-budget-filter').click(function () {
            self.$el.find('.get-offer-to-join-budget-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_budget_ratio_filter,#filter-offer-to-join-budget-button').click(function () {
                self.$el.find('.get-offer-to-join-budget-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-resource-filter').click(function () {
                self.$el.find('.get-offer-to-join-resource-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_resource_ratio_filter,#filter-offer-to-join-resource-button').click(function () {
                self.$el.find('.get-offer-to-join-resource-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-hire-res-filter').click(function () {
                self.$el.find('.get-offer-to-join-hire-res-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_hire_res_ratio_filter,#filter-offer-to-join-hire-res-button').click(function () {
                self.$el.find('.get-offer-to-join-hire-res-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-skill-filter').click(function () {
                self.$el.find('.get-offer-to-join-skill-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_skill_ratio_filter,#filter-offer-to-join-skill-button').click(function () {
                self.$el.find('.get-offer-to-join-skill-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-company-filter').click(function () {
                self.$el.find('.get-offer-to-join-company-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_company_ratio_filter,#filter-offer-to-join-company-button').click(function () {
                self.$el.find('.get-offer-to-join-company-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-designation-filter').click(function () {
                self.$el.find('.get-offer-to-join-designation-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_designation_ratio_filter,#filter-offer-to-join-designation-button').click(function () {
                self.$el.find('.get-offer-to-join-designation-ratio-wrapper').css('display', 'none');
            });   

            self.$el.find('#fy-offer-to-join-recruiter-filter').click(function () {
                self.$el.find('.get-offer-to-join-recruiter-ratio-wrapper').css('display', '');
            });
            self.$el.find('#close_offer_to_join_recruiter_ratio_filter,#filter-offer-to-join-recruiter-button').click(function () {
                self.$el.find('.get-offer-to-join-recruiter-ratio-wrapper').css('display', 'none');
            });   
        return true;
        },
        
        render_offer_to_join_grade_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_grade_id}
            console.log("parameters=====",parameters)
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_grade_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_grade_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_grade_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Grade Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#FFCC00', '#FF6633', '#00BFFF'
                ],
            });

        },

        render_offer_to_join_dept_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_dept_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_dept_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_dept_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_dept_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Department Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633', '#FFCC00'
                ],
            });

        },

        render_offer_to_join_location_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_loc_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_loc_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_loc_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_loc_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Location Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FFCC00', '#FF6633'
                ],
            });

        },

        render_offer_to_join_budget_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_budget_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_budget_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_budget_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_budget_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Budget Type Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_join_resource_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_resource_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_resource_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_resource_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_resource_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Type of Resource wise Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FFCC00', '#FF6633'
                ],
            });

        },

        render_offer_to_join_hire_res_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_hire_res_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_hire_res_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_hire_res_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_hire_res_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Type of Hiring wise Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#FF6633', '#FFCC00', '#00BFFF'
                ],
            });

        },

        render_offer_to_join_skill_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_skill_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_skill_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_skill_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_skill_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Skill Wise Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FFCC00', '#FF6633'
                ],
            });

        },

        render_offer_to_join_comapny_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_company_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_company_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_company_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_company_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Company Wise Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#FF6633', '#FFCC00', '#00BFFF'
                ],
            });

        },

        render_offer_to_join_designation_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_designation_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_designation_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_designation_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_designation_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Designation Wise Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        render_offer_to_join_recruiter_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.offer_to_join_recruiter_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_offer_to_join_recruiter_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('get_offer_to_join_recruiter_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); // Assuming 'category' is the value data
            var ratedData = defofferdata.map(item => item.data); // Assuming 'data' is the rate data


            Highcharts.chart('get_offer_to_join_recruiter_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Offer To Join Recruiter Wise Ratio',
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
                        name: 'Joined',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

    });
    core.action_registry.add('kw_recruitment_offer_to_join_dashboard_tag', RecruitmentoffertojoinDashboard);


});