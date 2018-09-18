import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models import BinaryLogitStep
from urbansim_templates.settings import pipe, register_modules

d1 = {'a': np.random.random(100),
      'b': np.random.randint(2, size=100)}

obs = pd.DataFrame(d1)
orca.add_table('obs', obs)


def test_binary_logit():
    """
    For now this just tests that the code runs.
    
    """
    register_modules(globals())
    modelmanager.initialize()

    m = BinaryLogitStep()
    m.tables = 'obs'
    m.model_expression = 'b ~ a'
    
    m.fit()
    
    m.name = 'binary-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('binary-test')
    
	
if __name__ == '__main__':
    test_binary_logit()
	