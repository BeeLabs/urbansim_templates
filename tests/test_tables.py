import os

import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.io import Table
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca session and initialize ModelManager.
    
    """
    orca.clear_all()
    modelmanager.initialize()


@pytest.fixture
def data(request):
    """
    Create data files on disk.
    
    """
    d1 = {'building_id': np.arange(10),
          'price': 1e6*np.random.random(10)}
    
    bldg = pd.DataFrame(d1).set_index('building_id')
    bldg.to_csv('data/buildings.csv')
    
    def teardown():
        os.remove('data/buildings.csv')
    
    request.addfinalizer(teardown)


def test_template_validity():
    """
    Run the template through the standard validation check.
    
    """
    assert validate_template(Table)


def test_property_persistence(orca_session):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    pass


######################################
### TESTS OF THE VALIDATE() METHOD ###
######################################

def test_validation_index_unique(orca_session):
    """
    Table validation should pass if the index is unique.
    
    These tests of the validate() method generate Orca tables directly, which is just a 
    shortcut for testing -- the intended use is for the method to validate the table
    loaded by the TableStep. 
    
    """
    d = {'id': [1,2,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index('id'))
    
    t = Table(name='tab')
    t.validate()
    

def test_validation_index_not_unique(orca_session):
    """
    Table validation should raise a ValueError if the index is not unique.
    
    """
    d = {'id': [1,1,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index('id'))
    
    t = Table(name='tab')
    try:
        t.validate()
    except ValueError:
        return
    
    pytest.fail()  # fail if ValueError wasn't raised


def test_validation_multiindex_unique(orca_session):
    """
    Table validation should pass with a MultiIndex whose combinations are unique.
    
    """
    d = {'id': [1,1,1], 'sub_id': [1,2,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index(['id', 'sub_id']))
    
    t = Table(name='tab')
    t.validate()


def test_validation_multiindex_not_unique(orca_session):
    """
    Table validation should raise a ValueError if the MultiIndex combinations are not 
    unique.
    
    """
    d = {'id': [1,1,1], 'sub_id': [2,2,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index(['id', 'sub_id']))
    
    t = Table(name='tab')
    try:
        t.validate()
    except ValueError:
        return
    
    pytest.fail()  # fail if ValueError wasn't raised


def test_validation_unnamed_index(orca_session):
    """
    Table validation should raise a ValueError if index is unnamed.
    
    """
    d = {'id': [1,1,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d))  # generates auto index without a name
    
    t = Table(name='tab')
    try:
        t.validate()
    except ValueError:
        return
    
    pytest.fail()  # fail if ValueError wasn't raised
    

def test_validation_columns_vs_other_indexes(orca_session):
    """
    Table validation should compare the 'households.building_id' column to 
    'buildings.build_id'.
    
    """
    d = {'household_id': [1,2,3], 'building_id': [2,3,4]}
    orca.add_table('households', pd.DataFrame(d).set_index('household_id'))

    d = {'building_id': [1,2,3,4], 'value': [4,4,4,4]}
    orca.add_table('buildings', pd.DataFrame(d).set_index('building_id'))

    t = Table(name='households')
    t.validate()


def test_validation_index_vs_other_columns(orca_session):
    """
    Table validation should compare the 'households.building_id' column to 
    'buildings.build_id'.
    
    """
    d = {'building_id': [1,2,3,4], 'value': [4,4,4,4]}
    orca.add_table('buildings', pd.DataFrame(d).set_index('building_id'))

    d = {'household_id': [1,2,3], 'building_id': [2,3,5]}
    orca.add_table('households', pd.DataFrame(d).set_index('household_id'))

    t = Table(name='buildings')
    t.validate()


def test_validation_with_multiindexes(orca_session):
    """
    Here, table validation should compare 'choice_table.[home_tract,work_tract]' to
    'distances.[home_tract,work_tract]'.
    
    """
    d = {'obs_id': [1,1,1,1], 'alt_id': [1,2,3,4], 
         'home_tract': [55,55,55,55], 'work_tract': [17,46,19,55]}
    orca.add_table('choice_table', pd.DataFrame(d).set_index(['obs_id','alt_id']))

    d = {'home_tract': [55,55,55], 'work_tract': [17,18,19], 'dist': [1,1,1]}
    orca.add_table('distances', pd.DataFrame(d).set_index(['home_tract','work_tract']))

    t = Table(name='choice_table')
    t.validate()


# test that parameters make it through a save
# test validation with stand-alone columns

# test loading an h5 file works
# test passing cache settings

# call it TableStep?


#################################
### TESTS OF THE DATA LOADING ###
#################################

def test_csv(orca_session, data):
    """
    Test that loading data from a CSV works.
    
    """
    t = Table()
    t.name = 'buildings'
    t.source_type = 'csv'
    t.path = 'data/buildings.csv'
    t.csv_index_cols = 'building_id'
    
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.register(t)
    assert 'buildings' in orca.list_tables()
    
    modelmanager.initialize()
    assert 'buildings' in orca.list_tables()
    
    modelmanager.remove_step('buildings')


def test_without_autorun(orca_session, data):
    """
    Confirm that disabling autorun works.
    
    """
    t = Table()
    t.name = 'buildings'
    t.source_type = 'csv'
    t.path = 'data/buildings.csv'
    t.csv_index_cols = 'building_id'
    t.autorun = False
    
    modelmanager.register(t)
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.remove_step('buildings')
    
    
    