odoo.define('gts_project_dashboard.DashboardOffice', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var ProjectDashboard = AbstractAction.extend({
    template: 'ProjectDashboard',
    events: {
//            'click .pos_order_today':'pos_order_today',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['ManagerProject'];
        this.revenue_expense = [];
        this.tenders_list = [];
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'project.project',
                method: 'get_details'
        }).then(function(result) {
           self.revenue_expense = result['revenue_expense']
           self.tenders_list = result['tenders_list']
        });
        return $.when(def1);
    },

    render_dashboards: function() {
        var self = this;
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_project_dashboard').append(QWeb.render(template, {widget: self}));
            });
    },
    render_graphs: function(){
        var self = this;
        self.onclick_contract();
        self.onclick_project_manager();
        self.onclick_program_manager();
        self.onclick_budget();
        self.onclick_stagewise();
        self.onclick_project_resource();
    },

    onclick_contract:function(events){
       var self = this;
       var ctx = self.$(".contractChart");
            rpc.query({
                model: "project.project",
                method: "get_contract_count",
                args: [],
            }).then(function (arrays) {
          var data = {
            labels: ['Active', 'Closed'],
            datasets: [
              {
                label: "",
                data: [arrays['active_contracts'],arrays['closed_contracts']],
                backgroundColor: [
                  "rgb(148, 22, 227)",
                  "rgba(54, 162, 235)",
                  "rgba(75, 192, 192)",
                  "rgba(153, 102, 255)",
                  "rgba(10,20,30)"
                ],
                borderColor: [
                 "rgba(255, 99, 132,)",
                  "rgba(54, 162, 235,)",
                  "rgba(75, 192, 192,)",
                  "rgba(153, 102, 255,)",
                  "rgba(10,20,30,)"
                ],
                borderWidth: 1
              },
            ]
          };
       //options
          var options = {
            responsive: true,
            title: {
              display: true,
              position: "top",
              text: "",
              fontSize: 18,
              fontColor: "#111"
            },
            legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
            scales: {
              yAxes: [{
                ticks: {
                  min: 0
                }
              }]
            }
          };
//       create Chart class object
          var chart = new Chart(ctx, {
            type: "doughnut",
            data: data,
            options: options
          });
        });
        },

    onclick_project_manager:function(events){
       var self = this;
       var ctx = self.$(".projectmanagerChart");
            rpc.query({
                model: "project.project",
                method: "get_project_manager_tagged",
                args: [],
            }).then(function (arrays) {
          var data = {
            labels: arrays['project_manager_name'],
            datasets: [
              {
                label: "Project Tagged (Avg)",
                data: arrays['count_list'],
                backgroundColor: '#b3aa47',
                borderColor: '#b3aa47',
                borderWidth: 1
              },
            ]
          };
       //options
          var options = {
            responsive: true,
            title: {
              display: false,
              position: "top",
              text: "",
              fontSize: 18,
              fontColor: "#111"
            },
            legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
            scales: {
              yAxes: [{
                ticks: {
                  min: 0
                }
              }]
            }
          };
//       create Chart class object
          var chart = new Chart(ctx, {
            type: "line",
            data: data,
            options: options
          });
        });
        },

    onclick_program_manager:function(events){
       var self = this;
       var ctx = self.$(".programmanagerChart");
            rpc.query({
                model: "project.project",
                method: "get_program_manager_tagged",
                args: [],
            }).then(function (arrays) {
          var data = {
            labels: arrays['program_manager_name'],
            datasets: [
              {
                label: "Project Tagged (Avg)",
                data: arrays['count_list'],
                backgroundColor: '#b3aa8d',
                borderColor: '#b3aa8d',
                borderWidth: 1
              },
            ]
          };
       //options
          var options = {
            responsive: true,
            title: {
              display: false,
              position: "top",
              text: "",
              fontSize: 18,
              fontColor: "#111"
            },
            legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
            scales: {
              yAxes: [{
                ticks: {
                  min: 0
                }
              }]
            }
          };
//       create Chart class object
          var chart = new Chart(ctx, {
            type: "bar",
            data: data,
            options: options
          });
        });
        },

    onclick_budget:function(events){
       var self = this;
       var ctx = self.$(".budgetChart");
            rpc.query({
                model: "project.project",
                method: "get_budget_cost_expense",
                args: [],
            }).then(function (arrays) {
          var data = {
            labels: arrays['project_list'],
            datasets: [
              {
                label: "Total Budgeted Amount",
                data: arrays['budget_list'],
                backgroundColor: 'green',
                borderColor: 'green',
                borderWidth: 1
              },
              {
                label: "Utilization Amount",
                data: arrays['utilized_list'],
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1
              },
            ]
          };
       //options
          var options = {
            responsive: true,
            title: {
              display: false,
              position: "top",
              text: "",
              fontSize: 18,
              fontColor: "#111"
            },
            legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
            scales: {
              yAxes: [{
                ticks: {
                  min: 0
                }
              }]
            }
          };
//       create Chart class object
          var chart = new Chart(ctx, {
            type: "bar",
            data: data,
            options: options
          });
        });
        },

    onclick_stagewise:function(events){
       var self = this;
       var ctx = self.$(".stagewiseChart");
            rpc.query({
                model: "project.project",
                method: "get_stage_wise_project",
                args: [],
            }).then(function (arrays) {
                console.log("arrays", arrays)
          var data = {
            labels: arrays['stage_list'],
            datasets: [
              {
                label: "",
                data: arrays['project_list'],
                backgroundColor: [
                  "rgb(148, 22, 227)",
                  "rgba(54, 162, 235)",
                  "rgba(75, 192, 192)",
                  "rgba(153, 102, 255)",
                  "rgba(10,20,30)"
                ],
                borderColor: [
                 "rgba(255, 99, 132,)",
                  "rgba(54, 162, 235,)",
                  "rgba(75, 192, 192,)",
                  "rgba(153, 102, 255,)",
                  "rgba(10,20,30,)"
                ],
                borderWidth: 1
              },
            ]
          };

       //options
          var options = {
            responsive: true,
            title: {
              display: true,
              position: "top",
              text: "",
              fontSize: 18,
              fontColor: "#111"
            },
            legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
            scales: {
              yAxes: [{
                ticks: {
                  min: 0
                }
              }]
            }
          };

//       create Chart class object
          var chart = new Chart(ctx, {
            type: "pie",
            data: data,
            options: options
          });

        });
        },

    onclick_project_resource:function(events){
       var self = this;
       var ctx = self.$("#canvas_2");
            rpc.query({
                model: "project.project",
                method: "get_project_resource",
                args: [],
            }).then(function (arrays) {
          var data = {
            labels: arrays['project_resource'],
            datasets: [
              {
                label: ['Internal Resource'],
                data: arrays['internal_list'],
                backgroundColor: '#FFBF00',
                borderColor: '#FFBF00',
                borderWidth: 1
              },
              {
                label: ['External Resource'],
                data: arrays['external_list'],
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1
              },
            ]
          };

       //options
          var options = {
            responsive: true,
            title: {
              display: false,
              position: "top",
              text: "",
              fontSize: 18,
              fontColor: "#111"
            },
            legend: {
              display: true,
              position: "bottom",
              labels: {
                fontColor: "#333",
                fontSize: 16
              }
            },
            scales: {
              yAxes: [{
                ticks: {
                  min: 0
                }
              }]
            }
          };

       //create Chart class object
          var chart = new Chart(ctx, {
            type: "horizontalBar",
            data: data,
            options: options
          });

        });
        },

});


core.action_registry.add('project_dashboard_office', ProjectDashboard);

return ProjectDashboard;

});
