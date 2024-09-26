odoo.define('kw_eos.AttritionDashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var AttritionDashboard = AbstractAction.extend({
        template: 'AttritionTableDashboard',

        start: function () {
            var self = this;
            this._super.apply(this, arguments);

            this.loadFiscalYears(); // Load fiscal years initially
            this.$('#filter-fy-button1').on('click', function () {
                self.handleFiscalYearFilter();
            });
            this.$('#filter-fy-button2').on('click', function () {
                self.JoineeResigneeFiscalYearFilter();
            });
            this.$('#apply_fiscal_year_filter').on('click', function () {
                self.GetDashboardDataAccFiscalYear();
            });
            this.loadDashboardData();
            this.loadDashboardtenureData();
            

            this.$('#fy-tenure-filter').on('click', function () {
                self.toggleFiscalYearFilterWrapper();
            });
            this.$('#fy-joinee-rejoinee-filter').on('click', function () {
                self.toggleFiscalYearFilterWrapper();
            });
            this.$('#fy-wise-filter').on('click', function () {
                self.toggleFiscalYearFilterWrapper();
            });
           
            this.$('#attrition_by_tenure_filter').on('click', function () {
                self.hideFiscalYearFilterWrapper();
            });
            this.$('#refresh_portlet1').on('click', function() {
                // Re-render the chart with the same data
                self.loadDashboardtenureData();

            });
            // Add event listener to the refresh button
            this.$('#refresh_portlet2').on('click', function() {
                // Re-render the chart with the same data
                self.loadDashboardJoineeResigneeData();

            });
            this.$('#refresh_portlet4').on('click', function() {
                // Re-render the chart with the same data
                self.loadDashboardData();

            });
            this.$('#joinee_resignee_filter').on('click', function () {
                self.hideFiscalYearFilterWrapper();
            });
            this.$('#fy_wise_filter').on('click', function () {
                self.hideFiscalYearFilterWrapper();
            });
            this.$('.fy-grade-filter-wrapper').hide();
        },

        loadDashboardData: function () {
            var self = this;
            rpc.query({
                model: 'kw_attrition_dashboard',
                method: 'get_current_fiscal_year_data',
                args: [],
            }).then(function (data) {
                self.fiscalYearStartDate = data.fiscal_year_start_date;
                self.fiscalYearEndDate = data.fiscal_year_end_date;
                self.tenure_data = data.tenure_data || {};
                // console.log('tenure data==========================',data.tenure_data,data.attrition_by_job_role,data.joiners_by_department,data.resignees_by_department)
                // console.log("Data received from server:", data);
                // console.log("Data attrition:", data.attrition_by_tenure);

                // Render general dashboard data
                self.renderDashboardValues(data);

                // If selected year and quarter are provided, load data for attrition by tenure chart
                self.renderAttritionByJobRoleChart(data.attrition_by_job_role);
                self.renderAttritionByGenderChart(data.attrition_by_gender);
                self.renderDepartmentAttrition(data.department_attrition);
                self.renderResignationReason(data.top_resignation_reasons);
                self.renderJoinersResigneesByDepartmentChart(data.joiners_by_department, data.resignees_by_department);
                self.renderVoluntaryInvoluntaryAttritionChart(data.voluntary_involuntary_attrition);
                self.renderAttritionByTenureChart(data.attrition_by_tenure);
                self.renderFYWiseJoiningExitTable(data.fy_wise_joining_exit);
            });
        },

        loadDashboardtenureData: function (selectedYear, selectedQuarter) {
            var self = this;
            rpc.query({
                model: 'kw_attrition_dashboard',
                method: 'get_dashboard_data',
                args: [],
            }).then(function (data) {
                // console.log("Data received from server:", data);
                // Render general dashboard data
                // self.renderDashboardValues(data);

                // If selected year and quarter are provided, load data for attrition by tenure chart
                if (selectedYear && selectedQuarter) {
                    // console.log('selectedYear=====================',selectedYear)
                    self.loadAttritionByTenureData(selectedYear, selectedQuarter);
                    self.hideFiscalYearFilterWrapper();
                }

            });
        },
        loadDashboardJoineeResigneeData: function (selectedYear, selectedQuarter) {
            var self = this;
            rpc.query({
                model: 'kw_attrition_dashboard',
                method: 'get_dashboard_data',
                args: [],
            }).then(function (data) {
                // console.log("Data received from server:", data);
                // Render general dashboard data
                // self.renderDashboardValues(data);

                // If selected year and quarter are provided, load data for attrition by tenure chart
                if (selectedYear && selectedQuarter) {
                    self.loadJoineeResigneeData(selectedYear, selectedQuarter);
                    self.hideFiscalYearFilterWrapper();
                }

            });
        },
        loadDashboardDataAccFiscalyear: function (selectedYear) {
            var self = this;
            rpc.query({
                model: 'kw_attrition_dashboard',
                method: 'get_selected_fiscal_year_data',
                args: [selectedYear],
            }).then(function (data) {
                // console.log("attrition by gender data=====================",data.attrition_by_gender)
                self.fiscalYearStartDate = data.fiscal_year_start_date;
                self.fiscalYearEndDate = data.fiscal_year_end_date;
                self.tenure_data = data.tenure_data || {};
                self.renderDashboardValues(data);
                self.renderAttritionByGenderChart(data.attrition_by_gender);
                self.renderAttritionByJobRoleChart(data.attrition_by_job_role);
                self.renderDepartmentAttrition(data.department_attrition);
                self.renderResignationReason(data.top_resignation_reasons);
                self.renderJoinersResigneesByDepartmentChart(data.joiners_by_department, data.resignees_by_department);
                self.renderVoluntaryInvoluntaryAttritionChart(data.voluntary_involuntary_attrition);
                self.renderAttritionByTenureChart(data.attrition_by_tenure);
                self.hideFiscalYearFilterWrapper();

            });
        },
      
        loadJoineeResigneeData: function (selectedYear, selectedQuarter) {
            var self = this;
            rpc.query({
                model: 'kw_attrition_dashboard',
                method: 'get_joinee_resignee_attrition_data',
                args: [selectedYear, selectedQuarter],
            }).then(function (data) {
                // console.log("Attrition by tenure data received from server:", data);
                // Render attrition by tenure chart
                self.renderJoinersResigneesByDepartmentChart(data.joiners_by_department,data.resignees_by_department);
            });
        },
        

        loadAttritionByTenureData: function (selectedYear, selectedQuarter) {
            var self = this;
            rpc.query({
                model: 'kw_attrition_dashboard',
                method: 'get_attrition_by_tenure_data',
                args: [selectedYear, selectedQuarter],
            }).then(function (data) {
                // console.log("Attrition by tenure data received from server:", data);
                // Render attrition by tenure chart
                self.renderAttritionByTenureChart(data.attrition_by_tenure);
                self.tenure_data = data.tenure_data || {};

            });
        },
        

        renderDashboardValues: function (data) {
            var self = this;
            // Render dashboard values
            self.$('.dashboard-value[data-field="employee_count"]').each(function (index, element) {
                $(element).text(data.employee_count || 0);
                $(element).on('click', function () {
                    self.openEmployeeCountTreeView();
                });
            });
            self.$('.dashboard-value[data-field="employee_count_as_of_april"]').each(function (index, element) {
                $(element).text(data.employee_count_as_of_april || 0);
                $(element).on('click', function () {
                    self.openEmployeeCountAsOnAprilTreeView();
                });
                
            });
            self.$('.dashboard-value[data-field="attrition_count"]').each(function (index, element) {
                $(element).text(data.attrition_count || 0);
                $(element).on('click', function () {
                    self.openEmployeeAttritionCountTreeView();
                });
            });
            self.$('.dashboard-value[data-field="average_tenure"]').each(function (index, element) {
                $(element).text(data.average_tenure || 0);
            });
            self.$('.dashboard-value[data-field="attrition_rate"]').each(function (index, element) {
                var attritionRate = data.attrition_rate ? parseFloat(data.attrition_rate).toFixed(1) : '0.0';
                $(element).text(attritionRate + '%');
            });
            
        },

        toggleFiscalYearFilterWrapper: function () {
            var wrapper = this.$('.fy-grade-filter-wrapper');
            if (wrapper.is(':visible')) {
                wrapper.hide();
            } else {
                this.loadFiscalYears(); // Load fiscal years when the wrapper is shown
                wrapper.show();
            }
        },
        hideFiscalYearFilterWrapper: function () {
            // Hide fiscal year filter wrapper
            var wrapper = this.$('.fy-grade-filter-wrapper');
            wrapper.hide();
        },

        loadFiscalYears: function () {
            var self = this;
            rpc.query({
                route: '/get_available_fiscal_years',
                params: {},
            }).then(function (result) {
                var fiscalYears = result.fiscal_years || [];
                self.populateFiscalYears(fiscalYears, '#filter-fy-select2');
                self.populateFiscalYears(fiscalYears, '#filter-fy-select3');
                self.populateFiscalYears(fiscalYears, '#filter-fy-select4');
            });
        },
        
        populateFiscalYears: function (fiscalYears, filterId) {
            var select = this.$(filterId);
            select.empty();
            fiscalYears.forEach(function (fy) {
                select.append($('<option>', {
                    value: fy,
                    text: fy
                }));
            });
        },
        JoineeResigneeFiscalYearFilter: function () {
            var selectedYear = $('#filter-fy-select3').val();
            var selectedQuarter = $('#filter-quarter-select1').val();

            this.loadDashboardJoineeResigneeData(selectedYear,selectedQuarter);
        },

        GetDashboardDataAccFiscalYear: function () {
            var selectedYear = $('#filter-fy-select4').val();

            this.loadDashboardDataAccFiscalyear(selectedYear);
        },

        handleFiscalYearFilter: function () {
            var selectedYear = $('#filter-fy-select2').val();
            var selectedQuarter = $('#filter-quarter-select').val();

            this.loadDashboardtenureData(selectedYear,selectedQuarter);
        },

        openEmployeeCountTreeView: function (domains) {
            var self = this;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'],
            }).then(function (view_id) {
            self.do_action({
                name: _t("Total Employee"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[view_id, 'list']],
                domain: [
                         '&','&','&',['date_of_joining','<=',self.fiscalYearEndDate],['last_working_day', '=',false],['employement_type.code', '!=', 'O'],['company_id','=',1],],
                context: {'create': 0,'edit': 0},
                target: 'current',
            });
            });
            // console.log('start=============',this.fiscalYearStartDate,this.fiscalYearEndDate)
        },
        openEmployeeCountAsOnAprilTreeView: function (domains) {
            var self = this;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'],
            }).then(function (view_id) {
            self.do_action({
                name: _t("Total Employee"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[view_id, 'list']],
                domain: ['&','&','&',['date_of_joining','<=',self.fiscalYearStartDate],['last_working_day', '=',false],['employement_type.code', '!=', 'O'],['company_id','=',1],],
                context: {'create': 0,'edit': 0},
                target: 'current',
            });
            });
            // console.log('start=============',this.fiscalYearStartDate,this.fiscalYearEndDate)
        },

        openEmployeeAttritionCountTreeView: function (domains) {
            var self = this;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'], // Adjust 'your_module' to the appropriate module name
            }).then(function (view_id) {
                self.do_action({
                    name: _t("Attrition Count"),
                    type: 'ir.actions.act_window',
                    res_model: 'hr.employee',
                    view_mode: 'tree',
                    views: [[view_id, 'list']],
                    domain: [['active','=',false],['last_working_day', '>=', self.fiscalYearStartDate],['last_working_day', '<=', self.fiscalYearEndDate],['employement_type.code', '!=', 'O'],['company_id','=',1]],
                    context: {'create': 0,'edit': 0},
                    target: 'current',
                });
            });
        },
        

        openEmployeeActiveCountTreeView: function (domains) {
            this.do_action({
                name: _t("Active Employee"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[false, 'list']],
                domain: [['active','=',true]],
                context: {'create': 0,'edit': 0},
                target: 'current',
            });
        },

        renderAttritionByGenderChart: function (attritionByGenderData) {
            var self = this; // Store the current context
            if (attritionByGenderData && attritionByGenderData.length > 0) {
                var customColors = ['#6B5B95', '#119620'];
                var icons = {
                    'Male': 'kw_eos/static/img/male.png',
                    'Female': 'kw_eos/static/img/female.png'
                };
        
                Highcharts.chart('attrition_by_gender_container', {
                    chart: {
                        type: 'pie',
                        events: {
                            load: function () {
                                updateIcons(this);
                            },
                            redraw: function () {
                                updateIcons(this);
                            }
                        }
                    },
                    title: {
                        text: 'Attrition by Gender',
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    tooltip: {
                        pointFormat: '<b>{point.name}: {point.percentage:.1f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            showInLegend: true,
                            innerSize: '50%',
                            dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}:</b> {point.percentage:.1f} %',
                                style: {
                                    color: 'black'
                                }
                            }
                        }
                    },
                    series: [{
                        name: 'Attrition',
                        colorByPoint: true,
                        data: attritionByGenderData.map(function (item, index) {
                            return {
                                name: item.name,
                                y: item.y,
                                color: customColors[index % customColors.length]
                            };
                        }),
                        point: {
                            events: {
                                click: function (e) {
                                    var gender = this.name === 'Male' ? 'male' : 'female';
                                    self.gender_wise_emp_attrition(gender);
                                }
                            }
                        }
                    }]
                });
        
                function updateIcons(chart) {
                    var totalWidth = chart.chartWidth;
                    var totalHeight = chart.chartHeight;
                    var iconSize = Math.min(totalWidth, totalHeight) * 0.3; // Increased icon size to 30%
                    var iconMargin = 10; // Margin between icon and text
                    var xPos = totalWidth - iconSize - iconMargin; // Same xPos for both icons
        
                    // Clear existing elements before adding new ones
                    if (chart.customElements) {
                        chart.customElements.forEach(function (element) {
                            element.destroy();
                        });
                    }
                    chart.customElements = [];
        
                    // Add Male icon and text below
                    var yPosMale = totalHeight * 0.1;
                    var maleIcon = chart.renderer.image(icons['Male'], xPos, yPosMale, iconSize, iconSize).add();
                    var maleText = chart.renderer.text(attritionByGenderData[0].y.toFixed(1) + '%', xPos + iconSize / 2, yPosMale + iconSize + 15)
                        .css({ color: '#6B5B95', fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }).add();
                    var maleLabel = chart.renderer.text('Male', xPos + iconSize / 2, yPosMale + iconSize + 35)
                        .css({ color: '#6B5B95', fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }).add();
        
                    // Add Female icon and text below
                    var yPosFemale = totalHeight * 0.6;
                    var femaleIcon = chart.renderer.image(icons['Female'], xPos, yPosFemale, iconSize, iconSize).add();
                    var femaleText = chart.renderer.text(attritionByGenderData[1].y.toFixed(1) + '%', xPos + iconSize / 2, yPosFemale + iconSize + 20)
                        .css({ color: '#119620', fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }).add();
                    var femaleLabel = chart.renderer.text('Female', xPos + iconSize / 2, yPosFemale + iconSize + 40)
                        .css({ color: '#119620', fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }).add();
        
                    // Store references to custom elements
                    chart.customElements = [maleIcon, maleText, maleLabel, femaleIcon, femaleText, femaleLabel];
                }
            } else {
                $('#attrition_by_gender_container').text('No data available.');
            }
        },        
        
        gender_wise_emp_attrition: function (gender) {
            var self = this;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'], // Adjust 'your_module' to the appropriate module name
            }).then(function (view_id) {
            self.do_action({
                name: _t("Attrition By Gender"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[view_id, 'list']],
                domain: [
                    ['gender', '=', gender],
                    ['active', '=', false],
                    ['last_working_day', '>=', self.fiscalYearStartDate],
                    ['last_working_day', '<=', self.fiscalYearEndDate],
                    ['employement_type.code', '!=', 'O'],
                    ['company_id','=',1]
                ],
                context: {'create': 0, 'edit': 0},
                target: 'current',
            });
        });
        },
        renderDepartmentAttrition: function (departmentAttritionData) {
            var container = $('#department_attrition_container');
            container.empty();
        
            if (departmentAttritionData && departmentAttritionData.length > 0) {
                const attritionColor = '#FF0000'; // Red for Attrition
                const departmentColors = [
                    '#1E90FF', // DodgerBlue
                    '#32CD32', // LimeGreen
                    '#FFD700', // Gold
                    '#6A5ACD', // SlateBlue
                    '#2E8B57', // SeaGreen
                    '#DAA520'  // GoldenRod
                ];
        
                var categories = [];
                var totalData = [];
                var attritionData = [];
        
                departmentAttritionData.forEach(function(item, index) {
                    categories.push(item.department);
                    totalData.push({
                        y: item.total_count || 0, // Total employees in the department
                        color: departmentColors[index % departmentColors.length] // Unique color for each department
                    });
                    attritionData.push({
                        y: item.attrition_count || 0, // Attrition count
                        color: attritionColor // Fixed color for Attrition (Red)
                    });
                });
        
                Highcharts.chart('department_attrition_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Department-wise Attrition',
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    xAxis: {
                        categories: categories,
                        title: {
                            text: 'Departments'
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
                        },
                        stackLabels: {
                            enabled: true,
                            style: {
                                fontWeight: 'bold',
                                color: (Highcharts.defaultOptions.title.style && Highcharts.defaultOptions.title.style.color) || 'gray'
                            }
                        }
                    },
                    tooltip: {
                        pointFormat: '<b>{point.y}</b>'
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            dataLabels: {
                                enabled: true,
                                format: '{point.y}',
                                style: {
                                    color: 'black'
                                }
                            },
                            point: {
                                events: {
                                    click: function (event) {
                                        var deptName = event.point.category;
                                        this.department_wise_emp_attrition(deptName, event.point.color === attritionColor);
                                    }.bind(this) // Bind the current context to the event handler
                                }
                            }
                        }
                    },
                    series: [{
                        name: 'Total Employees',
                        data: totalData
                    }, {
                        name: 'Attrition',
                        data: attritionData,
                        color: attritionColor // Red for Attrition
                    }]
                });
            } else {
                container.append('<div>No data available.</div>');
            }
        },
        
        department_wise_emp_attrition: function (DeptName, isAttrition) {
            var self = this;
            var domain = [['department_id.name', '=', DeptName]];
            if (isAttrition) {
                domain.push(['active', '=', false],['last_working_day', '>=', self.fiscalYearStartDate],['last_working_day', '<=', self.fiscalYearEndDate],['employement_type.code', '!=', 'O'],['company_id','=',1]);
            } else {
                domain.push(['active', '=', true],['employement_type.code', '!=', 'O'],['company_id','=',1]);
            }
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'],
            }).then(function (view_id) {
            self.do_action({
                name: _t("Departmentwise Attrition"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[view_id, 'list']],
                domain: domain,
                context: {'create': 0, 'edit': 0},
                target: 'current',
            });
        });
        },
        
        

        renderResignationReason: function (jobRoleAttritionData) {
            var container = $('#job_role_attrition_container');
            container.empty();
        
            if (jobRoleAttritionData && jobRoleAttritionData.length > 0) {
                Highcharts.chart('job_role_attrition_container', {
                    chart: {
                        type: 'pie',
                        options3d: {
                            enabled: true,
                            alpha: 45,
                            beta: 0
                        }
                    },
                    title: {
                        text: 'Reasons for Attrition',
                        style: {
                            fontWeight: 'bold' , // Setting the fontWeight to bold
                            fontSize:'20px'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        pie: {
                            innerSize: 100,
                            depth: 45,
                            dataLabels: {
                                enabled: true,
                                format: '{point.name}: {point.y}'
                            },
                            events: {
                                click: function (event) {
                                    // Redirect to the Odoo list view with appropriate domain filter
                                    var reason = event.point.name;
                                    // console.log('============reason', reason);
                                    this.attrition_by_resignation_reason(reason); // Call the redirection function with the reason
                                }.bind(this) // Bind the current context to the event handler
                            }
                        }
                    },
                    series: [{
                        name: 'Attrition Count',
                        data: jobRoleAttritionData.map(function(item) {
                            return { name: item.job_role, y: item.attrition_count };
                        })
                    }]
                });
            } else {
                container.append('<div>No data available.</div>');
            }
        },
        attrition_by_resignation_reason: function (reason) {
            var self = this;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree_reason'], // Ensure the module name is correct
            }).then(function (view_id) {
                self.do_action({
                    name: _t("Resignation Reason"),
                    type: 'ir.actions.act_window',
                    res_model: 'hr.employee',
                    view_mode: 'tree',
                    views: [[view_id, 'list']],
                    domain: [
                        ['active', '=', false], 
                        ['resignation_reason.name', '=', reason],
                        ['last_working_day', '>=', self.fiscalYearStartDate], // Corrected 'this' to 'self'
                        ['last_working_day', '<=', self.fiscalYearEndDate],  // Corrected 'this' to 'self'
                        ['employement_type.code', '!=', 'O'],
                        ['company_id', '=', 1]
                    ],
                    context: {'create': 0, 'edit': 0},
                    target: 'current',
                });
            });
        },
        
        

        renderJoinersResigneesByDepartmentChart: function (joinersData, resigneesData, period) {
            var self = this;
        
            var departments = [];
            var joinersCount = [];
            var resigneesCount = [];
        
            var joinersColor = '#1f77b4'; // Blue color for joiners
            var resigneesColor = '#ff7f0e'; // Orange color for resignees
        
            var groupedJoinersData = {};
            var groupedResigneesData = {};
        
            // Group joiners data by department and period
            joinersData.forEach(function (item) {
                var key = item.department + ' - ' + item.period;
                if (!groupedJoinersData[key]) {
                    groupedJoinersData[key] = 0;
                }
                groupedJoinersData[key] += item.count;
            });
        
            // Group resignees data by department and period
            resigneesData.forEach(function (item) {
                var key = item.department + ' - ' + item.period;
                if (!groupedResigneesData[key]) {
                    groupedResigneesData[key] = 0;
                }
                groupedResigneesData[key] += item.count;
            });
        
            // Combine keys from both joiners and resignees data
            var allKeys = Object.keys(groupedJoinersData).concat(Object.keys(groupedResigneesData));
            allKeys = Array.from(new Set(allKeys)).sort();
        
            // Iterate through each key and populate departments, joinersCount, and resigneesCount arrays
            allKeys.forEach(function (key) {
                var joinersCountValue = groupedJoinersData[key] || 0;
                var resigneesCountValue = groupedResigneesData[key] || 0;
        
                if (joinersCountValue !== 0 || resigneesCountValue !== 0) { // Exclude columns with zero count for both joiners and resignees
                    var [department, period] = key.split(' - ');
        
                    departments.push(key);
                    joinersCount.push({
                        y: joinersCountValue,
                        color: joinersColor,
                        department: department,
                        period: period
                    });
                    resigneesCount.push({
                        y: -resigneesCountValue,
                        color: resigneesColor,
                        department: department,
                        period: period
                    });
                }
            });
        
            // Create the chart using Highcharts
            Highcharts.chart('join_and_attrition_by_department', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Department Wise Joinee / Resignee',
                    style: {
                        fontWeight: 'bold',
                        fontSize: '20px'
                    }
                },
                credits: {
                    enabled: false
                },
                xAxis: {
                    categories: departments,
                    crosshair: true
                },
                yAxis: {
                    title: {
                        text: 'Count'
                    },
                    plotLines: [{
                        color: 'red',
                        width: 1,
                        value: 0
                    }]
                },
                tooltip: {
                    formatter: function () {
                        var tooltipText = '<b>' + this.x + '</b><br/>';
                        if (this.points && this.points.length > 0) {
                            this.points.forEach(function (point) {
                                var count = Math.abs(point.y);
                                tooltipText += '<span style="color:' + point.color + '">\u25CF</span> ' + point.series.name + ': ' + count + '<br/>';
                            });
                        }
                        return tooltipText;
                    },
                    shared: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            formatter: function () {
                                if (Math.abs(this.y) !== 0) {
                                    // Use a consistent black color for the department name
                                    return '<span style="color:black;">' + this.point.category.split(' - ')[0] + '</span><br/>' + Math.abs(this.y);
                                }
                                return null;
                            }
                        }
                    }
                },
                series: [{
                    name: 'Joinees',
                    data: joinersCount,
                    color: joinersColor  // Apply the same color for all joiners
                }, {
                    name: 'Resignees',
                    data: resigneesCount,
                    color: resigneesColor  // Apply the same color for all resignees
                }]
            }, function (chart) {
                // Add onclick event to each category (department)
                chart.series.forEach(function (series) {
                    series.data.forEach(function (point) {
                        point.graphic.element.onclick = function () {
                            var department = point.department;
                            var period = point.period;
                            var isActive = series.name === 'Joinees';
                            var domain = [];
        
                            if (isActive) {
                                domain.push(['active', '=', true]);
                                domain.push(['department_id', '=', department]);
                                if (period) {
                                    var [quarter, year] = period.split(' ');
                                    var [startDate, endDate] = self.getQuarterDates(quarter, year);
        
                                    domain.push(['date_of_joining', '>=', startDate]);
                                    domain.push(['date_of_joining', '<=', endDate]);
                                    domain.push(['employement_type.code', '!=', 'O']);
                                    domain.push(['company_id', '=', 1]);
                                }
                            } else {
                                domain.push(['active', '=', false]);
                                domain.push(['department_id', '=', department]);
                                if (period) {
                                    var [quarter, year] = period.split(' ');
                                    var [startDate, endDate] = self.getQuarterDates(quarter, year);
        
                                    domain.push(['last_working_day', '>=', startDate]);
                                    domain.push(['last_working_day', '<=', endDate]);
                                    domain.push(['employement_type.code', '!=', 'O']);
                                    domain.push(['company_id', '=', 1]);
                                }
                            }
        
                            self.filterByDomain(domain);
                        };
                    });
                });
            });
        },
        
        
        
        getQuarterDates: function (quarter, year) {
            var quarters = {
                'Q1': ['04-01', '06-30'],
                'Q2': ['07-01', '09-30'],
                'Q3': ['10-01', '12-31'],
                'Q4': ['01-01', '03-31']
            };
            var [start, end] = quarters[quarter];
            return [`${year}-${start}`, `${year}-${end}`];
        },
        
        filterByDomain: function (domain) {
            var self = this;

            // Format dates in the domain to 'YYYY-MM-DD' format
            domain = domain.map(condition => {
                if (condition[0] === 'date_of_joining' || condition[0] === 'last_working_day') {
                    return [condition[0], condition[1], condition[2]];
                } else {
                    return condition;
                }
            });
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'], // Ensure the module name is correct
            }).then(function (view_id) {
            // console.log("Constructed Domain:", domain);
            self.do_action({
                name: _t("Employee Attrition"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[view_id, 'list']],
                domain: domain,
                context: { 'create': 0, 'edit': 0 },
                target: 'current',
            });
        });
        },
        
        
        
        renderVoluntaryInvoluntaryAttritionChart: function (voluntaryInvoluntaryData) {
            var self = this;
            if (voluntaryInvoluntaryData && Object.keys(voluntaryInvoluntaryData).length > 0) {
                var customColors = ['#FF5733', '#33FF57', '#FFBD33', '#3375FF', '#8E44AD', '#E74C3C', '#2ECC71'];
                var totalAttrition = voluntaryInvoluntaryData.voluntary + voluntaryInvoluntaryData.involuntary;
        
                // Map the data to the format expected by Highcharts
                var formattedData = [
                    {
                        name: 'Voluntary',
                        y: voluntaryInvoluntaryData.voluntary,
                        color: customColors[0]
                    }
                ];
        
                // Add the involuntary details to the data
                Object.keys(voluntaryInvoluntaryData.involuntary_details).forEach(function (key, index) {
                    formattedData.push({
                        name: key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '),
                        y: voluntaryInvoluntaryData.involuntary_details[key],
                        color: customColors[index + 1]
                    });
                });
        
                Highcharts.chart('voluntary_involuntary_attrition_container', {
                    chart: {
                        type: 'pie',
                        options3d: {
                            enabled: true,
                            alpha: 45
                        }
                    },
                    title: {
                        text: 'Voluntary vs. Involuntary Attritions<br>Total: ' + totalAttrition,
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    tooltip: {
                        pointFormat: '<b>{point.name}: {point.y}</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            showInLegend: true,
                            innerSize: '40%',
                            depth: 45,
                            dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}:</b> {point.y}',
                                style: {
                                    color: 'black'
                                }
                            },
                            point: {
                                events: {
                                    click: function (event) {
                                        var attritionType = event.point.name.toLowerCase().replace(' ', '_');
                                        self.filterByAttritionType(attritionType);
                                    }
                                }
                            }
                        }
                    },
                    series: [{
                        name: 'Attrition',
                        colorByPoint: true,
                        data: formattedData
                    }]
                });
            } else {
                $('#voluntary_involuntary_attrition_container').text('No data available.');
            }
        },
        
        
        filterByAttritionType: function (attritionType) {
            var self = this;
            
            // Define the domain based on attrition type
            var domain = [
                ['active', '=', false],
                ['last_working_day', '>=', self.fiscalYearStartDate],
                ['last_working_day', '<=', self.fiscalYearEndDate],
                ['employement_type.code', '!=', 'O'],
                ['company_id', '=', 1]
            ];
            
            if (attritionType === 'voluntary' || attritionType === 'involuntary') {
                domain.push(['attrition_type', '=', attritionType]);
            } else {
                domain.push(['involuntary_reason', '=', attritionType]);
            }
            
            // Fetch the view ID using _rpc
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_all_tree_reason'],
            }).then(function (view_id) {
                // Execute the action with the resolved view ID
                self.do_action({
                    name: _t("Employee Attrition"),
                    type: 'ir.actions.act_window',
                    res_model: 'hr.employee',
                    view_mode: 'tree',
                    views: [[view_id, 'list']],
                    domain: domain,
                    context: {'create': 0, 'edit': 0},
                    target: 'current',
                });
            });
        },
        
        renderAttritionByTenureChart: function (attritionByTenureData) {
            var self = this;
            if (attritionByTenureData && attritionByTenureData.length > 0) {
                var customColors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#33A1FF', '#A133FF', '#FFA133'];
                var tenureRanges = [
                    '0-3 months',
                    '3-6 months',
                    '6-12 months',
                    '12-24 months',
                    '24-36 months',
                    '36+ months'
                ];
        
                var formattedData = [];
                for (var i = 0; i < attritionByTenureData.length; i++) {
                    formattedData.push({
                        name: tenureRanges[i],
                        y: attritionByTenureData[i],
                        color: customColors[i % customColors.length]
                    });
                }
        
                Highcharts.chart('attrition_by_tenure_container', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Attrition by Tenure',
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    xAxis: {
                        categories: tenureRanges,
                        title: {
                            text: 'Tenure Range'
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Attrition Percentage'
                        },
                        labels: {
                            format: '{value} %'
                        }
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.y:.1f}%</b>'
                    },
                    plotOptions: {
                        column: {
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.1f} %'
                            },
                            events: {
                                click: function (event) {
                                    var tenureRange = event.point.name;
                                    self.filterByTenureRange(tenureRange); // Call the filter function with the tenure range
                                }
                            }
                        }
                    },
                    series: [{
                        name: 'Attrition',
                        data: formattedData
                    }]
                });
            } else {
                $('#attrition_by_tenure_container').text('No data available.');
            }
        },
        
        filterByTenureRange: function (tenureRange) {
            var self = this;
            var tenureRangeKey;
            switch (tenureRange) {
                case '0-3 months':
                    tenureRangeKey = '0-3';
                    break;
                case '3-6 months':
                    tenureRangeKey = '3-6';
                    break;
                case '6-12 months':
                    tenureRangeKey = '6-12';
                    break;
                case '12-24 months':
                    tenureRangeKey = '12-24';
                    break;
                case '24-36 months':
                    tenureRangeKey = '24-36';
                    break;
                case '36+ months':
                    tenureRangeKey = '36+';
                    break;
                default:
                    tenureRangeKey = null;
            }
        
            if (tenureRangeKey) {
                var employeeIds = self.tenure_data[tenureRangeKey] || [];
                var domain = [['id', 'in', employeeIds], ['active', '=', false], ['employement_type.code', '!=', 'O'], ['company_id', '=', 1]];
                // console.log("Filtering by tenure range:", tenureRange);
                // console.log("Constructed Domain:", domain);
                this._rpc({
                    model: 'ir.model.data',
                    method: 'xmlid_to_res_id',
                    args: ['kw_eos.view_hr_employee_attrition_tree'],
                }).then(function (view_id) {
                self.do_action({
                    name: _t("Employee Attrition"),
                    type: 'ir.actions.act_window',
                    res_model: 'hr.employee',
                    view_mode: 'tree',
                    views: [[view_id, 'list']],
                    domain: domain,
                    context: {'create': 0, 'edit': 0},
                    target: 'current',
                });
            });
            } else {
                console.log("Invalid tenure range:", tenureRange);
            }
        },
        

        renderFYWiseJoiningExitTable: function (fyWiseJoiningExitData) {
            var self = this; // Store the current context
            var container = $('#fy_wise_joining_exit_container');
        
            // Clear previous content
            container.empty();
        
            if (fyWiseJoiningExitData && fyWiseJoiningExitData.length > 0) {
                // Create table element with shadow
                var table = $('<table>').addClass('table table-bordered table-striped table-hover shadow');
        
                // Add table title with proper styling
                var title = $('<div>').addClass('table-title').text('FY Wise Joining & Exit');
                container.append(title);
        
                // Create table header
                var header = $('<thead>').addClass('thead-light').append($('<tr>')
                    .append('<th rowspan="2">Department</th>')
                    .append('<th colspan="2">FY 22-23</th>')
                    .append('<th colspan="2">FY 23-24</th>')
                    .append('<th colspan="2">FY 24-25</th>')
                );
        
                // Create sub-header
                header.append($('<tr>')
                    .append('<th>Joining</th>')
                    .append('<th>Exit</th>')
                    .append('<th>Joining</th>')
                    .append('<th>Exit</th>')
                    .append('<th>Joining</th>')
                    .append('<th>Exit</th>')
                );
        
                // Append header to the table
                table.append(header);
        
                // Create table body
                var tbody = $('<tbody>');
        
                // Populate table rows with data
                fyWiseJoiningExitData.forEach(function(d, index) {
                    var rowClass = index % 2 === 0 ? 'table-light' : 'table-secondary'; // Alternating row colors
                    var row = $('<tr>').addClass(rowClass)
                        .append('<td>' + d.department_name + '</td>')
                        .append('<td>' + d.fy_22_23_joining + '</td>')
                        .append('<td>' + d.fy_22_23_exit + '</td>')
                        .append('<td>' + d.fy_23_24_joining + '</td>')
                        .append('<td>' + d.fy_23_24_exit + '</td>')
                        .append('<td>' + d.fy_24_25_joining + '</td>')
                        .append('<td>' + d.fy_24_25_exit + '</td>');
        
                    tbody.append(row);
                });
        
                // Append tbody to the table
                table.append(tbody);
        
                // Append the table to the container
                container.append(table);
            } else {
                container.text('No data available.');
            }
        },
        
        
        renderAttritionByJobRoleChart: function (attritionByJobRoleData) {
            var self = this;
        
            if (attritionByJobRoleData && attritionByJobRoleData.length > 0) {
                // Sort the data by the 'y' value in descending order
                attritionByJobRoleData.sort(function (a, b) {
                    return b.y - a.y;
                });
        
                var customColors = ['#FF6F61', '#88B04B', '#009B77', '#F7CAC9', '#92A8D1', '#B565A7'];
                
                // Calculate total count
                var totalAttritionCount = attritionByJobRoleData.reduce(function (accumulator, item) {
                    return accumulator + item.y;
                }, 0);
        
                Highcharts.chart('attrition_by_job_role_container', {
                    chart: {
                        type: 'bar'
                    },
                    title: {
                        text: 'Attrition by Job Role (Total: ' + totalAttritionCount + ')', // Display the total count
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    xAxis: {
                        type: 'category',
                        title: {
                            text: 'Job Role'
                        },
                        labels: {
                            style: {
                                fontSize: '14px'
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Count'
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        pointFormat: '<b>{point.y}</b>'
                    },
                    series: [{
                        name: 'Attrition',
                        data: attritionByJobRoleData.map(function (item, index) {
                            return {
                                name: item.name,
                                y: item.y,
                                color: customColors[index % customColors.length],
                                percentage: item.percentage
                            };
                        }),
                        point: {
                            events: {
                                click: function () {
                                    var jobroleName = this.name;
                                    self.job_role_wise_emp_attrition(jobroleName);
                                }
                            }
                        }
                    }],
                    plotOptions: {
                        bar: {
                            minPointLength: 5, // Minimum bar width to make small values visible
                            dataLabels: {
                                enabled: true,
                                formatter: function() {
                                    return this.y;
                                },
                                style: {
                                    fontSize: '12px'
                                }
                            }
                        }
                    }
                });
            } else {
                $('#attrition_by_job_role_container').text('No data available.');
            }
        },
        
        
        
        
        job_role_wise_emp_attrition: function (jobroleName) {
            var self = this;
            this._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_eos.view_hr_employee_attrition_tree'],
            }).then(function (view_id) {
            self.do_action({
                name: _t("Attrition By Job Role"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'tree',
                views: [[view_id, 'list']],
                domain: [['job_id.name', '=', jobroleName], ['last_working_day', '>=', self.fiscalYearStartDate], ['last_working_day', '<=', self.fiscalYearEndDate], ['active', '=', false], ['employement_type.code', '!=', 'O'], ['company_id', '=', 1]],
                context: {'create': 0, 'edit': 0},
                target: 'current',
            });
        });
        },
        
        // Other methods as needed
        });
        
        
    core.action_registry.add('hr_dashboard_attrition', AttritionDashboard);

    return AttritionDashboard;
});
