odoo.define('kw_recruitment.kw_recruitment_vacancy_dashboard_tag', function (require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;

    var RecruitmentvacancyDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            self.fy_id = 0;

            if (context.tag == 'kw_recruitment_vacancy_dashboard_tag') {
                self._rpc({
                    model: 'recruitment_data_dashboard',
                    method: 'get_filter_data',
                }, []).then(function (result) {
                    self.vacancy_fy_filters = result['dashboard_fy_filters'][0];
                }).done(function () {
                    self.render();
                    self.href = window.location.href;
                });
            }
        },
        events: {


            // 'click #filter-dept-wise-vacancy-button': _.debounce(function (ev) {
            //     var self = this;
            //     self.dept_id = $('#filter-dept-wise-vacancy').val();
            //     if(self.dept_id != 0)
            //         self.dept_wise_vacancy_container_graph('filter_fy');
            //     if(self.dept_id == 0)
            //         self.dept_wise_vacancy_container_graph('');
            // }, 0, true),

            'click #filter-dept-wise-vacancy-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-dept-wise-vacancy').val();
                if (self.fy_id != 0)
                    self.dept_wise_vacancy_container_graph('filter_fy');
                else
                    self.dept_wise_vacancy_container_graph('');
            }, 0, true),
        
            'click .refresh_dept_vacancy_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet1 = true;
                self.dept_wise_vacancy_container_graph("refresh");
            }, 0, true),

            'click #filter-desg-wise-vacancy-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-desg-wise-vacancy').val();
                if (self.fy_id != 0)
                    self.designation_wise_vacancy_container_graph('filter_fy');
                else
                    self.designation_wise_vacancy_container_graph('');
            }, 0, true),
        
            'click .refresh_desg_vacancy_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet2 = true;
                self.designation_wise_vacancy_container_graph("refresh");
            }, 0, true),

            'click #filter-dept-wise-joined-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-dept-wise-joined').val();
                if (self.fy_id != 0)
                    self.dept_wise_joined_container_graph('filter_fy');
                else
                    self.dept_wise_joined_container_graph('');
            }, 0, true),
        
            'click .refresh_dept_wise_joined_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet3 = true;
                self.dept_wise_joined_container_graph("refresh");
            }, 0, true),


            'click #filter-desg-wise-joined-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-desg-wise-joined').val();
                if (self.fy_id != 0)
                    self.desg_wise_joined_container_graph('filter_fy');
                else
                    self.desg_wise_joined_container_graph('');
            }, 0, true),
        
            'click .refresh_desg_wise_joined_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet4 = true;
                self.desg_wise_joined_container_graph("refresh");
            }, 0, true),

            'click #filter-location-wise-vacancy-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-location-wise-vacancy').val();
                if (self.fy_id != 0)
                    self.location_wise_vacancy_container_graph('filter_fy');
                else
                    self.location_wise_vacancy_container_graph('');
            }, 0, true),
        
            'click .refresh_location_vacancy_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet5 = true;
                self.location_wise_vacancy_container_graph("refresh");
            }, 0, true),

            'click #filter-skill-wise-vacancy-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-skill-wise-vacancy').val();
                if (self.fy_id != 0)
                    self.skill_wise_vacancy_container_graph('filter_fy');
                else
                    self.skill_wise_vacancy_container_graph('');
            }, 0, true),
        
            'click .refresh_skill_vacancy_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet6 = true;
                self.skill_wise_vacancy_container_graph("refresh");
            }, 0, true),

            'click #filter-location-wise-joined-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-location-wise-joined').val();
                if (self.fy_id != 0)
                    self.location_wise_joined_container_graph('filter_fy');
                else
                    self.location_wise_joined_container_graph('');
            }, 0, true),
        
            'click .refresh_location_wise_joined_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet7 = true;
                self.location_wise_joined_container_graph("refresh");
            }, 0, true),

            'click #filter-skill-wise-joined-button': _.debounce(function (ev) {
                var self = this;
                self.fy_id = $('#filter-skill-wise-joined').val();
                if (self.fy_id != 0)
                    self.skill_wise_joined_container_graph('filter_fy');
                else
                    self.skill_wise_joined_container_graph('');
            }, 0, true),
        
            'click .refresh_skill_wise_joined_portlet': _.debounce(function () {
                var self = this;
                self.refresh_portlet8 = true;
                self.skill_wise_joined_container_graph("refresh");
            }, 0, true),
        },
        
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Vacancy Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('vacancyDashboard', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(hr_dashboard).prependTo(self.$el);
            self.render_graphs();
            self.renderDashboard();
            return hr_dashboard;
        },
        
        render_graphs: function(){
            var self = this;
            self.dept_wise_vacancy_container_graph();
            self.designation_wise_vacancy_container_graph();
            self.dept_wise_joined_container_graph();
            self.desg_wise_joined_container_graph();
            self.location_wise_vacancy_container_graph();
            self.skill_wise_vacancy_container_graph();
            self.location_wise_joined_container_graph();
            self.skill_wise_joined_container_graph();

        },

        renderDashboard: async function () {
            var self = this;

            self.$el.find('.dept-vacancy-wrapper,.desg-vacancy-wrapper,.dept-wise-joined-wrapper,.desg-wise-joined-wrapper,.location-vacancy-wrapper,.skill-vacancy-wrapper,.location-wise-joined-wrapper,.skill-wise-joined-wrapper').css('display', 'none');


            self.$el.find('#fy-dept-vacancy-filter').click(function () {
            self.$el.find('.dept-vacancy-wrapper').css('display', '');
            });
            self.$el.find('#close_dept_wise_vacancy_filter,#filter-dept-wise-vacancy-button').click(function () {
                self.$el.find('.dept-vacancy-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-desg-vacancy-filter').click(function () {
            self.$el.find('.desg-vacancy-wrapper').css('display', '');
            });
            self.$el.find('#close_desg_wise_vacancy_filter,#filter-desg-wise-vacancy-button').click(function () {
                self.$el.find('.desg-vacancy-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-dept-joined-filter').click(function () {
            self.$el.find('.dept-wise-joined-wrapper').css('display', '');
            });
            self.$el.find('#close_dept_wise_joined_filter,#filter-dept-wise-joined-button').click(function () {
                self.$el.find('.dept-wise-joined-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-desg-joined-filter').click(function () {
            self.$el.find('.desg-wise-joined-wrapper').css('display', '');
            });
            self.$el.find('#close_desg_wise_joined_filter,#filter-desg-wise-joined-button').click(function () {
                self.$el.find('.desg-wise-joined-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-location-vacancy-filter').click(function () {
            self.$el.find('.location-vacancy-wrapper').css('display', '');
            });
            self.$el.find('#close_location_wise_vacancy_filter,#filter-location-wise-vacancy-button').click(function () {
                self.$el.find('.location-vacancy-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-skill-vacancy-filter').click(function () {
            self.$el.find('.skill-vacancy-wrapper').css('display', '');
            });
            self.$el.find('#close_skill_wise_vacancy_filter,#filter-skill-wise-vacancy-button').click(function () {
                self.$el.find('.skill-vacancy-wrapper').css('display', 'none');
            });

            self.$el.find('#fy-location-joined-filter').click(function () {
            self.$el.find('.location-wise-joined-wrapper').css('display', '');
            });
            self.$el.find('#close_location_wise_joined_filter,#filter-location-wise-joined-button').click(function () {
                self.$el.find('.location-wise-joined-wrapper').css('display', 'none');
            });
            
            self.$el.find('#fy-skill-joined-filter').click(function () {
            self.$el.find('.skill-wise-joined-wrapper').css('display', '');
            });
            self.$el.find('#close_skill_wise_joined_filter,#filter-skill-wise-joined-button').click(function () {
                self.$el.find('.skill-wise-joined-wrapper').css('display', 'none');
            });


            return true;
        },
        

        dept_wise_vacancy_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_dept_wise_vacancy_ratio',
                args: [],  // Pass an empty list for positional arguments
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('vacancy_dept_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category
            }));

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 

            Highcharts.chart('vacancy_dept_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Department Wise Vacancy',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: 'Job Position',
                    data: seriesData
                }],
                colors: [
                    '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                   '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                   '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
               ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },

        designation_wise_vacancy_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_desgination_wise_vacancy_ratio',
                args: [],  // Pass an empty list for positional arguments
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('vacancy_desg_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category
            }));

            Highcharts.chart('vacancy_desg_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Designation Wise Vacancy',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: 'Job Position',
                    data: seriesData
                }],
                colors: [
                    '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                    '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                   '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#E6B333',
               ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 3,
                    itemMarginBottom: 3,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },

        dept_wise_joined_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_dept_wise_joined_ratio',
                args: [],  // Pass an empty list for positional arguments
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('joined_dept_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category,
                // sliced: true,   
                selected: true       

            }));


            Highcharts.chart('joined_dept_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Department Wise Joined',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        borderColor: '#FFFFFF',  // Set border color to white
                        slicedOffset: 25,  // Adjust the offset distance to create more gap
                        borderWidth: 3,    // Set border width to create gap effect
                        // innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: 'Job Position',
                    data: seriesData
                }],
                colors: [
                    '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#FF6633', '#00B3E6','#991AFF', 
                    '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066','#1AB399','#791fb5',
                   '#6666FF','#E6B333', '#FF1A66', '#33FFCC',
                ],

                legend: {
                    layout: 'horizontal',        
                    align: 'left',             
                    verticalAlign: 'bottom',    
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    labelFormatter: function() { 
                        return this.name;
                    }
                },
                
            });

        },
        
        desg_wise_joined_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_desgination_wise_joined_ratio',
                args: [],  // Pass an empty list for positional arguments
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('joined_desg_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category,
                sliced: false,   
                selected: true 
            }));

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 

            Highcharts.chart('joined_desg_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Designation Wise Joined',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        borderColor: '#FFFFFF',  
                        slicedOffset: 25,  
                        borderWidth: 3,    
                        // innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: 'Job Position',
                    data: seriesData
                }],
                colors: [
                    '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#FF6633', '#00B3E6','#991AFF', 
                    '#3366E6',  '#1AB399','#791fb5','#6666FF','#E6B333', '#FF1A66',
                    '#33FFCC','#99FF99', '#FF99E6','#66991A','#4D8066',
                ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },

        location_wise_vacancy_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_location_wise_vacancy_ratio',
                args: [],  // Pass an empty list for positional arguments
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('vacancy_location_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category
            }));

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 

            Highcharts.chart('vacancy_location_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Location Wise Vacancy',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: ' Location ',
                    data: seriesData
                }],
                colors: [
                    '#6666FF','#E6B333', '#FF1A66','#99E6E6', '#FF6633', '#00B3E6',
                    '#3366E6',  '#1AB399','#791fb5','#991AFF','#33FFCC','#99FF99', 
                    '#FF99E6','#66991A','#4D8066','#E64D66', '#4DB380', '#FF4D4D',
                ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },

        skill_wise_vacancy_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_skill_wise_vacancy_ratio',
                args: [],  
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('vacancy_skill_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category
            }));

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 

            Highcharts.chart('vacancy_skill_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Skill Wise Vacancy',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: ' Skill ',
                    data: seriesData
                }],
                colors: [
                    '#991AFF','#33FFCC','#99FF99','#E64D66', '#4DB380', '#FF4D4D',
                    '#3366E6',  '#1AB399','#791fb5','#99E6E6', '#FF6633', '#00B3E6',
                    '#FF99E6','#66991A','#4D8066','#6666FF','#E6B333', '#FF1A66',
                ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 2,
                    itemMarginBottom: 2,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },

        location_wise_joined_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_location_wise_joined_ratio',
                args: [],  
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('joined_location_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category,
                sliced: false,   
                selected: true 
            }));

            Highcharts.chart('joined_location_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Location  Wise Joined',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        borderColor: '#FFFFFF',  
                        slicedOffset: 25,  
                        borderWidth: 3,    
                        // innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: ' Location ',
                    data: seriesData
                }],
                colors: [
                    '#991AFF','#33FFCC', '#4DB380', '#FF4D4D','#6666FF','#E6B333', '#FF1A66',
                    '#3366E6','#FF6633', '#00B3E6','#99FF99','#E64D66',
                    '#FF99E6','#66991A','#4D8066','#1AB399','#791fb5','#99E6E6',
                ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },

        skill_wise_joined_container_graph: async function (status) {
            var self = this;
            var parameters = {};

            if (status === 'filter_fy') {
                parameters = { 'fy_id': self.fy_id };

            }

            var defofferdata = await this._rpc({
                model: 'recruitment_data_dashboard',
                method: 'get_skill_wise_joined_ratio',
                args: [],  
                kwargs: parameters  
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('joined_skill_wise_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var seriesData = defofferdata.map(item => ({
                name: item.name,
                y: item.category,
                sliced: false,   
                selected: true 
            }));

            var categories = defofferdata.map(item => item.name); 
            var valdData = defofferdata.map(item => item.category); 

            Highcharts.chart('joined_skill_wise_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45,
                        beta: 0
                    }
                },
                title: {
                    text: 'Skill Wise Joined',
                    align: 'center'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        depth: 35,
                        borderColor: '#FFFFFF',  
                        slicedOffset: 25,  
                        borderWidth: 3,    
                        // innerSize: '50%', // Adjust the inner radius
                        // pointPadding: 0.2,
                        // borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        showInLegend: true

                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: ' Skill ',
                    data: seriesData
                }],
                colors: [
                    '#991AFF','#33FFCC', '#4DB380', '#FF4D4D','#6666FF','#E6B333', '#FF1A66',
                    '#3366E6','#FF6633', '#00B3E6','#99FF99','#E64D66',
                    '#FF99E6','#66991A','#4D8066','#1AB399','#791fb5','#99E6E6',
                ],
                legend: {
                    layout: 'horizontal',
                    align: 'left',
                    verticalAlign: 'bottom',
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    labelFormatter: function() {
                        return this.name;
                    }
                },
            });

        },
    });

    core.action_registry.add('kw_recruitment_vacancy_dashboard_tag', RecruitmentvacancyDashboard);
});
