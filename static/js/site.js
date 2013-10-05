var currentRequest = null;

$(document).ready(function(){
	$(document).on('click', '.item .title', function(){
		var content = $(this).next();
		$(content).toggle();
	});


	$('#search-input').focus().keyup(function(){
		if(this.value==''){
			$('#items').html('');
		} else {
			if(currentRequest) currentRequest.abort();

	        currentRequest = $.get('/search/items?ajax=1&name='+ this.value, function(html){
				
	        	$('#item-container').html(html);

	            if($('#item-container').children().length==1){
	                $('.content').show();                    
	            }
	        })
		}
	});	


    $('#form-add-item .tag').on('click', function(ev){
        ev.preventDefault();
        $(this).toggleClass('btn-primary');
    });

    $('#form-add-item').on('submit', function(ev){
    	$('.tag.btn-primary').each(function(){
            $('#form-add-item').append('<input type="hidden" name="tagIds[]" value="'+ this.id +'" />');
        });	
    });
    
});
