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

    def test__assignment_analyzer_single_assignment(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        script_test = ast2json(ast.parse(script_test))

        test_line = {'_type': 'Assign', 'col_offset': 0, 'lineno': 6, 'targets': [{'_type': 'Name', 'col_offset': 0, 'ctx': {'_type': 'Store'}, 'id': 'a', 'lineno': 6}], 'value': {'_type': 'BinOp', 'col_offset': 2, 'left': {'_type': 'Subscript', 'col_offset': 2, 'ctx': {'_type': 'Load'}, 'lineno': 6, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 5, 'lineno': 6, 's': 'b'}}, 'value': {'_type': 'Name', 'col_offset': 2, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 6}}, 'lineno': 6, 'op': {'_type': 'Add'}, 'right': {'_type': 'Num', 'col_offset': 10, 'lineno': 6, 'n': 10}}}

        test_object = script_parse(script_test)

        output = test_object._assignment_analyzer(test_line)

        self.assertEqual(output, ({'kind': {'Name': {'id': 'a', 's': None}, 'Num': None}, 'lineno': 6, 'main': None}, ['Add'], [{'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 6, 'main': None}]))


    def test__assignment_analyzer_error_multiple_assignments(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"],df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        script_test = ast2json(ast.parse(script_test))

        with self.assertRaises(NotImplementedError) as context:
            script_parse(script_test)

        self.assertTrue('This package only supports simple assignments' in str(context.exception))

    def test__get_name_num__return_subscript(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        script_test = ast2json(ast.parse(script_test))

        test_line = {'_type': 'Subscript', 'col_offset': 8, 'ctx': {'_type': 'Load'}, 'lineno': 6, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 11, 'lineno': 6, 's': 'a'}}, 'value': {'_type': 'Name', 'col_offset': 8, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 6}}

        test_object = script_parse(script_test)

        output = test_object._get_name_num(test_line)

        self.assertEqual(output, {'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None},
                                  'lineno': 6, 'main': None})

    def test__get_name_num__return_num(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        script_test = ast2json(ast.parse(script_test))

        test_line = {'_type': 'Num', 'col_offset': 10, 'lineno': 5, 'n': 10}

        test_object = script_parse(script_test)

        output = test_object._get_name_num(test_line)

        self.assertEqual(output, {'kind': {'Name': {'id': None, 's': None}, 'Num': 10},
                                  'lineno': 5, 'main': None})

    def test__get_name_num__return_call(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        script_test = ast2json(ast.parse(script_test))

        test_line = {'_type': 'Call', 'args': [{'_type': 'Str', 'col_offset': 15, 'lineno': 2, 's': 'test.csv'}], 'col_offset': 3, 'func': {'_type': 'Attribute', 'attr': 'read_csv', 'col_offset': 3, 'ctx': {'_type': 'Load'}, 'lineno': 2, 'value': {'_type': 'Name', 'col_offset': 3, 'ctx': {'_type': 'Load'}, 'id': 'pd', 'lineno': 2}}, 'keywords': [], 'lineno': 2}

        test_object = script_parse(script_test)

        output = test_object._get_name_num(test_line)

        self.assertEqual(output, {'kind': {'Name': {'id': None, 's': None}, 'Num': None},
                                  'lineno': None, 'main': True})
