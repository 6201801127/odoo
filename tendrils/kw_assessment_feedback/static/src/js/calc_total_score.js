odoo.define('kw_assessment_feedback.totalScore', function(require) {
    "use strict";
    var rpc = require('web.rpc');
    
    $('#miltable input').keyup(function(){
        let score = parseFloat($(this).val())
        if (isNaN(score)) {
            $(this).val('');
            return false
        }
        calculate_total();
    });
    
    
    let full_mark = $('#assessment_total_score').val();


    function calculate_total(){
        var total = 0;
        $('.feedback_assessment_items').each(function(){
            var el = $(this).find('input');
            var maxval = el.closest('tr').find('.assessment_max_value').attr('maxval');
            if(!isNaN(el.val()) && parseFloat(el.val()) <= parseFloat(maxval)){
                total += parseFloat(el.val());
            }else{
                el.val('');
            }
    
            console.log(maxval)

        });
        var perc = (total / full_mark * 100).toFixed(2);
        $('#totalScoreInput').html(perc);
        show_performance_grade();
    }

    

    

   function show_performance_grade(){
       var total_score = parseFloat($('#totalScoreInput').html());
       if(isNaN(total_score))
            return false;
        var str = '';
       $('#performance_weightage_id').find("option").each(function(){
            var el = $(this);
            var from_val = isNaN(el.attr('from')) ? 0 : parseFloat(el.attr('from'))
            if(!isNaN(el.attr('to')) && from_val < total_score && parseFloat(el.attr('to')) > total_score){
                str = el.html();
                $('#performance_grade').html(str);
                return true;
            }
       });
       
   }

});



