# flake8: noqa

def test_groups():
    from occams_imports import models
    assert models.groups.administrator() == u'administrator'
    assert models.groups.manager() == u'manager'
    assert models.groups.worker() == u'worker'
    assert models.groups.member() == u'member'