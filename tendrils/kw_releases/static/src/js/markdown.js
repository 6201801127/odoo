
//markdown integration

odoo.define('kw_releases.kw_markdown_md', function (require) { 
	'use strict';
	$(function(){
		
			// code for add calss in tables
			$("#mdfilewrapper").find('table').addClass('table table-stripped table-bordered');

			// code for set id in heading
			var hdngIde;
				$('#mdfilewrapper h1, #mdfilewrapper h2').each(function(){
				hdngIde = $(this).text().split(' ').join('-').toLowerCase();
				$(this).prop({'id': hdngIde});
			});

			
			$('.md_source').hide();	
			var converter = new showdown.Converter({
					tables: true, 
					tasklists: true
			})
		
			var resMdData 		=''
			$('.md_source').each(function(){
				resMdData 		= $(this).html();
			
				$(this).empty()
	
				$('#mdfilewrapper_'+$(this).attr('id')).html(converter.makeHtml(resMdData));

			});
				
	});



});