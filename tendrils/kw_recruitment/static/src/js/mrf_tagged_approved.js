odoo.define('kw_recruitment.kw_recruitment_mrf_dashboard', function (require) {
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

    var RecruitmentmrfDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_recruitment_mrf_dashboard_tag') {
                self._rpc({
                    model: 'recruitment_data_dashboard',
                    method: 'get_filter_data',
                }, []).then(function (result) {
                    self.mrf_fy_filters = result['dashboard_fy_filters'][0];
                }).done(function () {
                    self.render();
                    self.href = window.location.href;
                });
            }
        },
        events: {
            'click #filter-mrf-tagged-dept-button': _.debounce(function (ev) {
                var self = this;
                self.mrf_dept_id = $('#filter-mrf-tagged-dept').val();
                if(self.mrf_dept_id != 0)
                    self.mrf_dept_tagged_approved_container_graph('filter');
                if(self.mrf_dept_id == 0)
                    self.mrf_dept_tagged_approved_container_graph('');
            }, 0, true),
        
            'click .refresh_mrf_tagged_dept_portlet': _.debounce(function () {
                var self = this;
                self.refresh_mrf_portlet1 = true;
                self.mrf_dept_tagged_approved_container_graph("refresh");
            }, 0, true),

            'click #filter-mrf-tagged-location-button': _.debounce(function (ev) {
                var self = this;
                self.mrf_location_id = $('#filter-mrf-tagged-location').val();
                if(self.mrf_location_id != 0)
                    self.mrf_location_tagged_approved_container_graph('filter');
                if(self.mrf_location_id == 0)
                    self.mrf_location_tagged_approved_container_graph('');
            }, 0, true),
        
            'click .refresh_mrf_tagged_location_portlet': _.debounce(function () {
                var self = this;
                self.refresh_mrf_portlet2 = true;
                self.mrf_location_tagged_approved_container_graph("refresh");
            }, 0, true),

            'click #filter-mrf-tagged-budget-button': _.debounce(function (ev) {
                var self = this;
                self.mrf_budget_id = $('#filter-mrf-tagged-budget').val();
                if(self.mrf_budget_id != 0)
                    self.mrf_budget_tagged_approved_container_graph('filter');
                if(self.mrf_budget_id == 0)
                    self.mrf_budget_tagged_approved_container_graph('');
            }, 0, true),
        
            'click .refresh_mrf_tagged_budget_portlet': _.debounce(function () {
                var self = this;
                self.refresh_mrf_portlet3 = true;
                self.mrf_budget_tagged_approved_container_graph("refresh");
            }, 0, true),
            
            'click #filter-mrf-tagged-resource-button': _.debounce(function (ev) {
                var self = this;
                self.mrf_resource_id = $('#filter-mrf-tagged-resource').val();
                if(self.mrf_resource_id != 0)
                    self.mrf_resource_tagged_approved_container_graph('filter');
                if(self.mrf_resource_id == 0)
                    self.mrf_resource_tagged_approved_container_graph('');
            }, 0, true),
        
            'click .refresh_mrf_tagged_resource_portlet': _.debounce(function () {
                var self = this;
                self.refresh_mrf_portlet4 = true;
                self.mrf_resource_tagged_approved_container_graph("refresh");
            }, 0, true),


            'click #filter-mrf-tagged-skill-button': _.debounce(function (ev) {
                var self = this;
                self.mrf_skill_id = $('#filter-mrf-tagged-skill').val();
                if(self.mrf_skill_id != 0)
                    self.mrf_skill_tagged_approved_container_graph('filter');
                if(self.mrf_skill_id == 0)
                    self.mrf_skill_tagged_approved_container_graph('');
            }, 0, true),
        
            'click .refresh_mrf_tagged_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_mrf_portlet5 = true;
                self.mrf_skill_tagged_approved_container_graph("refresh");
            }, 0, true),

            'click #filter-mrf-tagged-designation-button': _.debounce(function (ev) {
                var self = this;
                self.mrf_designation_id = $('#filter-mrf-tagged-designation').val();
                if(self.mrf_designation_id != 0)
                    self.mrf_designation_tagged_approved_container_graph('filter');
                if(self.mrf_designation_id == 0)
                    self.mrf_designation_tagged_approved_container_graph('');
            }, 0, true),
        
            'click .refresh_mrf_tagged_designation_portlet': _.debounce(function () {
                var self = this;
                self.refresh_mrf_portlet6 = true;
                self.mrf_designation_tagged_approved_container_graph("refresh");
            }, 0, true),


            


        },
        
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'MRF Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('mrfDashboard', {
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
            self.mrf_dept_tagged_approved_container_graph();
            self.mrf_location_tagged_approved_container_graph();
            self.mrf_budget_tagged_approved_container_graph();
            self.mrf_resource_tagged_approved_container_graph();   
            self.mrf_skill_tagged_approved_container_graph();     
            self.mrf_designation_tagged_approved_container_graph();  
        },

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.mrf-tagged-dept-wrapper,.mrf-tagged-location-wrapper,.mrf-tagged-budget-wrapper,.mrf-tagged-resource-wrapper,.mrf-tagged-skill-wrapper,.mrf-tagged-designation-wrapper').css('display', 'none');


            self.$el.find('#fy-mrf-tagged-dept-filter').click(function () {
            self.$el.find('.mrf-tagged-dept-wrapper').css('display', '');
            });
            self.$el.find('#close_mrf_tagged_dept_ratio_filter,#filter-mrf-tagged-dept-button').click(function () {
                self.$el.find('.mrf-tagged-dept-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-mrf-tagged-location-filter').click(function () {
            self.$el.find('.mrf-tagged-location-wrapper').css('display', '');
            });
            self.$el.find('#close_mrf_tagged_location_ratio_filter,#filter-mrf-tagged-location-button').click(function () {
                self.$el.find('.mrf-tagged-location-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-mrf-tagged-budget-filter').click(function () {
            self.$el.find('.mrf-tagged-budget-wrapper').css('display', '');
            });
            self.$el.find('#close_mrf_tagged_budget_ratio_filter,#filter-mrf-tagged-budget-button').click(function () {
                self.$el.find('.mrf-tagged-budget-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-mrf-tagged-resource-filter').click(function () {
            self.$el.find('.mrf-tagged-resource-wrapper').css('display', '');
            });
            self.$el.find('#close_mrf_tagged_resource_ratio_filter,#filter-mrf-tagged-resource-button').click(function () {
                self.$el.find('.mrf-tagged-resource-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-mrf-tagged-skill-filter').click(function () {
            self.$el.find('.mrf-tagged-skill-wrapper').css('display', '');
            });
            self.$el.find('#close_mrf_tagged_skill_ratio_filter,#filter-mrf-tagged-skill-button').click(function () {
                self.$el.find('.mrf-tagged-skill-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-mrf-tagged-designation-filter').click(function () {
            self.$el.find('.mrf-tagged-designation-wrapper').css('display', '');
            });
            self.$el.find('#close_mrf_tagged_designation_ratio_filter,#filter-mrf-tagged-designation-button').click(function () {
                self.$el.find('.mrf-tagged-designation-wrapper').css('display', 'none');
            });

            return true;
        },

        mrf_dept_tagged_approved_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.mrf_dept_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_dept_mrf_tagged_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('mrf_tagged_dept_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('mrf_tagged_dept_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'MRF Tagged Department Wise Ratio',
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
                        name: 'Raised',
                        data: ratedData,

                    },
                    {
                        name: 'Approved',
                        data: valdData,

                    }
                ],
                colors: [
                    '#FF6633','#FFCC00','#00BFFF'
                ],
            });

        },

        mrf_location_tagged_approved_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.mrf_location_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_location_mrf_tagged_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('mrf_tagged_location_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.data); 
            var ratedData = defofferdata.map(item => item.category); 



            Highcharts.chart('mrf_tagged_location_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'MRF Tagged Location Wise Ratio',
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
                        name: 'Raised',
                        data: valdData,
                    },
                    {
                        name: 'Approved',
                        data: ratedData,
                    }
                ],
                colors: [
                    '#FFCC00','#00BFFF', '#FF6633'
                ],
            });

        },

        mrf_budget_tagged_approved_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.mrf_budget_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_budget_typ_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('mrf_tagged_budget_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('mrf_tagged_budget_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'MRF Tagged Budget Wise Ratio',
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
                        name: 'Raised',
                        data: ratedData,

                    },
                    {
                        name: 'Approved',
                        data: valdData,

                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        mrf_resource_tagged_approved_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.mrf_resource_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_hire_resource_typ_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('mrf_tagged_resource_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('mrf_tagged_resource_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'MRF Tagged Hire Resource Wise Ratio',
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
                        name: 'Raised',
                        data: ratedData,

                    },
                    {
                        name: 'Approved',
                        data: valdData,

                    }
                ],
                colors: [
                    '#FFCC00','#00BFFF', '#FF6633'
                ],
            });

        },


        mrf_skill_tagged_approved_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.mrf_skill_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_skill_mrf_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('mrf_tagged_skill_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('mrf_tagged_skill_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'MRF Tagged Skill Wise Ratio',
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
                        name: 'Raised',
                        data: ratedData,

                    },
                    {
                        name: 'Approved',
                        data: valdData,

                    }
                ],
                colors: [
                    '#00BFFF', '#FF6633','#FFCC00'
                ],
            });

        },

        mrf_designation_tagged_approved_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            if (status == 'filter') parameters = {'fy_id': self.mrf_designation_id}
            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_designation_mrf_ratio',
                args: [parameters],
                kwargs: parameters  
            });
            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('mrf_tagged_designation_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 
            var ratedData = defofferdata.map(item => item.data); 


            Highcharts.chart('mrf_tagged_designation_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'MRF Tagged Designation Wise Ratio',
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
                        name: 'Raised',
                        data: ratedData,

                    },
                    {
                        name: 'Approved',
                        data: valdData,

                    }
                ],
                colors: [
                    '#FFCC00','#00BFFF', '#FF6633'
                ],
            });

        },

        
    });
    core.action_registry.add('kw_recruitment_mrf_dashboard_tag', RecruitmentmrfDashboard);


});
