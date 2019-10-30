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

        output = script_parse(script_test)._get_df_assignments()

        mock_assignment_graph.assert_called_with()

        self.assertEqual(output, {'df': mock_assignment_graph().__getitem__()})

    def test__assignment_graph_simple_assignment(self):

        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        output = script_parse(script_test).assignment_graph()

        self.assertEqual(output, {'df': [({'kind': {'Name': {'id': 'df', 's': None}, 'Num': None}, 'lineno': 2, 'main': None}, [], [{'kind': {'Name': {'id': None, 's': None}, 'Num': None}, 'lineno': None, 'main': True}]), ({'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, ['Add', 'Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]), ({'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 4, 'main': None}, [], [{'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]), ({'kind': {'Name': {'id': 'df', 's': 'c'}, 'Num': None}, 'lineno': 6, 'main': None}, ['Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}])], 'a': [({'kind': {'Name': {'id': 'a', 's': None}, 'Num': None}, 'lineno': 5, 'main': None}, ['Add'], [{'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 5, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 5, 'main': None}])]})

    def test__get_import_name_pandas_fullname(self):
        script_test = 'import pandas\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        output = script_parse(script_test)._get_import_name()

        self.assertEqual(output, 'pandas')

    def test__get_import_name_pandas_alias(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        output = script_parse(script_test)._get_import_name()

        self.assertEqual(output, 'pd')

    def test__get_import_name_raise_no_module(self):
        script_test = 'import pindas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        with self.assertRaises(RuntimeError) as context:
            script_parse(script_test)

        self.assertTrue('No pandas module import found' in str(context.exception))

    def test__get_dataframes_return_single_name(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        output = script_parse(script_test)._get_dataframes()


        self.assertEqual(output, ['df'])

    def test__get_dataframes_return_multiple_names(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df2 = df=pd.read_csv("test2.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df2["x"] = 10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        output = script_parse(script_test)._get_dataframes()

        self.assertEqual(output, ['df', 'df2'])
