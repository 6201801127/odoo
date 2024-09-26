odoo.define('gts_project_dashboard.Dashboard', function (require) {
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
        this.dashboards_templates = ['UserChart'];
        this.quality_list = [];
        this.project_tagged = [];
        this.tasks_list = [];
        this.issue_list = [];
        this.change_request_list = [];
        this.ticket_list = [];
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
           self.quality_list = result['quality_list']
           self.project_tagged = result['project_tagged']
           self.tasks_list = result['tasks_list']
           self.issue_list = result['issue_list']
           self.change_request_list = result['change_request_list']
           self.ticket_list = result['ticket_list']
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
        self.onclick_project_resource();
        self.onclick_risk();
    },

    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
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

       onclick_risk:function(events){
       var self = this;
       var bg_color_list = []
       for (var i=0;i<=100;i++){
            bg_color_list.push(self.getRandomColor())
       }
       var ctx = self.$(".riskChart");
            rpc.query({
                model: "project.project",
                method: "get_project_risk",
                args: [],
            }).then(function (arrays) {
          var data = {
            labels: arrays['project_list'],
            datasets: [
              {
                label: "",
                data: arrays['risk_list'],
                backgroundColor: bg_color_list,
                borderColor: bg_color_list,
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
              display: false,
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
            type: "horizontalBar",
            data: data,
            options: options
          });

        });
        },

});


core.action_registry.add('project_dashboard', ProjectDashboard);

return ProjectDashboard;

});
