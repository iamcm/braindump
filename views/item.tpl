
%def page():

<form id="form-add-item" class="form-horizontal" role="form" action="" method="post">

	<div class="form-group">
		<label for="inputTitle" class="col-sm-2 control-label">Title</label>
		<div class="col-sm-6">
			<input type="text" class="form-control" id="inputTitle" placeholder="Title" name="title" value="{{vd['item'].title if vd['item'].title else ''}}">
		</div>
	</div>

	<div class="form-group">
		<label for="inputContent" class="col-sm-2 control-label">Content</label>
		<div class="col-sm-6">
			<textarea name="content" class="form-control" id="inputContent">{{vd['item'].content if vd['item'].content else ''}}</textarea>
		</div>
	</div>

	<div class="form-group">
		<label for="inputContent" class="col-sm-2 control-label">Tags</label>
		<div class="col-sm-6">
			%for t in vd['tags']:
				<button class="tag my5 btn {{'btn-primary' if str(t._id) in vd['item'].tagIds else '' }}" id="{{t._id}}">{{t.name}}</button>
			%end
		</div>
	</div>

	<div class="form-group">
		<label for="inputNewTag" class="col-sm-2 control-label">New Tag</label>
		<div class="col-sm-6">
			<input type="text" class="form-control" id="inputNewTag" placeholder="New Tag" name="tag" />
		</div>
	</div>

	<div class="form-group">
		<div class="col-sm-offset-2 col-sm-4">
			<button type="submit" class="btn btn-default">Save</button>
		</div>
	</div>
</form>

%end


%def js():
<script type="text/javascript">

        tinymce.init({
            selector: "textarea",
            plugins: ["link"],
            menubar: false,
            toolbar: 'bold italic | link',
            statusbar: false,
            tabfocus_elements: ":prev,:next"
        });

</script>
%end

%rebase base vd=vd, page=page, js=js