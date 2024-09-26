function add_educational_row() {
    var table = document.getElementById('educational_details');
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    var row_id = table.rows[rowCount - 1].id;
    row.id = row_id.substring(0, 3) + (parseInt(row_id.substring(3)) + 1).toString();
    var colCount = table.rows[2].cells.length;
    var a = 0;
    for (var i = 0; i < colCount; i++) {
        var newcell = row.insertCell(i);

        newcell.innerHTML = table.rows[2].cells[i].innerHTML;

        var id_name = newcell.children[0].name.substring(0, newcell.children[0].name.lastIndexOf("_") + 1) + row.id.substring(3);
        newcell.children[0].name = id_name;
        newcell.children[0].id = id_name;
    }
}

function add_experience_row() {
    var table = document.getElementById('experience_details');
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    var row_id = table.rows[rowCount - 1].id;
    row.id = row_id.substring(0, 3) + (parseInt(row_id.substring(3)) + 1).toString();
    var colCount = table.rows[2].cells.length;
    var a = 0;
    for (var i = 0; i < colCount; i++) {
        var newcell = row.insertCell(i);

        newcell.innerHTML = table.rows[2].cells[i].innerHTML;

        var id_name = newcell.children[0].name.substring(0, newcell.children[0].name.lastIndexOf("_") + 1) + row.id.substring(3);
        newcell.children[0].name = id_name;
        newcell.children[0].id = id_name;
    }
}

function add_address_row() {
    var table = document.getElementById('address_details');
    console.log(table)

    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    var row_id = table.rows[rowCount - 1].id;
    row.id = row_id.substring(0, 3) + (parseInt(row_id.substring(3)) + 1).toString();
    var colCount = table.rows[2].cells.length;
    var a = 0;
    for (var i = 0; i < colCount; i++) {
        var newcell = row.insertCell(i);

        newcell.innerHTML = table.rows[2].cells[i].innerHTML;

        var id_name = newcell.children[0].name.substring(0, newcell.children[0].name.lastIndexOf("_") + 1) + row.id.substring(3);
        newcell.children[0].name = id_name;
        newcell.children[0].id = id_name;
    }
}

// function edudeleteRow(x) {
//     try {
//         var table = document.getElementById('educational_details');
//         var rowCount = table.rows.length;
//         if (rowCount == 3) {
//             table.children[0].setAttribute("style", "display:none;");
//         }
//         var row_index = x.parentElement.parentElement.rowIndex;
//         console.log(row_index);
//         table.deleteRow(row_index);

//     } catch (e) {
//         alert(e);
//     }
// }

function upTo(el, tagName) {
    tagName = tagName.toLowerCase();
    while (el && el.parentNode) {
      el = el.parentNode;
      if (el.tagName && el.tagName.toLowerCase() == tagName) {
        return el;
      }
    }
    return null;
  }    
  
function edudeleteRow(el) {
    var row = upTo(el, 'tr')
    if (row) row.parentNode.removeChild(row);
}

function expdeleteRow(x) {
    try {
        var table = document.getElementById('experience_details');
        var rowCount = table.rows.length;
        if (rowCount == 3) {
            table.children[0].setAttribute("style", "display:none;");
        }
        var row_index = x.parentElement.parentElement.rowIndex;
        table.deleteRow(row_index);

    } catch (e) {
        alert(e);
    }
}

function addressdeleteRow(x){
    try {
        var table = document.getElementById('address_details');
        var rowCount = table.rows.length;
        if (rowCount == 3) {
            table.children[0].setAttribute("style", "display:none;");
        }
        var row_index = x.parentElement.parentElement.rowIndex;
        table.deleteRow(row_index);

    } catch (e) {
        alert(e);
    }
}

function showCardValue() {
    document.getElementById("cardNo").value = document.getElementById("aadhar_no").value;
}

function hideCardValue(val) {
    document.getElementById("aadhar_no").value = val;
    var len = val.length;
    if (len > 1) {
        const regex = /\d(?=\d{4})/g;
        const substr = "X";
        document.getElementById("cardNo").value = val.replace(regex, substr);
        var cardNo = document.getElementById('cardNo').value;
        var aadhar_no = document.getElementById('aadhar_no').value;
        // $('#dvCCN').html(cardNo);
        // $('#dvRe').html(aadhar_no);
        console.log(cardNo);
        console.log(aadhar_no);
    }
}

function readPDFURL(input) {
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $(input).val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                // console.log($('#certificatePreview').val(),"before");
                $(input).closest('td').find('.certificate-link,.hidden-certificate').remove();
                $(input).attr('filedata', '"'+ e.target.result +'"');
                $(input).attr('filename', '"'+ input.files[0].name +'"');
                // console.log($('#certificatePreview').val(),"after");
            }
            reader.readAsDataURL(input.files[0]);
        }
        // reader.close();
    }
};
function readexperiencePDFURL(input) {
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $(input).val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('td').find('.certificate-link,.hidden-experience-doc').remove();
                $(input).attr('filedata', '"'+ e.target.result +'"');
                $(input).attr('filename', '"'+ input.files[0].name +'"');
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
};

function readPaymentDocumentURL(input)
{
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#other_document').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

//function readSignatureDocumentURL(input)
//{
//    if (input.files && input.files[0]) {
//        console.log(input.files[0].name)
//        var reader = new FileReader();
//        reader.onload = function(e) {
//            $(input).closest('div').find('.signature-link,.hidden-signature').remove();
//            $(input).attr('filedata', e.target.result);
//            $(input).attr('filename', input.files[0].name);
//        }
//        reader.readAsDataURL(input.files[0]);
//    }
//}
function readotherDocumentURL(input)
{
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#other_document').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('div').find('.other-doc-link,.hidden-other-doc').remove();
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

function readDobDocumentURL(input){
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#upload_dob_doc').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('div').find('.dob-doc-link,.hidden-dob-doc').remove();
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

function readAadhaarDocumentURL(input){
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#upload_aadhar_upload').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('div').find('.aadhar-upload-link,.hidden-aadhar-upload').remove();
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

function readPANDocumentURL(input){
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#upload_pan_upload').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('div').find('.pan-upload-link,.hidden-pan-upload').remove();
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

function readNationalityDocumentURL(input){
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#upload_nationality_upload').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('div').find('.nationality-upload-link,.hidden-nationality-upload').remove();
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

function readCertificateDocumentURL(input){
    if (input.files && input.files[0]) {
        if (input.files[0].size > 1 * 1024 * 1024){
            $('#upload_certificate_upload').val('');
            alert('Maximum size should be 1MB.')
        }
        else {
            console.log(input.files[0].name)
            var reader = new FileReader();
            reader.onload = function(e) {
                $(input).closest('div').find('.certificate-upload-link,.hidden-certificate-upload').remove();
                $(input).attr('filedata', e.target.result);
                $(input).attr('filename', input.files[0].name);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}

function changeRelativeCcs(input){
    var relative_ccs = input.options[input.selectedIndex].text;
    if(relative_ccs.toUpperCase() == 'YES'){
        $('.relative_ccs_name').removeClass('d-none');
    }
    else{
        $('.relative_ccs_name').addClass('d-none');
    }
}

function changeNationality(input){
    var nationality = input.options[input.selectedIndex].text;
    if(nationality.toUpperCase() == 'INDIAN' || nationality.toUpperCase() == 'SELECT'){
        $('.upload_nationality_upload').addClass('d-none');
    }
    else{
        $('.upload_nationality_upload').removeClass('d-none');
    }
}

function changePhysicallyHandicapped(input){
    var physicallyHandicapped = input.options[input.selectedIndex].text;
    if(physicallyHandicapped.toUpperCase() == 'YES'){
        $('.differently_abled').removeClass('d-none');
    }
    else{
        $('.differently_abled').addClass('d-none');
    }
}

function printApplication(elem)
  {
      var mywindow = window.open();
      var content = document.getElementById(elem).innerHTML;
      var realContent = document.body.innerHTML;
      mywindow.document.write(content);
      mywindow.document.close(); // necessary for IE >= 10
      mywindow.focus(); // necessary for IE >= 10*/
      mywindow.print();
      document.body.innerHTML = realContent;
      mywindow.close();
      return true;
  }
