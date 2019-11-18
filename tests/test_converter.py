from unittest import TestCase
from unittest.mock import patch, call
from dpworkflow._converter import script_parse

import ast
from ast2json import ast2json


class TestScript_parse(TestCase):

    @patch('dpworkflow._converter.script_parse.assignment_graph')
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

        self.assertEqual(output, {'a': [({'Attr': None, 'kind': {'Name': {'id': 'a', 's': None}, 'Num': None}, 'lineno': 5, 'main': None}, ['Add'], [{'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 5, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 5, 'main': None}])], 'df': [({'Attr': None, 'kind': {'Name': {'id': 'df', 's': None}, 'Num': None}, 'lineno': 2, 'main': None}, [], [{'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': None}, 'lineno': None, 'main': True}]), ({'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, ['Add', 'Add'], [{'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]), ({'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 4, 'main': None}, [], [{'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]), ({'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'c'}, 'Num': None}, 'lineno': 6, 'main': None}, ['Add'], [{'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}])]})

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

        self.assertEqual(output, ({'Attr': None, 'kind': {'Name': {'id': 'a', 's': None}, 'Num': None}, 'lineno': 6, 'main': None}, ['Add'], [{'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 6, 'main': None}]))


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

        self.assertEqual(output, {'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'a'},
                                                         'Num': None}, 'lineno': 6, 'main': None})

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

        self.assertEqual(output, {'Attr': None, 'kind': {'Name': {'id': None, 's': None},
                                                         'Num': 10}, 'lineno': 5, 'main': None})

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

        self.assertEqual(output, {'Attr': None, 'kind': {'Name': {'id': None, 's': None},
                                                         'Num': None},
                                                         'lineno': None, 'main': True})

    @patch('dpworkflow._converter.script_parse._assignment_digger')
    def test__assignment_digger__calls_check(self, mock_assignment_digger):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        call_list = [call({'_type': 'Call', 'args': [{'_type': 'Str', 'col_offset': 15, 'lineno': 2, 's': 'test.csv'}], 'col_offset': 3, 'func': {'_type': 'Attribute', 'attr': 'read_csv', 'col_offset': 3, 'ctx': {'_type': 'Load'}, 'lineno': 2, 'value': {'_type': 'Name', 'col_offset': 3, 'ctx': {'_type': 'Load'}, 'id': 'pd', 'lineno': 2}}, 'keywords': [], 'lineno': 2}, [], []),
                     call({'_type': 'BinOp', 'col_offset': 23, 'left': {'_type': 'BinOp', 'col_offset': 8, 'left': {'_type': 'Subscript', 'col_offset': 8, 'ctx': {'_type': 'Load'}, 'lineno': 3, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 11, 'lineno': 3, 's': 'a'}}, 'value': {'_type': 'Name', 'col_offset': 8, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 3}}, 'lineno': 3, 'op': {'_type': 'Add'}, 'right': {'_type': 'Subscript', 'col_offset': 16, 'ctx': {'_type': 'Load'}, 'lineno': 3, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 19, 'lineno': 3, 's': 'b'}}, 'value': {'_type': 'Name', 'col_offset': 16, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 3}}}, 'lineno': 3, 'op': {'_type': 'Add'}, 'right': {'_type': 'Num', 'col_offset': 24, 'lineno': 3, 'n': 1}}, [], []),
                     call({'_type': 'Num', 'col_offset': 8, 'lineno': 4, 'n': 10}, [], []),
                     call({'_type': 'BinOp', 'col_offset': 2, 'left': {'_type': 'Subscript', 'col_offset': 2, 'ctx': {'_type': 'Load'}, 'lineno': 5, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 5, 'lineno': 5, 's': 'b'}}, 'value': {'_type': 'Name', 'col_offset': 2, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 5}}, 'lineno': 5, 'op': {'_type': 'Add'}, 'right': {'_type': 'Num', 'col_offset': 10, 'lineno': 5, 'n': 10}}, [], []),
                     call({'_type': 'BinOp', 'col_offset': 8, 'left': {'_type': 'Subscript', 'col_offset': 8, 'ctx': {'_type': 'Load'}, 'lineno': 6, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 11, 'lineno': 6, 's': 'a'}}, 'value': {'_type': 'Name', 'col_offset': 8, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 6}}, 'lineno': 6, 'op': {'_type': 'Add'}, 'right': {'_type': 'Subscript', 'col_offset': 16, 'ctx': {'_type': 'Load'}, 'lineno': 6, 'slice': {'_type': 'Index', 'value': {'_type': 'Str', 'col_offset': 19, 'lineno': 6, 's': 'b'}}, 'value': {'_type': 'Name', 'col_offset': 16, 'ctx': {'_type': 'Load'}, 'id': 'df', 'lineno': 6}}}, [], [])]

        script_test = ast2json(ast.parse(script_test))

        script_parse(script_test)

        self.assertEqual(mock_assignment_digger.mock_calls, call_list)

    def test__get_slices__return_slice(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'

        script_test = ast2json(ast.parse(script_test))

        test_object = script_parse(script_test)

        output = test_object._get_slices()

        self.assertEqual(output, {'df': [['df', 'a'], ['df', 'b'], ['df', 'c']]})

    def test__slice_assignments_get_slice_assigments(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        test_slice_desc = ['df', 'a']
        test_list_calls = [({'kind': {'Name': {'id': 'df', 's': None}, 'Num': None}, 'lineno': 2, 'main': None}, [], [{'kind': {'Name': {'id': None, 's': None}, 'Num': None}, 'lineno': None, 'main': True}]), ({'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, ['Add', 'Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]), ({'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 4, 'main': None}, [], [{'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]), ({'kind': {'Name': {'id': 'df', 's': 'c'}, 'Num': None}, 'lineno': 6, 'main': None}, ['Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}])]

        script_test = ast2json(ast.parse(script_test))

        test_object = script_parse(script_test)

        output = test_object._slice_assignments(test_slice_desc, test_list_calls)

        self.assertEqual(output, [[['Add', 'Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]]])

    def test__get_df_slice_assignments_get_assignments(self):
        script_test = 'import pandas as pd\n' \
                      'df=pd.read_csv("test.csv")\n' \
                      'df["a"]=df["a"]+df["b"]+1\n' \
                      'df["b"]=10\n' \
                      'a=df["b"]+10\n' \
                      'df["c"]=df["a"]+df["b"]'
        script_test = ast2json(ast.parse(script_test))

        output = script_parse(script_test)._get_df_slice_assignments()

        self.assertEqual(output, {'df': {'df[a]': [[['Add', 'Add'], [{'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]]], 'df[b]': [[[], [{'Attr': None, 'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]]], 'df[c]': [[['Add'], [{'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'Attr': None, 'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}]]]}})
