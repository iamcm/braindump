
function watchDeleteClicks(){
	$('.deleteLink').on('click', function(){
        return confirm('Are you sure you want to delete this '+ $(this).attr('entity'))
    })	
}

$(document).ready(function(){
   watchDeleteClicks();
});



