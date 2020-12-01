import uuid

from django.contrib import messages
from django.shortcuts import redirect, render, reverse

from tethys_sdk.gizmos import Button, DataTableView, SelectInput, TextInput
from tethys_sdk.permissions import login_required
from tethys_sdk.workspaces import app_workspace

from tethysext.atcore.models.file_database import FileDatabase, FileDatabaseClient, FileCollectionClient

from .app import Files as app
from .model import add_new_file_database, add_uploaded_files, get_all_file_databases, get_file_collections_for_database


@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    upload_files_button = Button(
        display_text='Upload Files',
        name='upload-files-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        href=reverse('files:upload_files')
    )

    add_file_database_button = Button(
        display_text='Add File Database',
        name='add-file-database-button',
        icon='glyphicon glyphicon-plus',
        style='warning',
        href=reverse('files:add_file_database')
    )

    table_rows = []
    all_file_databases = get_all_file_databases()

    for file_database in all_file_databases:
        table_rows.append(
            {
                'name': file_database['meta']['name'],
                'id': file_database['id'],
                'path': file_database['path'],
                'collection_count': file_database['collection_count'],
                'meta': file_database['meta'],
            }
        )

    if not len(table_rows) > 0:
        table_rows = None

    # file_databases_table = None
    # if len(table_rows) > 0:
    #     file_databases_table = DataTableView(
    #         column_names=('Database Name', 'ID', 'Path', 'Collection Count', 'Meta'),
    #         rows=table_rows,
    #         searching=False,
    #         orderClasses=False,
    #         lengthMenu=[[10, 25, 50, -1], [10, 25, 50, "All"]],
    #     )

    context = {
        'upload_files_button': upload_files_button,
        'add_file_database_button': add_file_database_button,
        'table_rows': table_rows,
    }

    return render(request, 'files/home.html', context)


@app_workspace
@login_required()
def upload_files(request, workspace):
    """
    Controller for the Add Dam page.
    """
    # Get databases from database
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    all_databases = session.query(FileDatabase).all()

    # default options
    database_select_options = [(database.meta['name'] + '-' + str(database.id), database.id) for database in all_databases]
    selected_database_id = None
    database_files = None

    # errors
    selected_database_error = ''
    database_files_error = ''

    # Handle form submission
    if request.POST and 'add-button' in request.POST:
        # Get values
        has_errors = False
        name = request.POST.get('name', None)
        notes = request.POST.get('notes', None)
        selected_database_id = request.POST.get('database-select', None)

        # Validate
        errors = []
        if not name:
            has_errors = True
            errors.append('Name is required')

        if not selected_database_id:
            has_errors = True
            errors.append('Selected Database is required')

        if request.FILES and 'upload-files' in request.FILES:
            database_files = request.FILES.getlist('upload-files')

        if not database_files or not len(database_files) > 0:
            has_errors = True
            errors.append('Files to upload are required')

        if not has_errors:
            add_uploaded_files(workspace=workspace, session=session,
                               name=name, notes=notes,
                               database_id=selected_database_id,
                               upload_files=database_files)
            return redirect(reverse('files:home'))

        messages.error(request, f"Please fix errors. ({', '.join(errors)})")

    add_button = Button(
        display_text='Add',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'upload-files-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('files:home')
    )

    name_input = TextInput(
        display_text='Name',
        name='name',
    )

    notes_input = TextInput(
        display_text='Notes',
        name='notes',
    )

    database_select_input = SelectInput(
        display_text='Database',
        name='database-select',
        multiple=False,
        options=database_select_options,
        initial=selected_database_id,
        error=selected_database_error,
    )

    context = {
        'add_button': add_button,
        'cancel_button': cancel_button,
        'name_input': name_input,
        'notes_input': notes_input,
        'database_select_input': database_select_input,
        'database_files_error': database_files_error,
    }

    return render(request, 'files/upload_files.html', context)


@app_workspace
@login_required()
def add_file_database(request, workspace):
    """
    Controller for creating a FileDatabase.
    """

    # Handle form submission
    if request.POST and 'add-button' in request.POST:
        # Get values
        has_errors = False
        name = request.POST.get('name', None)

        # Validate
        errors = []
        if not name:
            has_errors = True
            errors.append('Name is required')

        if not has_errors:
            add_new_file_database(db_directory=workspace.path, name=name)
            return redirect(reverse('files:home'))

        messages.error(request, f"Please fix errors. ({', '.join(errors)})")

    add_button = Button(
        display_text='Add',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-file-database-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('files:home')
    )

    name_input = TextInput(
        display_text='Name',
        name='name',
    )

    context = {
        'add_button': add_button,
        'cancel_button': cancel_button,
        'name_input': name_input,
    }

    return render(request, 'files/add_file_database.html', context)


@login_required()
def view_file_database(request, file_database_id):
    """
    Controller for the app home page.
    """
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    file_collections_for_database = get_file_collections_for_database(session, file_database_id)
    context = {
        'file_database_id': file_database_id,
        'file_collections': file_collections_for_database,
    }
    return render(request, 'files/view_file_database.html', context)


@login_required()
def delete_file_database(request, file_database_id):
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    file_database_client = FileDatabaseClient(session, file_database_id)
    for collection in file_database_client.instance.collections:
        file_database_client.delete_collection(collection.id)
    session.delete(file_database_client.instance)
    session.commit()
    return redirect(reverse('files:home'))


@login_required()
def delete_file_collection(request, file_collection_id):
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    file_collection_client = FileCollectionClient(session, file_collection_id)
    file_collection_client.delete()
    return redirect(reverse('files:home'))
