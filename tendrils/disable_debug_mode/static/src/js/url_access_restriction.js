odoo.define("url_access_restriction.WarningMessage", function (require) {
  "use strcit";

  var core = require('web.core');
  var Widget = require('web.Widget');
  var ControlPanelMixin = require('web.ControlPanelMixin');

  var WarningMessage = Widget.extend(ControlPanelMixin, {
    'template': 'WarningMessageTemplate',
    init: function(parent, context) {
      this._super.apply(this, arguments);
      $('.o_control_panel').addClass('o_hidden');
    }
  });

  core.action_registry.add('warning_message', WarningMessage);
});
