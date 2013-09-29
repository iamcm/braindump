
%def page():
	
	<div class="row">
		<a href="/tag" class="btn btn-primary">Add new tag</a>
	</div>
	<hr />

	%for t in vd['tags']:
	<div class="row">
		<div class="col-sm-10">
			{{t.name}}
		</div>

		<div class="col-sm-1">
			<a href="/tag/{{t._id}}/edit">Edit</a>
		</div>

		<div class="col-sm-1">
			<a href="/tag/{{t._id}}/delete">Delete</a>
		</div>
	</div>
	<hr />
	%end

%end


%rebase base vd=vd, page=page