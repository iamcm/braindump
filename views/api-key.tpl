
%def page():

	<div>
		<div class="col-sm-9">
			Api-key: {{vd['key']}}
		</div>

		<div class="col-sm-3">
			<form class="pull-right" action="" method="post">
				<input type="submit" class="btn btn-primary" value="Generate new api key" />
			</form>
		</div>
	</div>

%end


%rebase base vd=vd, page=page