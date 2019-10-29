from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch
from dpworkflow.converter import script_parse

import ast
from ast2json import ast2json


class TestScript_parse(TestCase):

    @patch('dpworkflow.converter.script_parse.assignment_graph')
    def test__get_df_assignments_regular_call(self, mock_assignment_graph):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        script_parse(script_test)

        mock_assignment_graph.assert_called_with()


