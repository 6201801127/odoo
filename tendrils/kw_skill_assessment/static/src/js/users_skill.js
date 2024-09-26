odoo.define('kw_skill_assessment.users_skill_report', function (require) {
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
    
    var SkillReportView = AbstractAction.extend(ControlPanelMixin, {
        init: function(parent, value) {
            this._super(parent, value);
            var skill_master = [];
            var self = this;
            if (value.tag == 'kw_skill_assessment.users_skill_report') {
                self._rpc({
                    route: '/users_skill-report',
                }, []).then(function(result){
                    self.skill_master = result
                    self.render();
                    self.href = window.location.href;
                    self.render_Datatable();
                });
            }
        },
        render_Datatable: function()
        {
            var skill_report_table = $('#skill_report').DataTable({
                dom: 'Bfrtip',
                buttons: [
                    'excel',
                    {
                        extend: 'pdf',
                        footer: 'true',
                        orientation: 'landscape',
                        text: 'PDF',
                        exportOptions: {
                            modifier: {
                                selected: true
                            }
                        }
                    },
                ],
                // paging: false,
                info : false, 
                columnDefs: [
                    { width: 200, targets: 0 },
                    { width: 100, targets: 1 },
                    { width: 100, targets: 2 },
                ],
                // processing: true,
                // ServerSide: true,
                // ajax: {
                //     url : 'scripts/server_processing.php',
                //     type: 'POST',
                // }
                
            });
            // $(document).ready(function() {
            //     $('#skill_report').DataTable( {
            //         "processing": true,
            //         "serverSide": true,
            //         "ajax": "/users_skill-report"
            //     } );
            // } );
            
            $(".buttons-excel").addClass("btn btn-primary");
            $(".buttons-excel").removeClass("dt-button");
            $(".buttons-pdf").addClass("btn btn-primary");
            $(".buttons-pdf").removeClass("dt-button");
            skill_report_table.columns().every(function () {
                var that = this;
    
                $('#skill_report_filter > input', this.header()).on('keyup change clear', function () {
                    if (that.search() !== this.value) {
                        that
                            .search(this.value)
                            .draw();
                    }
                });
            });
        },
        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            var self = this;
            return this._super();
        },
        render: function() {
            var super_render = this._super;
            var self = this;
            var kw_skill = QWeb.render( 'kw_skill_assessment.users_skill_report', {
                widget:self.skill_master,
            });
            $(kw_skill).prependTo(self.$el);
            return kw_skill;
        },
        reload: function () {
                window.location.href = this.href;
        },
    });
    core.action_registry.add('kw_skill_assessment.users_skill_report', SkillReportView);
    return SkillReportView
});

