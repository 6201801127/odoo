odoo.define('kw_info_aboutus', function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var aboutus = AbstractAction.extend({
        template: 'aboutus',
    });
    core.action_registry.add('kw_info.aboutus', aboutus);
    });
    