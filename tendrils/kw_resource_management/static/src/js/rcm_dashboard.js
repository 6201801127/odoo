odoo.define('kw_resource_management.rcm_dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var ListController = require('web.ListController');

    var RCMDashboardView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        template: 'RCMDashboardMain',
        init: function (parent, action) {
            this.actionManager = parent;
            this.action = action;
            this.domain = [];
            return this._super.apply(this, arguments);
        },
        events: {
            'click .talent_pool_report': 'talent_pool_report',
            'click .under_skill': 'under_skill',
            'click .standard_orientation': 'standard_orientation',
            'click .future_projection': 'future_projection',
            'click .investment_resource': 'investment_resource',
        },
    
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },
        start: function () {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function () {
                setTimeout(function () {
                    self.render_graphs();
                }, 0);
            });
        },
        fetch_data: function() {
            var self = this;
            var def0 =  this._rpc({
                    model: 'talent_pool_dashboard',
                    method: 'get_talent_pool_count'
            }).done(function(result) {
                self.talent_pool_count =  result[0];
            });
            var def1 =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_under_skill_count'
            }).done(function(result) {
                self.under_skill_count =  result[0];
            });
            var def2 =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_standard_orientation_count'
            }).done(function(result) {
                self.standard_orientation_count =  result[0];
            });
            var def3 =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_future_projection_count'
            }).done(function(result) {
                self.future_projection_count =  result[0];
            });
            var def4 =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_investment_resource_count'
            }).done(function(result) {
                self.investment_resource_count =  result[0];
            });
            return $.when(def0,def1,def2,def3,def4);
        },
        
        render_graphs: function(){
            var self = this;
            self.render_designation_wise_strength_container_graph();
            self.render_skill_wise_strength_container_graph();
            self.render_location_wise_employee_strength_container_graph();
            self.render_engagement_plan_wise_distribution_container_graph();
            self.render_bench_day_wise_distribution_container_graph();
            self.render_skill_distribution_in_designation_container_graph();
        },
        talent_pool_report: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Report"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                target: 'current'
            })
    
        },
        under_skill: function(e){
            var self = this;
            console.log('click event is called')
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Report/Up Skilling Program"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['engagement_plan_by_id.code','=','usp']],
                target: 'current'
            })
    
        },
        standard_orientation: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Report/Standard Orientation Program"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['engagement_plan_by_id.code','=','sop']],
                target: 'current'
            })
    
        },
        future_projection: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Report/Future Projection"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['future_projection','!=',' ']],
                target: 'current'
            })
    
        },
        investment_resource: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Report/Investment Resource"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['engagement_plan_by_id.code','=','ir']],
                target: 'current'
            })
    
        },
        designation_wise_emp: function(e, select_deg_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Designation Wise Employee"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['designation', '=', select_deg_bar]],
                target: 'current'
            });
        },
        skill_wise_emp: function(e, select_skill_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Skill Wise Employee"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill_id', '=', select_skill_bar]],
                target: 'current'
            });
        },
        engagement_plan_wise_emp: function(e, select_plan_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Engagement Plan Wise Employee"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['engagement_plan_by_id', '=', select_plan_bar]],
                target: 'current'
            });
        },
        location_wise_emp: function(e, select_loc_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Location Wise Employee"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['job_branch_id', '=', select_loc_bar]],
                target: 'current'
            });
        },
        bench_day_wise_emp: function(e, select_bench_bar) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var domain;
            if (select_bench_bar=='<90 Days') {
                domain = [['interval_day', '<', 90]];
            } else if (select_bench_bar=='90-180 Days') {
                domain = [['interval_day', '>=', 90], ['interval_day', '<=', 180]];
            }  else if (select_bench_bar=='>180 Days') {
                domain = [['interval_day', '>', 180]];
            } 
            else {
                domain = [];
            }
            self.do_action({
                name: _t("Talent Pool Bench Day Wise Employee"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: domain,
                target: 'current'
            });
        },
        skill_distribution_emp: function(e, select_skill,select_desg) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Talent Pool Skill Distribution In Designation"),
                type: 'ir.actions.act_window',
                res_model: 'sbu_bench_resource',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['designation', '=', select_desg], ['primary_skill_id', '=', select_skill]],
                target: 'current'
            });
        },
        render_designation_wise_strength_container_graph: function() {
            var self = this;
            var defdesig = this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_designation_wise_strenth'
            }).done(function(result) {
                self.designation_strength_count =  result[0];
                Highcharts.chart('designation_wise_strength_container', {
                    chart: {
                        type: 'bar'
                    },
                    title: {
                        text: 'Designation wise strength'
                    },
                    xAxis: {
                        type: 'category',
                        labels: {
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'No of Employees'
                        }
                    },
                    legend: {
                        enabled: false
                    },
                    credits: {
                        enabled: false
                    },
                    tooltip: {
                        pointFormat: '<b> Employee Strength: {point.y}</b>'
                    },
                    series: [{
                        name: 'No of Employees',
                        colors: [
                            '#E6B333', '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                            '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
                        ],
                        colorByPoint: true,
                        groupPadding: 0,
                        data: self.designation_strength_count,
                        dataLabels: {
                            enabled: true,
                            color: '#FFFFFF',
                            align: 'center',
                            // format: '{point.y}', // one int
                            y: -3, // 10 pixels down from the top
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        },
                        point: {
                            events: {
                                click: function(e) {
                                    // Call the location_wise_emp function passing the selected bar name
                                    self.designation_wise_emp(e, this.name);
                                }
                            }
                        }
                    }]
                });
            });
        },
        render_skill_wise_strength_container_graph:function(){
            var self = this;
            var defskill =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_skill_wise_strenth'
            }).done(function(result) {
                self.skill_strength_count =  result[0];
                if (self.skill_strength_count && self.skill_strength_count.length > 0) {
                Highcharts.chart('skill_wise_strength_container', {
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                        type: 'pie'
                    },
                    title: {
                        text: 'Skill Wise Strength',
                        align: 'center'
                    },
                    credits: {
                        enabled: false
                    },
                    tooltip: {
                        pointFormat: '<b> {series.name}: {point.y}</b>'
                    },
                    accessibility: {
                        point: {
                            valueSuffix: '%'
                        }
                    },
                    plotOptions: {
                        pie: {
                            // allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}</b>: {point.y}'
                            },
                            showInLegend: true
                        }
                    },
                    series: [{
                        name: 'Count',
                        colors: [
                            '#E6B333', '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                            '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
                        ],
                        colorByPoint: true,
                        data: self.skill_strength_count,
                        point: {
                            events: {
                                click: function(e) {
                                    // Call the location_wise_emp function passing the selected bar name
                                    self.skill_wise_emp(e, this.name);
                                }
                            }
                        }
                    }]
                });
                } else {
                    // No data available, show a message in the donut container
                    var container = document.getElementById('skill_wise_strength_container');
                    container.innerHTML = 'No data available.';
                    container.style.textAlign = 'center';
                }
            });
        },
        render_engagement_plan_wise_distribution_container_graph: function(){
            var self = this;
            var defloc =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_engagement_plan_wise_distribution'
            }).done(function(result) {
                self.engagement_plan_wise_distribution =  result[0];
                Highcharts.chart('engagement_plan_wise_distribution_container', {
                    chart: {
                        type: 'pie',
                        options3d: {
                            enabled: true,
                            alpha: 45
                        }
                    },
                    title: {
                        text: 'Engagement Plan Wise Distribution',
                        align: 'center'
                    },
                    accessibility: {
                        point: {
                            valueSuffix: '%'
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        pie: {
                            innerSize: 100,
                            depth: 45,
                            allowPointSelect: true,
                            showInLegend: true
                        }
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.y}</b>'
                    },
                    series: [{
                        name: 'Count',
                        colors: [
                            '#E6B333', '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                            '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
                        ], // Add your desired colors here
                        colorByPoint: true,
                        data: self.engagement_plan_wise_distribution,
                        point: {
                            events: {
                                click: function(e) {
                                    // Call the location_wise_emp function passing the selected bar name
                                    self.engagement_plan_wise_emp(e, this.name);
                                }
                            }
                        }
                    }],
                });               
            });
        },
        
        render_location_wise_employee_strength_container_graph: function() {
            var self = this;
            var defloc = this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_location_wise_strenth'
            }).done(function(result) {
                self.location_emp_strength_count =  result[0];
                Highcharts.chart('location_wise_employee_strength_container_graph', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Location Wise Employee Strength'
                    },
                    xAxis: {
                        type: 'category',
                        labels: {
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        },
                    },
                   
                    legend: {
                        enabled: false
                    },
                    credits: {
                        enabled: false
                    },
                    tooltip: {
                        pointFormat: ' <b> Employee Strength:{point.y}</b>'
                    },
                    series: [{
                        name: 'Count',
                        colorByPoint: true,
                        colors: [
                            '#E6B333', '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                            '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
                        ], // Add your desired colors here
                        groupPadding: 0,
                        data: self.location_emp_strength_count,
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
                        point: {
                            events: {
                                click: function(e) {
                                    // Call the location_wise_emp function passing the selected bar name
                                    self.location_wise_emp(e, this.name);
                                }
                            }
                        }
                    }]
                });
            });
        },
        render_bench_day_wise_distribution_container_graph:function(){
            var self = this;
            var defbenchday =  this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_bench_day_wise_distribution'
            }).done(function(result) {
                self.bench_day_count =  result[0];
                setTimeout(function(){
                    Highcharts.chart('bench_day_wise_distribution_container_graph', {
                        chart: {
                          type: 'waterfall'
                        },
                      
                        title: {
                          text: 'Bench Day Wise Distribution',
                          align: 'center'
                        },
                      
                        xAxis: {
                          type: 'category'
                        },
                        yAxis: {
                          title: {
                            text: 'Count'
                          }
                        },
                        legend: {
                          enabled: false
                        },
                        credits: {
                            enabled: false
                        },
                        tooltip: {
                          pointFormat: '<b>Count:{point.y}</b>'
                        },
                        series: [{
                            colors: ['#FF6633','#3366E6','#FF99E6', '#00B3E6'],
                            colorByPoint: true,
                          data:self.bench_day_count,
                          dataLabels: {
                            enabled: true,
                          },
                          pointPadding: 0,
                          point: {
                            events: {
                                click: function(e) {
                                    // Call the location_wise_emp function passing the selected bar name
                                    self.bench_day_wise_emp(e, this.name);
                                }
                            }
                        }
                        }]
                      });
                })
            });
        },
        render_skill_distribution_in_designation_container_graph: function() {
            var self = this;
            var defskill = this._rpc({
                model: 'talent_pool_dashboard',
                method: 'get_skill_distribution_in_designation'
            }).done(function(result) {
                self.skill_distribution_count = result;
                var categories = [];
                var seriesData = {};
        
                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (designation)
                    var skill = data.name; // Skill
                    var skillCount = data.data; // Skill count
        
                    if (!seriesData[skill]) {
                        seriesData[skill] = {};
                    }
                    seriesData[skill][category] = skillCount;
        
                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                for (var skill in seriesData) {
                    var skillData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[skill][category] || 0;
                        skillData.push(count);
                    }
                    series.push({
                        name: skill,
                        data: skillData
                    });
                }
                Highcharts.chart('skill_distribution_in_designation_container_graph', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Skill Distribution In Designation',
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
                        pointFormat: '{series.name}: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                        // pointFormat: '{point.y} ({point.percentage:.0f}%)<br/>',
                        pointFormatter: function() {
                            if (this.y !== 0) {
                            return this.series.name + ': <b>' + this.y + '</b> (' + this.percentage.toFixed(0) + '%)<br/>';
                            } else {
                            return '';
                            }
                        },
                        shared: true
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            stacking: 'percent',
                            point: {
                                events: {
                                    click: function (e) {
                                        // Call the skill_distribution_emp function passing the selected skill name
                                        self.skill_distribution_emp(e, this.series.name, this.category);
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    colors: [
                        '#E6B333', '#3366E6',  '#99FF99', '#FF99E6','#66991A','#4D8066',
                        '#FF6633', '#00B3E6','#991AFF', '#1AB399','#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
                    ], // Add your desired colors here
                });
            });
        },
    });
    core.action_registry.add('kw_resource_management.rcm_dashboard', RCMDashboardView);

    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
     
            if(this.modelName == 'kw_resource_mapping_data' && this.viewType == 'list'){
                this.button_click_resource_map();
                
            }
        },
        button_click_resource_map: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_resource_mapping_button', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Employee Resource Mapping Data from Tendrils V5",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        return rpc.query({
                            model: 'kw_resource_mapping_data',
                            method: 'sync_resource_mapping_data',
                            args: [{'a':'b'}],
                        }).then(function (e) {
                            console.log(e);                            
                        });
                    }
                  }
                );
            });

        }
    });
    

    return ListController, RCMDashboardView;

});