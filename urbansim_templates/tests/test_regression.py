import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models import OLSRegressionStep


@pytest.fixture
def orca_session():
    d1 = {'a': np.random.random(100),
          'b': np.random.random(100)}

    obs = pd.DataFrame(d1)
    orca.add_table('obs', obs)


def test_ols(orca_session):
    """
    For now this just tests that the code runs.
    
    """
    modelmanager.initialize()

    m = OLSRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'a ~ b'
    
    m.fit()
    
    m.name = 'ols-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('ols-test')
    
    modelmanager.remove_step('ols-test')
    
if __name__ == '__main__':
	session = orca_session()
	test_ols(session)
