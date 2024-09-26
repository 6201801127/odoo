odoo.define('change_request_management.cr_sr_dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var framework = require('web.framework');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var CrSrDashboard = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        
        template: 'CrsrDashboard',
        init: function (parent, action) {
            this.actionManager = parent;
            this.action = action;
            this.domain = [];
            return this._super.apply(this, arguments);
        },
        events:{
            
            'click #filter-uploaded-by-administrator': _.debounce(function(){
                var self = this;
                self.uploadYearselect = $('#upload-years-select').val();
                self.uploadMonthSelect = $('#upload-months-select').val();

                self.render_uploaded_by_cr_sr_container_graph("filter")
            },200,true),
            

            
            'click .refresh_employee_portlet': _.debounce(function () {
                var self = this;
                self.refresh_uploaded_by_data = true;
                self.render_uploaded_by_cr_sr_container_graph("refresh_uploaded_data");
            }, 0, true),

            'click #filter-project-wise': _.debounce(function(){
                var self = this;
                self.projectYearselect = $('#project-years-select').val();
                self.projectMonthSelect = $('#project-months-select').val();

                self.render_project_wise_cr_sr_container_graph("filter")
            },200,true),
            

            
            'click .refresh_project_portlet': _.debounce(function () {
                var self = this;
                self.refresh_project_wise_data = true;
                self.render_project_wise_cr_sr_container_graph("refresh_project_data");
            }, 0, true),

            'click #filter-day-wise': _.debounce(function(){
                var self = this;
                self.daywiseYearselect = $('#day-wise-years-select').val();
                self.daywiseMonthSelect = $('#day-wise-months-select').val();

                self.render_day_wise_staticstis_container_graph("filter")
            },200,true),
            

            
            'click .refresh_day_wise_portlet': _.debounce(function () {
                var self = this;
                self.refresh_day_wise_data = true;
                self.render_day_wise_staticstis_container_graph("refresh_day_wise_data");
            }, 0, true),


            
        },        
    
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'CR SR dashboard');
            return this._super().then(function () {
                setTimeout(function () {
                    self.render();
                }, 0);
            });
        },
        
        render: function () {
            var super_render = this._super;
            var self = this;
            self.renderDashboard();
            // self.renderCrSrFetchDate();
            self.render_graphs();
            // var cr_sr_dashboard = QWeb.render('change_request_management.cr_sr_dashboard', {
            //     widget: self,
            // });
            $(".o_control_panel").addClass("o_hidden");
            // $(cr_sr_dashboard).prependTo(self.$el);
            // return cr_sr_dashboard
        },
        

        get_uploaded_by_administrators: function (e, record_id,category) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Uploaded Report By Administrators',
                res_model: 'uploaded_by_administrators_report',
                view_mode: 'tree',
                views: [[false, 'list']], // You can omit this line if you only have one view
                target: 'current',
                domain: [['uploaded_by.name', '=', record_id]]
            });
        },

        get_server_instance_report: function (event, record_id, series_name) {
            var self = this;
            console.log("Clicked category: ", record_id);
            console.log("Series name: ", series_name);
            event.stopPropagation();
            event.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Server Instance',
                res_model: 'environment_cr_service_count',
                view_mode: 'tree',
                views: [[false, 'list']],
                target: 'current',
                domain: [['environment_id.name', '=', record_id]]
            });
        },
        
        

        get_working_in_number_of_projects: function (e,uploadedby) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: ' Working In No. of Projects ',
                res_model: 'server_admin_projects',
                view_mode: 'tree',
                views: [[false, 'list']], // You can omit this line if you only have one view
                target: 'current',
                domain: [['uploaded_by.name', '=',uploadedby]]
            });
        },

        get_working_total_number_of_projects_by_server_admin: function (e,record_id) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: ' Working Total Projects By Server Admin',
                res_model: 'working_projects_details_by_server_admin',
                view_mode: 'tree',
                views: [[false, 'list']], // You can omit this line if you only have one view
                target: 'current',
                domain: [['uploaded_by', '=',record_id]]
            });
        },

        get_project_wise_cr_sr: function (e,record_id) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Project Wise CR SR',
                res_model: 'project_wise_cr_sr_report',
                view_mode: 'tree',
                views: [[false, 'list']], // You can omit this line if you only have one view
                target: 'current',
                domain: [['project_id', '=',record_id]]
            });
        },

        get_time_phase_wise_cr_sr: function (e,record_id) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Time Phase Wise CR & SR',
                res_model: 'time_range_wise_cr_sr_report',
                view_mode: 'tree',
                views: [[false, 'list']], // You can omit this line if you only have one view
                target: 'current',
                // domain: [['morning_cr_count', '=', record_id]]
            });
        },
        
        get_day_wise_cr_sr: function (e,record_id) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Day Wise CR & SR',
                res_model: 'day_wise_cr_sr_report',
                view_mode: 'tree',
                views: [[false, 'list']], 
                target: 'current',
                domain: [['uploaded_date','=',record_id]]

            });
        },
        
        
        
        render_graphs: function(){
            var self = this;
            self.render_uploaded_by_cr_sr_container_graph();
            self.render_server_instance_cr_sr_container_graph();
            self.render_working_in_total_projects_container_graph();
            self.render_working_total_projects_by_server_admin_container_graph();
            self.render_project_wise_cr_sr_container_graph();
            self.render_time_range_of_the_day_container_graph();
            self.render_day_wise_staticstis_container_graph();
            
        },

        renderDashboard: async function () {
            var self = this;
            self.$el.find('.uploaded-by-filter-wrapper,.project-wise-filter-wrapper,.day-wise-statictics-wrapper').css('display', 'none');

            self.$el.find('#uploaded-by-filter').click(function () {

            self.$el.find('.uploaded-by-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_uploaded_by_filter,#filter-uploaded-by-administrator').click(function () {
                self.$el.find('.uploaded-by-filter-wrapper').css('display', 'none');
            });

            self.$el.find('#project-wise-filter').click(function () {

            self.$el.find('.project-wise-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_project_wise_filter,#filter-project-wise').click(function () {
                self.$el.find('.project-wise-filter-wrapper').css('display', 'none');
            });

            self.$el.find('#day-wise-filter').click(function () {

            self.$el.find('.day-wise-statictics-wrapper').css('display', '');
            });
            self.$el.find('#close_day_wise_filter,#filter-day-wise').click(function () {
                self.$el.find('.day-wise-statictics-wrapper').css('display', 'none');
            });

            return true;
        },

        // renderCrSrFetchDate: function() {
        //     var self = this;
        //     return this._rpc({
        //         model: 'cr_sr_dashboard',
        //         // method: 'get_month_year_list',
        //         // args: [{'a':'b'}],
        //         // kwargs: {},
        //         context: self.getContext(),
        //     }).then(function(result) {
        //     });
        // },
        
        render_uploaded_by_cr_sr_container_graph: async function (status) {
            var self = this;
            var parameters = {}
            
            // Populate year dropdown with the last 5 years
            var currentYear = new Date().getFullYear();
            var yearsSelect = document.getElementById("upload-years-select");
            yearsSelect.innerHTML = ""; // Clear previous options
            for (var i = 0; i < 5; i++) {
                var yearOption = document.createElement("option");
                yearOption.value = currentYear - i;
                yearOption.text = currentYear - i;
                yearsSelect.appendChild(yearOption);
            }

            // Populate month dropdown with month names
            var monthsSelect = document.getElementById("upload-months-select");
            monthsSelect.innerHTML = ""; // Clear previous options
            var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            months.forEach(function(month, index) {
                var monthOption = document.createElement("option");
                var monthIndex = (index + 1).toString().padStart(2, "0"); // Pad single-digit months with a leading zero
                monthOption.value = monthIndex;
                monthOption.text = month;
                monthsSelect.appendChild(monthOption);
            });
            
            if (status == 'filter') parameters = {'current_year': self.uploadYearselect,'current_month': self.uploadMonthSelect}
            var defofferdata = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'uploaded_by_cr_sr_count',
                args: [parameters]
            });

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('cr_sr_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }

            var categories = defofferdata.map(item => item.uploaded_by);
            var CrdData = defofferdata.map(item => item.cr_count);
            var SrdData = defofferdata.map(item => item.service_count);

            var currentYearLabel = ""; // Default to empty string
            // Check if current financial year data is being displayed
            if (defofferdata.length > 0 && defofferdata[0].is_current_financial_year) {
                currentYearLabel = ' (Current Financial Year)'; // Set label if it's the current financial year
            }

            Highcharts.chart('cr_sr_container', {
                chart: {
                    type: 'column',
                    options3d: {
                        enabled: true,
                        alpha: 45
                    }
                },
                title: {
                    text: 'Uploaded By Administrators' + currentYearLabel,
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
                        groupPadding: 0.2 ,// Adjust this value as needed
                        pointWidth: 30 ,// Adjust this value as needed

                        pointPadding: 0.2,
                        borderWidth: 0,
                        depth: 35, // Set the depth for the 3D effect

                        dataLabels: {
                            enabled: true,
                            format: '{y}', // Display y value (data) on top of each bar
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        events: {
                            click: function (event) {

                                self.get_working_total_number_of_projects_by_server_admin(event, event.point.category, event.point.series.name ); 
                            }
                        },
                        groupPadding: 0.39 // Adjust the value to control the amount of overlapping (between 0 and 1)
                    }
                },
                
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'CR',
                        data: CrdData,
                    },
                    {
                        name: 'SR',
                        data: SrdData,
                    }
                ],
                colors: [
                    '#B2B2B2', '#FF6633',
                ],
            });

        },
        
        render_server_instance_cr_sr_container_graph: async function () {
            var self = this;
            var defofferdata = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'server_instance_cr_sr_count'
            });

        
            // Aggregate data by environment_id and sum up counts for each environment
            var aggregatedData = {};
            defofferdata.forEach(function (item) {
                if (!aggregatedData[item.environment_id]) {
                    aggregatedData[item.environment_id] = {
                        cr_count: 0,
                        service_count: 0
                    };
                }
                aggregatedData[item.environment_id].cr_count += item.cr_count;
                aggregatedData[item.environment_id].service_count += item.service_count;
            });
        
            var categories = Object.keys(aggregatedData);
            var colors = ['#4D8066', '#FF6633', '#3366CC', '#00BFFF', '#FFCC00', '#ADFF2F', '#9966CC'];
            
            var seriesData = [];
            categories.forEach(function (category,index) {
                var crCount = aggregatedData[category].cr_count;
                var serviceCount = aggregatedData[category].service_count;
        
                if (crCount > 0) {
                    seriesData.push({
                        name: category + ' (CR)',
                        y: crCount,
                        color: colors[index % colors.length] // Assign color based on index

                        // color: colors[4]
                    });
                }
                if (serviceCount > 0) {
                    seriesData.push({
                        name: category + ' (Service)',
                        y: serviceCount,
                        color: colors[index % colors.length] // Assign color based on index

                        // color: colors[3]
                    });
                }
            });
        
            Highcharts.chart('server_instance_cr_sr_container', {
                chart: {
                    type: 'pie',
                    options3d: {
                        enabled: true,
                        alpha: 45
                    }
                },
                title: {
                    text: 'Server Instance',
                    align: 'center'
                },
                accessibility: {
                    description: 'Server Instance Ratio'
                },

                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        allowPointSelect: true,
                        showInLegend: true,
                        innerSize: '50%', // Adjust the inner radius
                        depth: 35, // Set the depth for the 3D effect
                        dataLabels: {
                            enabled: true,
                            format: '{point.name}: {point.y}', // Display name and y value (data) on each slice
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        // animation: {
                        //     duration: 1000, // Customize the entrance animation duration
                        //     easing: 'easeOutBounce' // Choose any easing function you like
                        // }
        
                    }
                },
                credits: {
                    enabled: false
                },
                legend: {
                    align: 'right',
                    verticalAlign: 'bottom',
                    layout: 'horizontal',
                    itemMarginTop: 5, // Add space between legend items
                    labelFormatter: function () {
                        return this.name; // To display legend with category name and type (CR/Service)
                    }
                },
                series: [{
                    name: 'Count',
                    colorByPoint: true,
                    data: seriesData,
                    point: {
                        events: {
                            click: function (event) {
                                var category = event.point.name.split(' ')[0]; // Extracting category from the point name
                                self.get_server_instance_report(event, category);
                            }
                            
                            
                        }
                    }
                }],
                colors: colors
            });
        },
        
        
        

        render_working_in_total_projects_container_graph: async function () {
            var self = this;
           
            var defofferdata = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'working_in_total_no_of_projects'
            })
            var categories = defofferdata.map(item => item.uploaded_by);
            var ProjectData = defofferdata.map(item => item.project_count);

            Highcharts.chart('working_projects_count_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Working In Number of Projects ',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    labels:{
                        rotation: -90
                    },
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
                            format: '{y}',
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        events: {
                            click: function (event) {
                                self.get_working_in_number_of_projects(event, event.point.category, event.point.series.name); 
                            }
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'No Of Projects',
                        data: ProjectData
                    },
                    // {
                    //     name: 'SR',
                    //     data: SrdData
                    // },
                                       
                ],
                colors: [
                   '#00BFFF','#FF6633',
                ],
            });
        },

        render_working_total_projects_by_server_admin_container_graph: async function () {
            var self = this;
            var defofferdata = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'working_in_total_projects_by_serveradmin'
            })
            var categories = defofferdata.map(item => item.uploaded_by);
            var CrdData = defofferdata.map(item => item.cr_count);
            var SrdData = defofferdata.map(item => item.service_count);

            var colors = ['#4D8066', '#FF6633', '#3366CC', '#9933CC', '#FFCC00'];
            
            Highcharts.chart('working_projects_by_server_admin_count_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Working Total Projects By Server Admin ',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    labels:{
                        rotation: -90
                    },
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
                            format: '{y}',
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        events: {
                            click: function (event) {
                                self.get_working_total_number_of_projects_by_server_admin(event, event.point.category, event.point.series.name); 
                            }
                        }
                    }
                },
                // tooltip: {
                //     formatter: function () {
                //         return '<b>' + this.x + '</b><br/>' +
                //             this.series.name + ': ' + this.y + '<br/>' +
                //             'Project Name: ' + this.point.project_name; // Update to match your field name
                //     }
                // },
                
                credits: {
                    enabled: false
                },
                series: [
                    
                    {
                        name: 'CR',
                        data: CrdData,
                        color: colors[4]
                        
                    },

                    {
                        name: 'SR',
                        data: SrdData,
                        color: colors[2]
        
                    },
                                       
                ],
                colors: [
                    colors
                ],
            });
        },

        render_project_wise_cr_sr_container_graph: async function (status) {
            var self = this;

            var parameters = {}

            // Populate year dropdown with the last 5 years
            var currentYear = new Date().getFullYear();
            var yearsSelect = document.getElementById("project-years-select");
            yearsSelect.innerHTML = ""; // Clear previous options
            for (var i = 0; i < 5; i++) {
                var yearOption = document.createElement("option");
                yearOption.value = currentYear - i;
                yearOption.text = currentYear - i;
                yearsSelect.appendChild(yearOption);
            }

            // Populate month dropdown with month names
            var monthsSelect = document.getElementById("project-months-select");
            monthsSelect.innerHTML = ""; // Clear previous options
            var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            months.forEach(function(month, index) {
                var monthOption = document.createElement("option");
                var monthIndex = (index + 1).toString().padStart(2, "0"); // Pad single-digit months with a leading zero
                monthOption.value = monthIndex;
                monthOption.text = month;
                monthsSelect.appendChild(monthOption);
            });
            if (status == 'filter') parameters = {'current_year': self.projectYearselect,'current_month': self.projectMonthSelect}

            var proj_data = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'top_project_cr_sr_count',
                args: [parameters]
            });

            if (proj_data.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('project_wise_cr_sr_count_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            

            var categories = proj_data.map(item => item.project_name);
            var CrdData = proj_data.map(item => item.cr_count);
            var SrdData = proj_data.map(item => item.sr_count);
            Highcharts.chart('project_wise_cr_sr_count_container', {
                chart: {
                    type: 'bar' 
                },
                title: {
                    text: 'Project Wise CR SR',
                    align: 'center'
                },
                xAxis: {
                    categories: categories, 
                    title: {
                        text: 'Projects',
                        style: {
                            fontWeight: 'bold'
                        } 
                    }

                   
                },
                yAxis: {
                    title: {
                        text: 'Count', 
                        style: {
                            fontWeight: 'bold' 
                        }
                    }
                   
                },
                plotOptions: {
                    bar: {
                        dataLabels: {
                            enabled: true,
                            format: '{y}',
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        events: {
                            click: function (event) {
                                self.get_project_wise_cr_sr(event, event.point.category, event.point.series.name); 
                            }
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'CR',
                        data: CrdData
                    },
                    {
                        name: 'SR',
                        data: SrdData
                    },
                ],
                colors: [
                   '#00BFFF','#FF6633',
                ],
            });
            
        },

        render_time_range_of_the_day_container_graph: async function () {
            var self = this;
            var defofferdata = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'time_range_of_the_day_cr_sr_count'
            })
            var categories = defofferdata.map(item => item.time_period);
           
            var CrData = defofferdata.map(item => item.cr_count);
            var SrdData = defofferdata.map(item => item.sr_count);

            
            Highcharts.chart('time_range_of_the_day_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Parts Of the Day',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
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
                        stacking: 'normal',
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{y}',
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        events: {
                            click: function (event) {
                                self.get_time_phase_wise_cr_sr(event, event.point.category, event.point.series.name); 
                            }
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'CR',
                        data: CrData
                    },
                    {
                        name: 'SR',
                        data: SrdData
                    },
                                       
                ],
                colors: [
                   '#FFCC00','#3366CC',
                ],
            });
        },

        render_day_wise_staticstis_container_graph: async function (status) {
            var self = this;

            var parameters = {}

            // Populate year dropdown with the last 5 years
            var currentYear = new Date().getFullYear();
            var yearsSelect = document.getElementById("day-wise-years-select");
            yearsSelect.innerHTML = ""; // Clear previous options
            for (var i = 0; i < 5; i++) {
                var yearOption = document.createElement("option");
                yearOption.value = currentYear - i;
                yearOption.text = currentYear - i;
                yearsSelect.appendChild(yearOption);
            }

            // Populate month dropdown with month names
            var monthsSelect = document.getElementById("day-wise-months-select");
            monthsSelect.innerHTML = ""; // Clear previous options
            var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            months.forEach(function(month, index) {
                var monthOption = document.createElement("option");
                var monthIndex = (index + 1).toString().padStart(2, "0"); // Pad single-digit months with a leading zero
                monthOption.value = monthIndex;
                monthOption.text = month;
                monthsSelect.appendChild(monthOption);
            });
            if (status == 'filter') parameters = {'current_year': self.daywiseYearselect,'current_month': self.daywiseMonthSelect}
            console.log('current_year',self.daywiseYearselect)
            console.log('current_month',self.daywiseMonthSelect)

            var defofferdata = await this._rpc({
                model: 'cr_sr_dashboard',
                method: 'day_wise_staticstis_cr_sr_count',
                args: [parameters] 
            })

            if (defofferdata.length === 0) {
                // If no data is available, display a message
                var container = document.getElementById('day_wise_staticstis_container');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';
                return;
            }
            var categories = defofferdata.map(item => item.upload_date);
           
            var CrData = defofferdata.map(item => item.cr_count);
            var SrdData = defofferdata.map(item => item.sr_count);

            Highcharts.chart('day_wise_staticstis_container', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Day-wise staticstis',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    labels: {
                        rotation: -45
                    },
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
                            format: '{y}',
                            style: {
                                fontWeight: 'bold'
                            }
                        },
                        events: {
                            click: function (event) {
                                self.get_day_wise_cr_sr(event, event.point.category, event.point.series.name); 
                            }
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'CR',
                        data: CrData
                    },
                    {
                        name: 'SR',
                        data: SrdData
                    },
                                       
                ],
                colors: [
                   '#ADFF2F','#3366CC',
                ],
            });
        },
        

    });

    core.action_registry.add('cr_sr_dashboard', CrSrDashboard);


});
        