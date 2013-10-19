from FormBinder import FormBuilder, FormItem, Types

def item_validator(form):
	errors = []

	if form.get_value('tagIds') is None and form.get_value('newTag') is None:
		errors.append('Please select or create a tag')

	return errors

def ItemForm(tags=None, entity=None):
    formitems = []
    formitems.append(FormItem(Types.HIDDEN_TYPE, '_id', id='_id'))
    formitems.append(FormItem(Types.TEXT_TYPE, 'title', id='title', label_text='Title', class_name="form-control", required=True))
    formitems.append(FormItem(Types.TEXTAREA_TYPE, 'content', id='content', label_text='Content', class_name="form-control"))
    formitems.append(FormItem(Types.MULTI_SELECT_TYPE, 'tagIds', id='tagIds', label_text='Tags', class_name="form-control", select_list_items=tags))
    formitems.append(FormItem(Types.TEXT_TYPE, 'newTag', id='newTag', label_text='New Tag', class_name="form-control"))

    return FormBuilder(formitems, item_validator, entity=entity)


def TagForm(entity=None):
    formitems = []
    formitems.append(FormItem(Types.HIDDEN_TYPE, '_id', id='_id'))
    formitems.append(FormItem(Types.TEXT_TYPE, 'name', id='name', label_text='Name', class_name="form-control", required=True))

    return FormBuilder(formitems, entity=entity)

