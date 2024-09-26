odoo.define('enterprise_backend_theme.ArchieveUnarchieve', function (require) {
    "use strict";
    
    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
            init: function(viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var model = 'True';
                if(model) {
                    session.user_has_group('enterprise_backend_theme.group_archive').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                }
            },
    });
    });
    