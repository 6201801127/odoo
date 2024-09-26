odoo.define('kw_onboarding', function (require) {
    'use strict';
   // var ajax = require('web.ajax');
   $(document).ready(function()
   {   
    //    var slct_option = $('#drpLanguage').html();
    //    var row_ind = $('#lang_tbl tr').length;
    //    var lbl = 1;
    //    $('#lang_tbl').on('click', ".add-row", function() 
    //    {
    //        $(this).parents('tbody').append('<tr>\
    //        <td><select name="drpLanguage'+row_ind+'" id="drpLanguage'+row_ind+'">'+slct_option+'</select></td>\
    //        <td>\
    //            <input type="radio" id="rdnReading_0" name="rdnReading1' + lbl +'" value="good" /> Good\
    //            <input type="radio" id="rdnReading_1" name="rdnReading1' + lbl +'" value="fair" /> Fair\
    //            <input type="radio" id="rdnReading_2" name="rdnReading1' + lbl +'" value="slight" /> Slight\
    //        </td>\
    //        <td>\
    //            <input type="radio" name="rdnWriting1' + lbl +'" id="rdnWriting_0" value="good" /> Good\
    //            <input type="radio" name="rdnWriting1' + lbl +'" id="rdnWriting_1" value="fair" /> Fair\
    //            <input type="radio" name="rdnWriting1' + lbl +'" id="rdnWriting_2" value="slight" /> Slight\
    //        </td>\
    //        <td>\
    //            <input type="radio" name="rdnSpeaking1' + lbl +'" id="rdnSpeaking_0" value="good" /> Good\
    //            <input type="radio" name="rdnSpeaking1' + lbl +'" id="rdnSpeaking_1" value="fair" /> Fair\
    //            <input type="radio" name="rdnSpeaking1' + lbl +'" id="rdnSpeaking_2" value="slight" /> Slight\
    //        </td>\
    //        <td>\
    //            <input type="radio" name="rdnUnderstanding1' + lbl +'" id="rdnUnderstanding_0" value="good" /> Good\
    //            <input type="radio" name="rdnUnderstanding1' + lbl +'" id="rdnUnderstanding_1" value="fair" /> Fair\
    //            <input type="radio" name="rdnUnderstanding1' + lbl +'" id="rdnUnderstanding_2" value="slight" /> Slight\
    //        </td>\
    //        <td width="10%">\
    //            <center> <button class="btn btn-danger close_row">Close</button> </center>\
    //        </td>\
    //        </tr>');
           
    //        row_ind ++;
    //        lbl ++;
    //    });

    $("button.add-row").on('click', function() {
        var cltr  = $(this).closest('.tr_clone');
        var nearclone = cltr.clone();
        cltr.after(nearclone);
        
        nearclone.append("<center><button class='btn btn-danger close_row'>Close</button></center>");
    });
    
        $('#lang_tbl').on('click', ".close_row", function() {
           $(this).parents('tr').remove();
       });
   });
    
});