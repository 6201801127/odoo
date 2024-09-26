odoo.define('kw_resource_management.rcm_skill_data_dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var SkillAnalyticsDashboardView = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: true,
        events: {

            'click #filter-location-button': _.debounce(function (ev) {
                var self = this;
                self.loc_skill_select_id = $('#filter-location-select').val();
                self.loc_select_id = $('#filter-lskill-select').val();
                if (self.loc_skill_select_id !=0 || self.loc_select_id !=0)
                    self.render_location_wise_skill_container_graph('filter_loc_skill');
                if (self.loc_skill_select_id == 0 || self.loc_select_id ==0)
                    self.render_location_wise_skill_container_graph('');
            }, 0, true),

            'click .refresh_loc_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_location_skill_data = true;
                self.render_location_wise_skill_container_graph("refresh_loc_skill");
            }, 0, true),


            'click #filter-total-skill-button': _.debounce(function (ev) {
                var self = this;
                self.skill_type_select_id = $('#filter-skill-type-select').val();
                self.pst_select_id = $ ('#filter-pst-skill-select').val();
                if (self.skill_type_select_id != 0 || self.pst_select_id !=0)
                    self.render_skill_distribution_in_type_container_graph('filter_total_skill');
                if (self.skill_type_select_id == 0 || self.pst_select_id == 0)
                    self.render_skill_distribution_in_type_container_graph('');
            }, 0, true),

            'click .refresh_skill_type_portlet': _.debounce(function () {
                var self = this;
                self.refresh_skill_type_data = true;
                self.render_skill_distribution_in_type_container_graph("refresh_total_skill");
            }, 0, true),

            'click #filter-skill-role-button': _.debounce(function (ev) {
                var self = this;
                self.role_select_id = $('#filter-role-select').val();
                self.role_skill_select_id = $('#filter-role_skill-select').val();
                if (self.role_select_id != 0 || self.role_skill_select_id != 0)
                    self.render_skill_wise_role_distribution_container_graph('filter_skill_role');
                if (self.role_select_id == 0 || self.role_select_id ==0)
                    self.render_skill_wise_role_distribution_container_graph('');
            }, 0, true),

            'click .refresh_skill_role_portlet': _.debounce(function () {
                var self = this;
                self.refresh_skill_role_data = true;
                self.render_skill_wise_role_distribution_container_graph("refresh_skill_role");
            }, 0, true),

            'click #filter-skill-button': _.debounce(function (ev) {
                var self = this;
                self.primary_skill_select_id = $('#filter-skill-select').val();
                if(self.primary_skill_select_id !=0)
                    self.render_total_primary_skill_container_graph('filter_primary_skill');
                if(self.primary_skill_select_id == 0)
                    self.render_total_primary_skill_container_graph('');
                }, 0, true),

            'click .refresh_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_skill_data = true;
                self.render_total_primary_skill_container_graph("refresh_primary_skill");
            }, 0, true),

            'click #filter-emtech-button': _.debounce(function (ev) {
                var self = this;
                self.emtech_skill_select_id = $('#filter-emtech-select').val();
                if(self.emtech_skill_select_id !=0)
                    self.render_sbu_wise_emtech_container_graph('filter_emtech_skill');
                if(self.emtech_skill_select_id == 0)
                    self.render_sbu_wise_emtech_container_graph('');
            }, 0, true),

            'click .refresh_emtech_portlet': _.debounce(function () {
                var self = this;
                self.refresh_emtech_data = true;
                self.render_sbu_wise_emtech_container_graph("refresh _emtech_skill");
            }, 0, true),

            'click #filter-certification-button': _.debounce(function (ev) {
                var self = this;
                self.certification_select_id = $('#filter-certification-select').val();
                if(self.certification_select_id != 0)
                    self.render_certification_count_container_graph('filter_certification')
                if(self.certification_select_id == 0)
                    self.render_certification_count_container_graph('');
            }, 0, true),

            'click .refresh_certification_portlet': _.debounce(function () {
                var self = this;
                self.refresh_certification_data = true;
                self.render_certification_count_container_graph("refresh_certification");
            }, 0, true),

            'click #filter-db-button': _.debounce(function (ev) {
                var self = this;
                self.designation_skill_select_id = $('#filter-designation-select').val();
                self.desg_skill_select_id = $('#filter-db-skill-select').val();
                if (self.designation_skill_select_id != 0 || self.desg_skill_select_id != 0)
                    self.render_database_bifurcation_container_graph('filter_db_skill');
                if (self.designation_skill_select_id ==0 || self.desg_skill_select_id ==0)
                    self.render_database_bifurcation_container_graph('');
            }, 0, true),

            'click .refresh_db_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_db_skill_data = true;
                self.render_database_bifurcation_container_graph("refresh_db_skill");
            }, 0, true),
            'click #filter-sbu-skill-button': _.debounce(function (ev) {
                var self = this;
                self.sbu_select_id = $('#filter-sbu-select').val();
                self.sbu_skill_select_id = $('#filter-sbu_skill-select').val();
                if (self.sbu_select_id != 0 || self.sbu_skill_select_id != 0)
                    self.render_sbu_wise_skill_distribution('filter_skill_sbu');
                if (self.sbu_select_id == 0 || self.sbu_select_id ==0)
                    self.render_sbu_wise_skill_distribution('');
            }, 0, true),

            'click .refresh_sbu_skill_portlet': _.debounce(function () {
                var self = this;
                self.refresh_skill_sbu_data = true;
                self.render_sbu_wise_skill_distribution("refresh_skill_sbu");
            }, 0, true),

            'click #filter-ex-it-button': _.debounce(function (ev) {
                var self = this;
                self.exit_skill_select_id = $('#filter-exit-type-select').val();
                if(self.exit_skill_select_id != 0)
                    self.render_skill_wise_extit_container_graph('filter_exit_skill');
                if(self.exit_skill_select_id ==0 )
                    self.render_skill_wise_extit_container_graph('');
            }, 0, true),

            'click .refresh_exit_portlet': _.debounce(function () {
                var self = this;
                self.refresh_exit_data = true;
                self.render_skill_wise_extit_container_graph("refresh_exit_skill");
            }, 0, true),


        },


        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_resource_management.rcm_skill_data_dashboard') {
                self._rpc({
                    model: 'skill_data_analytics_dashboard',
                    method: 'get_filter_data',
                }, []).then(function (result) {
                    self.primary_skill_filters = result['dashboard_filters'][0];
                    self.emtech_skill_filters = result['dashboard_filters'][1];
                    self.certification_filters = result['dashboard_filters'][2];
                    self.db_skill_filters = result['dashboard_filters'][3];
                    self.exit_skill_filters = result['dashboard_filters'][4];
                    self.loc_skill_filters = result['dashboard_filters'][5];
                    self.skill_type_filters = result['dashboard_filters'][6];
                    self.role_skill_filters = result['dashboard_filters'][7];
                    self.sbu_skill_filters = result['dashboard_filters'][8];
                    self.pst_skill_filters = result['dashboard_filters'][9];
                    self.designation_filter = result['dashboard_filters'][10];
                }).done(function () {
                    self.render();
                    self.href = window.location.href;
                });
            }
        },

        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            this.set("title", 'Skill Analytics Dashboard');
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var hr_dashboard = QWeb.render('kw_resource_management.rcm_skill_data_dashboard', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(hr_dashboard).prependTo(self.$el);
            self.render_graphs();
            self.renderDashboard();
            return hr_dashboard
        },
        get_primary_skill: function (e, select_primary_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Primary Skill"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill.name', '=', select_primary_skill]],
                target: 'current'
            });
        },
        get_location_wise_skill: function (e, select_loc,select_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Location Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill.name', '=', select_skill], ['emp_location', '=', select_loc]],
                target: 'current'
            });
        },
        get_total_skill_wise_count: function (e, select_skill_type, select_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Total Skill Wise"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain : ['|',
                    '|',
                    '&',
                    ['primary_skill.name', '=', select_skill],
                    ['primary_skill_type', '=', select_skill_type],
                    '&',
                    ['secondary_skill.name', '=', select_skill],
                    ['secondary_skill_type', '=', select_skill_type],
                    '&',
                    ['tertiarry_skill.name', '=', select_skill],
                    ['tertiary_skill_type', '=', select_skill_type]
                    ],


                target: 'current'
            });
        },

        get_skill_wise_role: function (e, select_role, select_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            console.log("Club Role",select_role)
            self.do_action({
                name: _t("Skill wise Role"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['club_role', '=', select_role], ['primary_skill.name', '=', select_skill]],
                target: 'current'
            });
        },
        get_sbu_wise_skill: function (e, select_skill,select_sbu) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Skill wise Role"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['sbu_master_id.name', '=', select_sbu], ['primary_skill.name', '=', select_skill]],
                target: 'current'
            });
        },
        get_sbu_emtech_wise_skill: function (e, select_resource,select_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            console.log('skill',select_skill,'type',select_resource)
            self.do_action({
                name: _t("SBU EmTech Wise Skill"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill.name', '=', select_skill],['sbu_type', '=', select_resource], ['sbu_master_id', '!=', false]],
                target: 'current'
            });
        },
        certification_wise: function (e, select_crt) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Certification Wise"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: ['|', '|', '|', '|', ['certification_course_1.name', '=', select_crt], ['certification_course_2.name', '=', select_crt], ['certification_course_3.name', '=', select_crt], ['certification_course_4.name', '=', select_crt], ['certification_course_5.name', '=', select_crt]],
                target: 'current'
            });
        },
        database_wise_bifurcation: function (e, select_desg, select_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Database Bifurcation"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['designation', '=', select_desg], ['primary_skill', '=', select_skill]],
                target: 'current'
            });
        },
        skill_eisw_total_ext_it: function (e, select_skill) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                name: _t("Skill Wise Total Ext-IT"),
                type: 'ir.actions.act_window',
                res_model: 'skill_dashboard_analytics_report',
                view_mode: 'tree',
                view_type: 'form',
                views: [[false, 'list']],
                domain: [['primary_skill.name', '=', select_skill], ['sbu_type', '=', 'horizontal'], ['sbu_master_id.name', '=', 'External-IT'], ['sbu_master_id', '!=', false]],
                target: 'current'
            });
        },
        render_graphs: function () {
            var self = this;
            self.render_total_primary_skill_container_graph();
            self.render_location_wise_skill_container_graph();
            self.render_skill_wise_role_distribution_container_graph();
            self.render_sbu_wise_emtech_container_graph();
            self.render_certification_count_container_graph();
            self.render_database_bifurcation_container_graph();
            self.render_skill_wise_extit_container_graph();
            self.render_skill_distribution_in_type_container_graph();
            self.render_sbu_wise_skill_distribution();
        },
        renderDashboard: async function () {
            var self = this;
            self.$el.find('.primary-skill-filter-wrapper,.location-skill-filter-wrapper,.skill-type-filter-wrapper,.skill-role-filter-wrapper,.sbu-skill-filter-wrapper,.emtech-skill-filter-wrapper,.certification-skill-filter-wrapper,.database-skill-filter-wrapper,.extit-skill-filter-wrapper').css('display', 'none');
            self.$el.find('#skill-filter').click(function () {
                self.$el.find('.primary-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_primary_skill_filter,#filter-skill-button').click(function () {
                self.$el.find('.primary-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#location-filter').click(function () {
                self.$el.find('.location-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_location_filter,#filter-location-button').click(function () {
                self.$el.find('.location-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#total-skill-filter').click(function () {
                self.$el.find('.skill-type-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_total_skill_filter,#filter-total-skill-button').click(function () {
                self.$el.find('.skill-type-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#skill-wise-role-filter').click(function () {
                self.$el.find('.skill-role-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_skill_role_filter,#filter-skill-role-button').click(function () {
                self.$el.find('.skill-role-filter-wrapper').css('display', 'none');
            });

            self.$el.find('#emtech-filter').click(function () {
                self.$el.find('.emtech-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_emtech_filter,#filter-emtech-button').click(function () {
                self.$el.find('.emtech-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#certification-filter').click(function () {
                self.$el.find('.certification-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_certification_filter,#filter-certification-button').click(function () {
                self.$el.find('.certification-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#database-skill-filter').click(function () {
                self.$el.find('.database-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_db_filter,#filter-db-button').click(function () {
                self.$el.find('.database-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#sbu-wise-skill-filter').click(function () {
                self.$el.find('.sbu-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_sbu_filter,#filter-sbu-skill-button').click(function () {
                self.$el.find('.sbu-skill-filter-wrapper').css('display', 'none');
            });
            self.$el.find('#external-id-skill-filter').click(function () {
                self.$el.find('.extit-skill-filter-wrapper').css('display', '');
            });
            self.$el.find('#close_ext_it_filter,#filter-ex-it-button').click(function () {
                self.$el.find('.extit-skill-filter-wrapper').css('display', 'none');
            });

            return true;
        },

        render_total_primary_skill_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_primary_skill') params = { 'primary_skill_id': self.primary_skill_select_id }
            if (status == 'refresh_primary_skill') params = {}
            var deftotalprimaryskill = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_primary_skill_count',
                kwargs: params,
            }).done(function (result) {
                var skillCountPairs = result[0];
                if (result && result.length > 0){
                var categories = [];
                var seriesData = [];

                for (var i = 0; i < skillCountPairs.length; i++) {
                    categories.push(skillCountPairs[i][0]);
                    seriesData.push({
                        name: skillCountPairs[i][0],
                        y: skillCountPairs[i][1]
                    });
                }
                Highcharts.chart('total_primary_skill_container_graph', {
                    chart: {
                        type: 'pie',
                    },
                    title: {
                        text: 'Total Primary Skill',
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
                            innerSize: 70,
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
                        colors: ['#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066', '#FF6633', '#00B3E6', '#991AFF', '#4efcdf', '#791fb5', '#FF1A66', '#33FFCC', '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF', '#E6B333'],
                        colorByPoint: true,
                        data: seriesData,
                        point: {
                            events: {
                                click: function (e) {
                                    self.get_primary_skill(e, this.name);
                                }
                            }
                        }
                    }],
                });
            }else {
                var container = document.getElementById('total_primary_skill_container_graph');
                container.innerHTML = 'No Data Available';
                container.style.textAlign = 'center';
            }
        });
    },
        
        render_location_wise_skill_container_graph: async function (status) {
            var self = this;
            var params
            if (status == 'filter_loc_skill') params = { 'location': self.loc_skill_select_id, 'skill': self.loc_select_id }
            if (status == 'refresh_loc_skill') params = {}
            var deflocationwiseskill = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_location_wise_skill_count',
                kwargs: params,
            }).done(function (result) {
                self.location_wise_skill_count = result;
                if(result && result.length >0) {
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
                Highcharts.chart('location_wise_skill_container_graph', {
                    chart: {
                        type: 'bar'
                    },
                    title: {
                        text: 'Location Wise Skill Count',
                        align: 'center'
                    },
                    xAxis: {
                        categories: categories,
                        title: {
                            text: null
                        },
                        gridLineWidth: 1,
                        lineWidth: 0
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Resource Count',
                            align: 'high'
                        },
                        labels: {
                            overflow: 'justify'
                        },
                        gridLineWidth: 0
                    },

                    plotOptions: {
                        bar: {
                            // borderRadius: '50%',
                            point: {
                                events: {
                                    click: function (e) {
                                        self.get_location_wise_skill(e, this.series.name, this.category);
                                    }
                                }
                            },
                            groupPadding: 0.1,
                            showInLegend: true,
                            stacking: 'normal' // You can use 'normal', 'percent', or null for no stacking
                        }
                    },
                    
                    credits: {
                        enabled: false
                    },
                    series: series,
                    colors: [
                        '#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066',
                        '#FF6633', '#00B3E6', '#991AFF', '#4efcdf', '#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF', '#E6B333',
                    ], // Add your desired colors here
                });
            }else {
                var container = document.getElementById('location_wise_skill_container_graph');
                container.innerHTML = 'No Matching Data Available.';
                container.style.textAlign = 'center';

            }
        });
    },
        render_skill_wise_role_distribution_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_skill_role') params = { 'role': self.role_select_id, 'skill': self.role_skill_select_id }
            if (status == 'refresh_skill_role') params = {}
            var defskillrole = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_skill_wise_role_count',
                kwargs: params,
            }).done(function (result) {
                self.skill_wise_role_count = result;
                if(result && result.length > 0){
                var categories = [];
                var seriesData = {};

                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (designation)
                    var role = data.name; // role
                    var roleCount = data.data; // role count

                    if (!seriesData[role]) {
                        seriesData[role] = {};
                    }
                    seriesData[role][category] = roleCount;

                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                for (var role in seriesData) {
                    var roleData = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[role][category] || 0;
                        roleData.push(count);
                    }
                    series.push({
                        name: role,
                        data: roleData
                    });
                }
                Highcharts.chart('skill_wise_role_ditribution_container_graph', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Skill Wise Role Distribution',
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
                    legend: {
                        itemWidth: 100, // Set the width of each legend item
                        itemMarginBottom: 5, // Set the margin between legend items
                        layout: 'horizontal', // Arrange legend items horizontally
                        align: 'center', // Align the legend to the center
                        width: 400, // Set the width of the legend container
                        labelFormatter: function () {
                            // Customize the legend label if needed
                            return this.name;
                        }
                    },
                    tooltip: {
                        pointFormat: ' <b> {series.name}:{point.y}</b>'
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
                                        self.get_skill_wise_role(e, this.series.name, this.category);
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    colors: [
                        '#991AFF', '#4efcdf', '#FF99E6', '#66991A', '#4D8066','#FF6633', '#00B3E6', 
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF', '#791fb5', '#FF1A66', '#E6B333',
                    ], // Add your desired colors here
                });
            }else {
                var container = document.getElementById('skill_wise_role_ditribution_container_graph');
                container.innerHTML = 'No Matching Data Available';
                container.style.textAlign = 'center';
            }
        });
    },
        render_sbu_wise_skill_distribution: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_skill_sbu') params = { 'sbu': self.sbu_select_id, 'skill': self.sbu_skill_select_id }
            if (status == 'refresh_skill_sbu') params = {}
            var defskillrole = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'sbu_wise_skill_count',
                kwargs: params,
            }).done(function (result) {
                self.sbu_wise_skill = result;
                if (result && result.length > 0){
                var categories = [];
                var seriesData = {};

                for (var i = 0; i < result.length; i++) {
                    var data = result[i];
                    var category = data.category; // Category (designation)
                    var sbu = data.name; // SBU
                    var sbu_count = data.data; // SBU count

                    if (!seriesData[sbu]) {
                        seriesData[sbu] = {};
                    }
                    seriesData[sbu][category] = sbu_count;

                    if (!categories.includes(category)) {
                        categories.push(category);
                    }
                }
                var series = [];
                for (var sbu in seriesData) {
                    var sbudata = [];
                    for (var i = 0; i < categories.length; i++) {
                        var category = categories[i];
                        var count = seriesData[sbu][category] || 0;
                        sbudata.push(count);
                    }
                    series.push({
                        name: sbu,
                        data: sbudata
                    });
                }
                Highcharts.chart('sbu_wise_skill_graph_cointainer', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'SBU Wise Skill Distribution',
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
                        pointFormat: ' <b> {series.name}:{point.y}</b>'
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
                                        // Call the SBU Wise Skill Count function passing the selected SBU name
                                        self.get_sbu_wise_skill(e, this.series.name, this.category);
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    colors: [
                        '#00B3E6', '#991AFF', '#4efcdf', '#791fb5', '#FF1A66','#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066','#FF6633',  '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF', '#E6B333',
                    ], // Add your desired colors here
                });
            }else {
                var container = document.getElementById('sbu_wise_skill_graph_cointainer');
                container.innerHTML = 'No Matching Data Available';
                container.style.textAlign = 'center';
            }
        });
    },

        render_sbu_wise_emtech_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_emtech_skill') params = { 'emtech_skill_id': self.emtech_skill_select_id }
            var skillData = await this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_emtech_skill_count',
                kwargs: params,
            });
        
            var categories = skillData.map(item => item.name);
            var sbuCountData = skillData.map(item => item.sbu_count);
            var horizontalCountData = skillData.map(item => item.horizontal_count);
            if (skillData && skillData.length > 0){
            Highcharts.chart('emtech_skill_container_graph', {
                chart: {
                    type: 'bar'
                },
                title: {
                    text: 'SBU Wise EmTech Resource',
                    align: 'center'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    accessibility: {
                        description: 'Skills'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    bar: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        point: {
                            events: {
                                click: function (e) {
                                    self.get_sbu_emtech_wise_skill(e, this.series.options.custom.type, this.category);
                                }
                            }
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                series: [
                    {
                        name: 'SBU',
                        custom:{
                            type:'sbu'
                        },
                        data: sbuCountData
                    },
                    {
                        name: 'Horizontal',
                        custom:{
                            type:'horizontal'
                        },
                        data: horizontalCountData
                    },
                                       
                ],
                colors: [
                   '#4D8066','#FF6633',
                ],
            });
        }else {
            var container = document.getElementById('emtech_skill_container_graph');
            container.innerHTML = 'No Data Available';
            container.style.textAlign = 'center';
        }
        },
        render_certification_count_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_certification') params = { 'certification_id': self.certification_select_id }
            var defcertification = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_certification_skill_count',
                kwargs: params,
            }).done(function (result) {
                self.certification_count = result[0];
                if (self.certification_count && self.certification_count.length > 0) {
                    Highcharts.chart('certification_skill_container_graph', {
                        chart: {
                            plotBackgroundColor: null,
                            plotBorderWidth: null,
                            plotShadow: false,
                            type: 'pie'
                        },
                        title: {
                            text: 'Certification Count',
                            align: 'center'
                        },
                        credits: {
                            enabled: false
                        },
                        tooltip: {
                            pointFormat: '<b> {series.name}: {point.y}</b>'
                        },
                        legend: {
                            itemWidth: 100, // Set the width of each legend item
                            itemMarginBottom: 5, // Set the margin between legend items
                            layout: 'horizontal', // Arrange legend items horizontally
                            align: 'center', // Align the legend to the center
                            width: 400, // Set the width of the legend container
                            labelFormatter: function () {
                                // Customize the legend label if needed
                                return this.name;
                            }
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
                                '#E6B333', '#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066',
                                '#FF6633', '#00B3E6', '#991AFF', '#4efcdf', '#791fb5', '#FF1A66', '#33FFCC',
                                '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
                            ],
                            colorByPoint: true,
                            data: self.certification_count,
                            point: {
                                events: {
                                    click: function (e) {
                                        self.certification_wise(e, this.name);
                                    }
                                }
                            }
                        }]
                    });
                } else {
                    // No data available, show a message in the donut container
                    var container = document.getElementById('certification_skill_container_graph');
                    container.innerHTML = 'No data available.';
                    container.style.textAlign = 'center';
                }
            });
        },
        render_skill_wise_extit_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_exit_skill') params = { 'ex_it_skill_id': self.exit_skill_select_id }
            var defexternalitskill = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_ext_it_skill_count',
                kwargs: params,
            }).done(function (result) {
                self.external_it_skill_count = result[0];
                if (self.external_it_skill_count && self.external_it_skill_count.length > 0) {
                    Highcharts.chart('external_it_skill_container_graph', {
                        chart: {
                            plotBackgroundColor: null,
                            plotBorderWidth: null,
                            plotShadow: false,
                            type: 'pie'
                        },
                        title: {
                            text: 'Skill Wise Total Ext-IT',
                            align: 'center'
                        },
                        credits: {
                            enabled: false
                        },
                        legend: {
                            itemWidth: 100, // Set the width of each legend item
                            itemMarginBottom: 5, // Set the margin between legend items
                            layout: 'horizontal', // Arrange legend items horizontally
                            align: 'center', // Align the legend to the center
                            width: 400, // Set the width of the legend container
                            labelFormatter: function () {
                                // Customize the legend label if needed
                                return this.name;
                            }
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
                                '#FF4D4D', '#99E6E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066',
                                '#FF6633',  '#4efcdf', '#791fb5', '#FF1A66', '#33FFCC',
                                '#E64D66', '#4DB380', '#6666FF','#00B3E6', '#991AFF','#E6B333', '#3366E6',
                            ],
                            colorByPoint: true,
                            data: self.external_it_skill_count,
                            point: {
                                events: {
                                    click: function (e) {
                                        self.skill_eisw_total_ext_it(e, this.name);
                                    }
                                }
                            }
                        }]
                    });
                } else {
                    // No data available, show a message in the donut container
                    var container = document.getElementById('external_it_skill_container_graph');
                    container.innerHTML = 'No data available.';
                    container.style.textAlign = 'center';
                }
            });
        },
        render_database_bifurcation_container_graph: function (status) {
            var self = this;
            var params = {}
            if (status == 'filter_db_skill') params = { 'designation': self.designation_skill_select_id, 'db_skill': self.desg_skill_select_id }
            if (status == 'refresh_db_skill') params = {}

            var defdatabasebifurcation = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_database_skill_count',
                kwargs: params,
            }).done(function (result) {
                self.database_bifurcation_count = result;
                if (result && result.length > 0) {
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
                Highcharts.chart('database_skill_container_graph', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Database Bifurcation',
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
                        pointFormat: ' <b> {series.name}:{point.y}</b>'
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
                                        self.database_wise_bifurcation(e, this.series.name, this.category);
                                    }
                                }
                            }
                        },
                        series: {
                            showInLegend: false
                        }
                    },
                    series: series,
                    colors: [
                        '#E6B333', '#4D8066','#FF6633', '#00B3E6', '#3366E6', '#99FF99', '#FF99E6', '#66991A', '#991AFF', '#4efcdf', '#791fb5', '#FF1A66', '#33FFCC',
                        '#E64D66', '#4DB380', '#FF4D4D', '#134040', '#6666FF',
                    ],
                });
            }else {
                // No data available, show a message in the donut container
                var container = document.getElementById('database_skill_container_graph');
                container.innerHTML = 'No Matching data available.';
                container.style.textAlign = 'center';
            }
        });
    },
        render_skill_distribution_in_type_container_graph: async function (status) {
            var self = this;
            var params = {}
            if (status === 'filter_total_skill' && self.skill_type_select_id !== 'Select' && self.pst_select_id !== 'Select'){ 
                params = { 'skill_type': self.skill_type_select_id, 'skill_name': self.pst_select_id };
            }
            // if (status == 'refresh_total_skill') params = {}
            if (status === 'refresh_total_skill' || (self.skill_type_select_id === 'Select' && self.pst_select_id === 'Select')) {
                params = {};
            }
            var defskillwisedistribution = this._rpc({
                model: 'skill_data_analytics_dashboard',
                method: 'get_skill_data_count_with_type',
                kwargs: params,
            }).done(function (result) {
                self.skill_wise_distribution_count = result;
                if (result && result.length > 0) {
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
                Highcharts.chart('skill_distribution_in_type_container_graph', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Total Skill Count',
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
                        pointFormat: ' <b> {series.name}:{point.y}</b>'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            // stacking: 'percent',
                            point: {
                                events: {
                                    click: function (e) {
                                        self.get_total_skill_wise_count(e, this.series.name, this.category);
                                    }
                                }
                            }
                        }
                    },
                    series: series,
                    colors: [
                        '#791fb5', '#FF1A66',  '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF','#33FFCC','#E6B333', '#3366E6', '#99FF99', '#FF99E6', '#66991A', '#4D8066',
                        '#FF6633', '#00B3E6', '#991AFF', '#4efcdf', '#E64D66'
                    ],
                });
            }else {
                    // No data available, show a message in the donut container
                    var container = document.getElementById('skill_distribution_in_type_container_graph');
                    container.innerHTML = 'No Matching data available.';
                    container.style.textAlign = 'center';
                }    
            });
        },
        reload: function () {
            window.location.href = this.href;
        },
    });
    core.action_registry.add('kw_resource_management.rcm_skill_data_dashboard', SkillAnalyticsDashboardView);
    return SkillAnalyticsDashboardView
});