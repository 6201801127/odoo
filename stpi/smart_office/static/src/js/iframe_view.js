odoo.define('smart_office', function (require) {
"use strict";

    var f_Registry = require('web.field_registry');
    var A_Field = require('web.AbstractField');

    var IFrameWidget = A_Field.extend({
        start: function() {
            var val = this.value;
            this.$el.html(val);
        }
    });
    f_Registry.add('iframe_view', IFrameWidget);
    return {
        IFrameWidget: IFrameWidget
    };
});