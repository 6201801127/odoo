odoo.define('tendrils_internship.internship_apply', function (require) {
    "use strict";

    var core = require('web.core');

    var _t = core._t;

    var InternshipApply = core.Class.extend({
        init: function (parent, action) {
            this.action_manager = parent;
        },
        start: function () {
            var self = this;
            // Call the server-side method to check the condition
            this._rpc({
                model: 'tendrils_internship',
                method: 'btn_internship_apply',
            }).then(function(result) {
                // If the condition is not satisfied, display an alert
                if (!result.condition_satisfied) {
                    self.displayAlert(_t("Alert"), result.alert_message);
                }
            });
        },
        displayAlert: function (title, message) {
            alert(title + ': ' + message);
        }
    });

    core.action_registry.add('internship_apply', InternshipApply);

    return InternshipApply;
});
