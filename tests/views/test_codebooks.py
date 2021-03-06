# flake8: noqa

import pytest
import mock

from occams.testing import USERID, make_environ, get_csrf_token

@pytest.mark.webtest
class TestCodebooks:

    @pytest.fixture(autouse=True)
    def populate(self, app, db_session):
        from datetime import date

        import transaction
        from occams_datastore import models as datastore
        from occams_studies import models as studies

        # Any view-dependent data goes here
        with transaction.manager:
            user = datastore.User(key=USERID)
            drsc = studies.Study(
                name=u'drsc',
                title=u'DRSC',
                short_title=u'dr',
                code=u'drs',
                consent_date=date.today(),
                is_randomized=False)
            ucsd = studies.Study(
                name=u'ucsd',
                title=u'UCSD',
                short_title=u'ucsd',
                code=u'ucsd',
                consent_date=date.today(),
                is_randomized=False
            )
            db_session.add(user)
            db_session.add(drsc)
            db_session.add(ucsd)
            db_session.flush()

    @pytest.mark.parametrize('group', ['administrator'])
    def test_qds_upload_validate(self, app, group, datadir):

        url = '/imports/codebooks/qds/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'study': u'DRSC'
        }

        qds = datadir.join('qds_input_fixture.csv').open()
        qds_data = qds.read()

        response = app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.csv', qds_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        qds.close()

        assert response.status_code == 200
        assert u'Test_Schema_Title' in response.body
        assert u'Test Schema Title' in response.body
        assert u'Codebook Import Status' in response.body
        assert u'2015-08-11' in response.body
        assert u'Fields evaluated' in response.body

    @pytest.mark.parametrize('group', ['administrator'])
    def test_occams_upload_validate(self, app, group, datadir):

        url = '/imports/codebooks/occams/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'study': u'DRSC'
        }

        codebook = datadir.join('/codebook.csv').open()
        csv_data = codebook.read()

        response = app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.csv', csv_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        codebook.close()

        assert response.status_code == 200
        assert u'ClinicalAssessment595vitd' in response.body
        assert u'Codebook Import Status' in response.body
        assert u'2014-10-23' in response.body
        assert u'Fields evaluated' in response.body

    @pytest.mark.parametrize('group', ['administrator'])
    def test_iform_upload_validate(self, app, group, datadir):

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'study': u'DRSC'
        }

        iform = datadir.join('iform_input_fixture.json').open()
        json_data = iform.read()

        response = app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.json', json_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        iform.close()

        assert u'test_595_hiv_test_v04' in response.body
        assert u'Codebook Import Status' in response.body
        assert u'2013-10-21' in response.body
        assert u'Fields evaluated' in response.body

    @pytest.mark.parametrize('group', ['administrator'])
    def test_qds_insert(self, app, db_session, group, datadir):
        import datetime
        from occams_datastore import models as datastore

        url = '/imports/codebooks/qds/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'study': u'DRSC',
            'delimiter': u'comma'
        }

        qds = datadir.join('qds_input_fixture.csv').open()
        qds_data = qds.read()

        app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.csv', qds_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        qds.close()

        form = db_session.query(datastore.Schema).one()
        attributes = db_session.query(datastore.Attribute).filter(
            datastore.Schema.id == form.id).order_by(
            datastore.Attribute.name).all()

        assert form.name == u'Test_Schema_Title'
        assert form.title == u'Test Schema Title'
        assert form.publish_date == datetime.date(2015, 8, 11)
        assert attributes[0].name == u'BIRTHSEX'
        assert attributes[1].name == u'GENDER'
        assert attributes[2].name == u'TODAY'
        assert attributes[0].type == u'choice'
        assert attributes[1].type == u'choice'
        assert attributes[2].type == u'string'

    @pytest.mark.parametrize('group', ['administrator'])
    def test_occams_codebook_insert(self, app, db_session, group, datadir):
        import datetime
        from occams_datastore import models as datastore

        url = '/imports/codebooks/occams/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'study': u'DRSC',
            'delimiter': u'comma'
        }

        codebook = datadir.join('codebook.csv').open()
        csv_data = codebook.read()

        app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.csv', csv_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        codebook.close()

        form = db_session.query(datastore.Schema).one()
        attributes = db_session.query(datastore.Attribute).filter(
            datastore.Schema.id == form.id).order_by(
            datastore.Attribute.name).all()

        assert form.name == u'ClinicalAssessment595vitd'
        assert form.title == u'595 Vitamin D - Clinical Assessment'
        assert form.publish_date == datetime.date(2014, 10, 23)
        assert attributes[0].name == u'cont'
        assert attributes[2].name == u'frac'

        expected_title = u'Has the subject had any fractures since the visit?'
        assert attributes[2].title == expected_title

        assert attributes[2].choices['0'].title == u'No'


    @pytest.mark.parametrize('group', ['administrator'])
    def test_iform_insert(self, app, db_session, group, datadir):
        import datetime
        from occams_datastore import models as datastore

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'study': u'DRSC'
        }

        iform = datadir.join('iform_input_fixture.json').open()
        json_data = iform.read()

        app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.json', json_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        iform.close()

        form = db_session.query(datastore.Schema).one()
        attributes = db_session.query(datastore.Attribute).filter(
            datastore.Schema.id == form.id).order_by(
            datastore.Attribute.name).all()

        assert form.name == u'test_595_hiv_test_v04'
        assert form.title == u'test_595_hiv_test_v04'
        assert form.publish_date == datetime.date(2013, 10, 21)
        assert attributes[0].choices['2'].name == u'2'
        assert attributes[0].choices['2'].title == u'Dont know'
        assert attributes[0].choices['2'].order == 2

    @pytest.mark.parametrize('group', ['administrator'])
    def test_iform_insert_import_table(self, app, db_session, group, datadir):
        from occams_imports import models
        from occams_studies import models as studies

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'study': u'DRSC'
        }

        iform = datadir.join('iform_input_fixture.json').open()
        json_data = iform.read()

        app.post(
            url,
            extra_environ=environ,
            expect_errors=True,
            upload_files=[('codebook', 'test.json', json_data)],
            headers={
                'X-CSRF-Token': csrf_token,
            },
            params=data)

        iform.close()

        import_data = db_session.query(models.Import).one()
        study = (
            db_session.query(studies.Study)
            .filter(studies.Study.title == data['study'])).one()

        assert study.title == data['study']
        assert import_data.schema.name == u'test_595_hiv_test_v04'

    def test_process_import(self, db_session):
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies
        from occams_imports.views.codebook import process_import

        attr_dict = {}

        schema = datastore.Schema(
            name=u'test_name',
            title=u'test_title',
            publish_date=date.today()
        )

        study = studies.Study(
            name=u'test_site',
            title=u'test_title',
            short_title=u'tt',
            code=u'tt1',
            consent_date=date.today(),
            is_randomized=False
        )

        process_import(schema, attr_dict, study, db_session)

        imported_study = (
            db_session.query(studies.Study)
            .filter(studies.Study.title == study.title)).one()

        assert imported_study.title == study.title

    def test_is_duplicate_schema(self, db_session):
        import transaction

        from occams_datastore import models as datastore
        from occams_imports.views.codebook import is_duplicate_schema

        forms = {}
        errors = []
        errors = is_duplicate_schema(forms, errors, db_session)

        assert errors == []

        forms = [{
            'name': u'test_schema_name',
            'title': u'test_schema_title',
            'publish_date': u'2015-01-01',
            'extra_key': u'test_title'
        }]

        schema = datastore.Schema(
            name=u'test_schema_name',
            title=u'test_schema_title',
            publish_date=u'2015-01-01'
        )

        with transaction.manager:
            db_session.add(schema)
            db_session.flush()

        errors = is_duplicate_schema(forms, errors, db_session)
        expected = u'Duplicate schema -  already exists in the db'
        exists = errors[0]['errors'] == expected

        assert exists is True


def test_validate_populate_imports(monkeypatch):
    import datetime

    from occams_imports.views.codebook import validate_populate_imports

    record = {
        'schema_name': u'test_schema_name',
        'schema_title': u'test_schema_title',
        'publish_date': datetime.date.today(),
        'name': u'test_name',
        'title': u'test_title',
        'description': u'',
        'is_required': False,
        'is_collection': False,
        'is_private': False,
        'type': u'number',
        'order': 0,
        'choices': []
    }

    mock_validate = mock.MagicMock()
    mock_validate.return_value = True
    mock_field_form = mock.MagicMock()
    mock_field_form.from_json.return_value = mock_validate

    mock_form_validate = mock.MagicMock()
    mock_form_validate.return_value = True
    mock_form_form = mock.MagicMock()
    mock_form_form.from_json.return_value = mock_form_validate

    monkeypatch.setattr(
        'occams_imports.views.codebook.FieldFormFactory',
        lambda **x: mock_field_form)

    monkeypatch.setattr(
        'occams_imports.views.codebook.FormFormFactory',
        lambda **x: mock_form_form)

    errors, imports, forms = validate_populate_imports(None, [record])

    assert errors == []
    assert len(imports) == 1
    assert len(forms) == 1
    assert forms[0]['name'] == u'test_schema_name'
    assert forms[0]['title'] == u'test_schema_title'
    assert imports[0][0].name == u'test_name'
    assert imports[0][1].name == u'test_schema_name'


def test_validate_populate_imports_schema_with_errors(monkeypatch):
    import datetime

    from occams_imports.views.codebook import validate_populate_imports

    record = {
        'schema_name': u'test_schema_name',
        'schema_title': u'test_schema_title',
        'publish_date': datetime.date.today(),
        'name': u'test_name',
        'title': u'test_title',
        'description': u'',
        'is_required': False,
        'is_collection': False,
        'is_private': False,
        'type': u'number',
        'order': 0,
        'choices': []
    }

    mock_validate = mock.MagicMock()
    mock_validate.return_value = True
    mock_field_form = mock.MagicMock()
    mock_field_form.from_json.return_value = mock_validate

    mock_form_validate = mock.MagicMock()
    mock_form_validate.validate.return_value = False
    mock_form_form = mock.MagicMock()
    mock_form_form.from_json.return_value = mock_form_validate

    monkeypatch.setattr(
        'occams_imports.views.codebook.FieldFormFactory',
        lambda **x: mock_field_form)

    monkeypatch.setattr(
        'occams_imports.views.codebook.FormFormFactory',
        lambda **x: mock_form_form)

    errors, imports, forms = validate_populate_imports(None, [record])

    assert errors != []
    assert len(errors) == 1
    assert errors[0]['schema_title'] == u'test_schema_title'


def test_log_errors():
    from occams_imports.views.codebook import log_errors
    errors = {
        'error': 'something is broken'
    }

    record = {
        'schema_name': u'test_schema_name',
        'schema_title': u'test_schema_title',
        'publish_date': u'2017-01-01',
        'name': u'test_name',
        'title': u'test_title'
    }

    output = log_errors(errors, record)

    assert output['errors'] == errors
    assert output['name'] == record['name']


def test_group_imports_by_schema():
    import datetime

    from occams_datastore import models as datastore
    from occams_imports.views.codebook import group_imports_by_schema

    with mock.patch('occams_imports.views.codebook.process_import') \
        as mock_process_import:

        db_session = None
        site = u'UCSD'
        attribute = datastore.Attribute(
            name=u'test_attr_name',
            title=u'test_title'
        )
        attribute2 = datastore.Attribute(
            name=u'test_attr_name2',
            title=u'test_title2'
        )

        schema = datastore.Schema(
            name=u'test_schema_name',
            title=u'test_schema_title',
            publish_date=datetime.date.today())

        schema2 = datastore.Schema(
            name=u'test_schema_name2',
            title=u'test_schema_title2',
            publish_date=datetime.date.today())

        imports = [(attribute, schema), (attribute2, schema2)]

        response = group_imports_by_schema(imports, site, db_session)

        mock_process_import.assert_any_call(
            imports[0][1], {u'test_attr_name': imports[0][0]}, u'UCSD', None)

        mock_process_import.assert_any_call(
            imports[1][1], {u'test_attr_name2': imports[1][0]}, u'UCSD', None)

        assert mock_process_import.call_count == 2
        assert response == 2


def test_get_unique_forms():
    from occams_imports.views.codebook import get_unique_forms

    forms = [{
        'name': u'test_schema_name',
        'title': u'test_schema_title',
        'publish_date': u'2015-01-01',
        'extra_key': u'test_title'
    },
        {
        'name': u'test_schema_name',
        'title': u'test_schema_title',
        'publish_date': u'2015-01-01',
        'extra_key': u'test_title'
    }]

    output = get_unique_forms(forms)

    assert len(output) == 1
    assert output == [(u'test_schema_name',
                       u'test_schema_title',
                       u'2015-01-01')]


def test_convert_delimiter():
    from occams_imports.views.codebook import convert_delimiter

    delimiter = u'comma'
    actual = convert_delimiter(delimiter)
    expected = u','

    delimiter = u'tab'
    actual = convert_delimiter(delimiter)
    expected = u'\t'

    assert actual == expected


def test_validate_delimiter(datadir):
    from occams_imports.views.codebook import validate_delimiter

    delimiter = ','
    codebook = datadir.join('codebook.csv').open()

    delimiter_mismatch, errors = validate_delimiter(delimiter, codebook)

    assert delimiter_mismatch is False
    assert errors == []

    codebook.seek(0)

    delimiter = '\t'
    delimiter_mismatch, errors = validate_delimiter(delimiter, codebook)
    expected_error = u"Selected delimiter doesn't match file delimiter"

    assert delimiter_mismatch is True
    assert errors[0]['errors'] == expected_error

    codebook.close()
