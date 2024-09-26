odoo.define('kw_budget.CustomBudgetWidget', function (require) {
    'use strict';

    var FieldFloat = require('web.FieldFloat');
    var core = require('web.core');

    var CustomBudgetWidget = FieldFloat.extend({
        className: 'o_budget_field',

        // Override the _render function to customize rendering
        _render: function () {
            this._super.apply(this, arguments); // Call parent _render function
            console.log('DDDDDDDDD')
            var value = this.value;
            var $content = this.$el;

            // Add classes based on the value
            if (parseFloat(value) < 0) {
                $content.addClass('negative');
            } else if (parseFloat(value) > 0) {
                $content.addClass('positive');
            }
        }
    });

    // Register the custom widget in the form widget registry
    core.form_widget_registry.add('custom_budget_widget', CustomBudgetWidget);

    return CustomBudgetWidget;
});
