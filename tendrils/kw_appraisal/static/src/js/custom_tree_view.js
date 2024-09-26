odoo.define('my_module.sticky_header_column', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderHeader: function () {
            var $header = this._super.apply(this, arguments);

            var $thead2 = $header.find('tr th:nth-child(2)');
            var $thead3 = $header.find('tr th:nth-child(3)');
            var $thead4 = $header.find('tr th:nth-child(4)');
            var $thead5 = $header.find('tr th:nth-child(5)');
            var $thead6 = $header.find('tr th:nth-child(6)');
            var $thead7 = $header.find('tr th:nth-child(7)');
            var $thead8 = $header.find('tr th:nth-child(8)');
            var $thead9 = $header.find('tr th:nth-child(9)');
            var $thead10 = $header.find('tr th:nth-child(10)');


            console.log($thead2.html(), $thead3.html(), $thead4.html(), $thead5.html(), $thead6.html(), $thead7.html(), $thead8.html(), $thead9.html());

            if ($thead2.html() === 'Employee Code' && $thead3.html() === 'Employee' && $thead4.html() === 'Designation' && $thead5.html() === 'Joining Date' && $thead6.html() === 'Total Experience' && $thead7.html() === 'Grade/Band' ) {
                console.log('Inside if');
                $thead2.addClass('o_column_header1');
                $thead3.addClass('o_column_header2');
                $thead4.addClass('o_column_header3');
                $thead5.addClass('o_column_header4');
                $thead6.addClass('o_column_header5');
                $thead7.addClass('o_column_header6');
                $thead8.addClass('o_column_header7');
                $thead9.addClass('o_column_header8');
                $thead10.addClass('o_column_header9');

            }

            return $header;
        },
    });
});