
%def page():

<form class="form-horizontal" role="form" action="" method="post">

	<div class="form-group">
		<label for="inputName" class="col-sm-2 control-label">Name</label>
		<div class="col-sm-4">
			<input type="text" class="form-control" id="inputName" placeholder="Name" name="name" value="{{vd['tag'].name if vd['tag'].name else ''}}">
		</div>
	</div>

	<div class="form-group">
		<div class="col-sm-offset-2 col-sm-4">
			<button type="submit" class="btn btn-default">Save</button>
		</div>
	</div>
</form>

%end


%rebase base vd=vd, page=page