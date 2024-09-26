odoo.define('kw_accounting.partner_dashboard_page', function (require) {
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

    var LedgerReport = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'kw_accounting.partner_dashboard_page') {
                self._rpc({
                    model: 'account.account',
                    method: 'get_ledger_report_data',
                }, []).then(function (result) {
                    console.log(result)
                }).done(function () {
                    self.render();
                    self.renderPartnerType();
                    self.renderIndustries();
                    self.renderTechnologies();
                    self.renderGeographicsOffered();
                    self.renderServices();
                    self.href = window.location.href;
                });
            }
        },
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var ledger_report_page = QWeb.render('kw_accounting.partner_dashboard_page', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(ledger_report_page).prependTo(self.$el);
            return ledger_report_page
        },
        renderPartnerType: async function () {
            Highcharts.chart('partnerType', {
                chart: {
                    type: 'column'
                },
                title: {
                    align: 'left',
                    text: 'Partner Types'
                },

                accessibility: {
                    announceNewData: {
                        enabled: true
                    }
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
                credits: { enabled: false },
                plotOptions: {
                    series: {
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            format: '{point.y:.1f}%'
                        }
                    }
                },

                tooltip: {
                    headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                    pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of total<br/>'
                },

                series: [
                    {
                        name: 'Partner Types',
                        colorByPoint: true,
                        data: [
                            {
                                name: 'OEM',
                                y: 63.06,
                                drilldown: 'OEM'
                            },
                            {
                                name: 'Global Accreditors',
                                y: 19.84,
                                drilldown: 'Global Accreditors'
                            },
                            {
                                name: 'Large Partners/MSI',
                                y: 4.18,
                                drilldown: 'Large Partners/MSI'
                            },
                            {
                                name: 'Multilateral Aid Organizations',
                                y: 4.12,
                                drilldown: 'Multilateral Aid Organizations'
                            },
                            {
                                name: 'Nodal Agencies',
                                y: 2.33,
                                drilldown: 'Nodal Agencies'
                            },
                            {
                                name: 'BD Partners',
                                y: 0.45,
                                drilldown: 'BD Partners'
                            },
                            {
                                name: 'Small/Similar',
                                y: 18.582,
                                drilldown: 'Small/Similar'
                            },
                            {
                                name: 'System Integrator',
                                y: 15.582,
                                drilldown: 'System Integrator'
                            },
                            {
                                name: 'Vendor',
                                y: 21.582,
                                drilldown: 'Vendor'
                            },
                            {
                                name: 'CON-IT-ISP',
                                y: 17.582,
                                drilldown: 'CON-IT-ISP'
                            },

                        ]
                    }
                ],
                // drilldown: {
                //     breadcrumbs: {
                //         position: {
                //             align: 'right'
                //         }
                //     },
                //     series: [
                //         {
                //             name: 'Chrome',
                //             id: 'Chrome',
                //             data: [
                //                 [
                //                     'v65.0',
                //                     0.1
                //                 ],
                //                 [
                //                     'v64.0',
                //                     1.3
                //                 ],
                //                 [
                //                     'v63.0',
                //                     53.02
                //                 ],
                //                 [
                //                     'v62.0',
                //                     1.4
                //                 ],
                //                 [
                //                     'v61.0',
                //                     0.88
                //                 ],
                //                 [
                //                     'v60.0',
                //                     0.56
                //                 ],
                //                 [
                //                     'v59.0',
                //                     0.45
                //                 ],
                //                 [
                //                     'v58.0',
                //                     0.49
                //                 ],
                //                 [
                //                     'v57.0',
                //                     0.32
                //                 ],
                //                 [
                //                     'v56.0',
                //                     0.29
                //                 ],
                //                 [
                //                     'v55.0',
                //                     0.79
                //                 ],
                //                 [
                //                     'v54.0',
                //                     0.18
                //                 ],
                //                 [
                //                     'v51.0',
                //                     0.13
                //                 ],
                //                 [
                //                     'v49.0',
                //                     2.16
                //                 ],
                //                 [
                //                     'v48.0',
                //                     0.13
                //                 ],
                //                 [
                //                     'v47.0',
                //                     0.11
                //                 ],
                //                 [
                //                     'v43.0',
                //                     0.17
                //                 ],
                //                 [
                //                     'v29.0',
                //                     0.26
                //                 ]
                //             ]
                //         },
                //         {
                //             name: 'Firefox',
                //             id: 'Firefox',
                //             data: [
                //                 [
                //                     'v58.0',
                //                     1.02
                //                 ],
                //                 [
                //                     'v57.0',
                //                     7.36
                //                 ],
                //                 [
                //                     'v56.0',
                //                     0.35
                //                 ],
                //                 [
                //                     'v55.0',
                //                     0.11
                //                 ],
                //                 [
                //                     'v54.0',
                //                     0.1
                //                 ],
                //                 [
                //                     'v52.0',
                //                     0.95
                //                 ],
                //                 [
                //                     'v51.0',
                //                     0.15
                //                 ],
                //                 [
                //                     'v50.0',
                //                     0.1
                //                 ],
                //                 [
                //                     'v48.0',
                //                     0.31
                //                 ],
                //                 [
                //                     'v47.0',
                //                     0.12
                //                 ]
                //             ]
                //         },
                //         {
                //             name: 'Internet Explorer',
                //             id: 'Internet Explorer',
                //             data: [
                //                 [
                //                     'v11.0',
                //                     6.2
                //                 ],
                //                 [
                //                     'v10.0',
                //                     0.29
                //                 ],
                //                 [
                //                     'v9.0',
                //                     0.27
                //                 ],
                //                 [
                //                     'v8.0',
                //                     0.47
                //                 ]
                //             ]
                //         },
                //         {
                //             name: 'Safari',
                //             id: 'Safari',
                //             data: [
                //                 [
                //                     'v11.0',
                //                     3.39
                //                 ],
                //                 [
                //                     'v10.1',
                //                     0.96
                //                 ],
                //                 [
                //                     'v10.0',
                //                     0.36
                //                 ],
                //                 [
                //                     'v9.1',
                //                     0.54
                //                 ],
                //                 [
                //                     'v9.0',
                //                     0.13
                //                 ],
                //                 [
                //                     'v5.1',
                //                     0.2
                //                 ]
                //             ]
                //         },
                //         {
                //             name: 'Edge',
                //             id: 'Edge',
                //             data: [
                //                 [
                //                     'v16',
                //                     2.6
                //                 ],
                //                 [
                //                     'v15',
                //                     0.92
                //                 ],
                //                 [
                //                     'v14',
                //                     0.4
                //                 ],
                //                 [
                //                     'v13',
                //                     0.1
                //                 ]
                //             ]
                //         },
                //         {
                //             name: 'Opera',
                //             id: 'Opera',
                //             data: [
                //                 [
                //                     'v50.0',
                //                     0.96
                //                 ],
                //                 [
                //                     'v49.0',
                //                     0.82
                //                 ],
                //                 [
                //                     'v12.1',
                //                     0.14
                //                 ]
                //             ]
                //         }
                //     ]
                // }
            });
        },
        renderIndustries: async function () {
            Highcharts.chart('industries', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Industries'
                },

                xAxis: {
                    type: 'category',
                    labels: {
                        autoRotation: [-45, -90],
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Count'
                    }
                },
                legend: {
                    enabled: false
                },
                tooltip: {
                    pointFormat: 'Count: <b>{point.y:.1f}</b>'
                },
                series: [{
                    name: 'Population',
                    colors: [
                        '#9b20d9', '#9215ac', '#861ec9', '#7a17e6', '#7010f9', '#691af3',
                        '#6225ed', '#5b30e7', '#533be1', '#4c46db', '#4551d5', '#3e5ccf',
                        '#3667c9', '#2f72c3', '#277dbd', '#1f88b7', '#1693b1', '#0a9eaa',
                        '#03c69b', '#00f194'
                    ],
                    colorByPoint: true,
                    groupPadding: 0,
                    data: [

                        ['Administrative', 37.33],
                        ['Agriculture', 31.18],
                        ['Construction', 27.79],
                        ['Education', 22.23],
                        ['Energy supply', 21.91],
                        ['Entertainment', 21.74],
                        ['Extraterritorial', 21.32],
                        ['Finance/Insurance', 20.89],
                        ['Food', 20.67],
                        ['Health/Social', 19.11],
                        ['Households', 16.45],
                        ['IT/Communication', 16.38],
                        ['Manufacturing', 15.41],
                        ['Mining', 15.25],
                        ['Other Services', 14.974],
                        ['Public Administration', 14.970],
                        ['Real Estate', 14.86],
                        ['Scientific', 14.16],
                        ['Transportation', 13.79],
                        ['Water supply', 13.79],
                        ['Wholesale/Retail', 13.79]
                    ],
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        inside: true,
                        verticalAlign: 'top',
                        format: '{point.y:.1f}', // one decimal
                        y: 10, // 10 pixels down from the top
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }]
            });

        },
        renderTechnologies: async function () {
            Highcharts.chart('Technologies', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Technologies'
                },

                xAxis: {
                    type: 'category',
                    labels: {
                        autoRotation: [-45, -90],
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Count'
                    }
                },
                legend: {
                    enabled: false
                },
                tooltip: {
                    pointFormat: 'Count: <b>{point.y:.1f}</b>'
                },
                series: [{
                    name: 'Population',
                    colors: [
                        '#9b20d9', '#9215ac', '#861ec9', '#7a17e6', '#7010f9', '#691af3',
                        '#6225ed', '#5b30e7', '#533be1', '#4c46db', '#4551d5', '#3e5ccf',
                        '#3667c9', '#2f72c3', '#277dbd', '#1f88b7', '#1693b1', '#0a9eaa',
                        '#03c69b', '#00f194'
                    ],
                    colorByPoint: true,
                    groupPadding: 0,
                    data: [

                        ['AI OEM', 37.33],
                        ['Application Development', 31.18],
                        ['Data Analytics', 27.79],
                        ['IT Infra Mgmt.', 22.23],
                        ['Nodal Agency', 21.74],

                    ],
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        inside: true,
                        verticalAlign: 'top',
                        format: '{point.y:.1f}', // one decimal
                        y: 10, // 10 pixels down from the top
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }]
            });

        },
        renderGeographicsOffered: async function () {
            // Data retrieved from https://fas.org/issues/nuclear-weapons/status-world-nuclear-forces/
            Highcharts.chart('geographiesOffered', {
                chart: {
                    type: 'area'
                },

                title: {
                    text: 'Geographies Offered'
                },
                xAxis: {
                    allowDecimals: false,
                    accessibility: {
                        rangeDescription: 'Range: 1940 to 2017.'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Count'
                    }
                },
                tooltip: {
                    pointFormat: '{series.name} had stockpiled <b>{point.y:,.0f}</b><br/>warheads in {point.x}'
                },
                plotOptions: {
                    area: {
                        pointStart: 1940,
                        marker: {
                            enabled: false,
                            symbol: 'circle',
                            radius: 2,
                            states: {
                                hover: {
                                    enabled: true
                                }
                            }
                        }
                    }
                },
                series: [{
                    name: 'India',
                    data: [
                        null, null, null, null, null, 2, 9, 13, 50, 170, 299, 438, 841,
                        1169, 1703, 2422, 3692, 5543, 7345, 12298, 18638, 22229, 25540,
                        28133, 29463, 31139, 31175, 31255, 29561, 27552, 26008, 25830,
                        26516, 27835, 28537, 27519, 25914, 25542, 24418, 24138, 24104,
                        23208, 22886, 23305, 23459, 23368, 23317, 23575, 23205, 22217,
                        21392, 19008, 13708, 11511, 10979, 10904, 11011, 10903, 10732,
                        10685, 10577, 10526, 10457, 10027, 8570, 8360, 7853, 5709, 5273,
                        5113, 5066, 4897, 4881, 4804, 4717, 4571, 4018, 3822, 3785, 3805,
                        3750, 3708, 3708
                    ]
                }, {
                    name: 'Export',
                    data: [null, null, null, null, null, null, null, null, null,
                        1, 5, 25, 50, 120, 150, 200, 426, 660, 863, 1048, 1627, 2492,
                        3346, 4259, 5242, 6144, 7091, 8400, 9490, 10671, 11736, 13279,
                        14600, 15878, 17286, 19235, 22165, 24281, 26169, 28258, 30665,
                        32146, 33486, 35130, 36825, 38582, 40159, 38107, 36538, 35078,
                        32980, 29154, 26734, 24403, 21339, 18179, 15942, 15442, 14368,
                        13188, 12188, 11152, 10114, 9076, 8038, 7000, 6643, 6286, 5929,
                        5527, 5215, 4858, 4750, 4650, 4600, 4500, 4490, 4300, 4350, 4330,
                        4310, 4495, 4477
                    ]
                }]
            });

        },
        renderServices: async function () {
            Highcharts.chart('services', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: 'Services'
                },
                
                xAxis: {
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                },
                yAxis: {
                    title: {
                        text: 'Count'
                    }
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: false
                    }
                },
                series: [{
                    name: 'Nodal Agency',
                    data: [16.0, 18.2, 23.1, 27.9, 32.2, 36.4, 39.8, 38.4, 35.5, 29.2,
                        22.0, 17.8]
                }, {
                    name: 'RPA',
                    data: [-2.9, -3.6, -0.6, 4.8, 10.2, 14.5, 17.6, 16.5, 12.0, 6.5,
                        2.0, -0.9]
                },
                {
                    name: 'Security',
                    data: [-2.9, -3.6, -0.6, 4.8, 10.2, 14.5, 17.6, 16.5, 12.0, 6.5,
                        2.0, -0.9]
                }]
            });            
        },

        reload: function () {
            window.location.href = this.href;
        },
    });

    core.action_registry.add('kw_accounting.partner_dashboard_page', LedgerReport);
    return LedgerReport
});
