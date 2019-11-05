from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from dpworkflow.graph_generator import graph



class TestGraph(TestCase):

    @patch('dpworkflow.graph_generator.graph.create_nodes')
    @patch('dpworkflow.graph_generator.script_parse')
    def test_graph_setup(self, mock_script_parse, mock_create_nodes):
        test_script = 'test_script'

        mock_script_parse().pandas_df_slice_assignments = {'df': {'df[a]': [[['Add', 'Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]]], 'df[b]': [[[], [{'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]]], 'df[c]': [[['Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}]]]}}

        test_object = graph(test_script)

        mock_script_parse.assert_called_with(test_script)
        mock_create_nodes.assert_called_with('df', {'df[a]': [[['Add', 'Add'], [{'kind': {'Name':{'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]]], 'df[b]': [[[], [{'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]]], 'df[c]': [[['Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}]]]})

    @patch('dpworkflow.graph_generator.Digraph')
    @patch('dpworkflow.graph_generator.graph.link_transversal_assignments')
    @patch('dpworkflow.graph_generator.script_parse')
    def test_form_subgraphs(self, mock_script_parse, mock_link_transversal_assignments, mock_graph):
        test_script = 'test_script'
        mock_script_parse().pandas_df_slice_assignments = {'df': {'df[a]': [[['Add', 'Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 3, 'main': None}, {'kind': {'Name': {'id': None, 's': None}, 'Num': 1}, 'lineno': 3, 'main': None}]]], 'df[b]': [[[], [{'kind': {'Name': {'id': None, 's': None}, 'Num': 10}, 'lineno': 4, 'main': None}]]], 'df[c]': [[['Add'], [{'kind': {'Name': {'id': 'df', 's': 'a'}, 'Num': None}, 'lineno': 6, 'main': None}, {'kind': {'Name': {'id': 'df', 's': 'b'}, 'Num': None}, 'lineno': 6, 'main': None}]]]}}
        test_dict_assignments = {'df[a]': {'value': ['df', 'df[a]', 'df[a]+df[b]+1', 'df[a]'], 'line': [None, None, 3, None]}, 'df[b]': {'value': ['df', 'df[b]', '10', 'df[b]'], 'line': [None, None, 4, None]}, 'df[c]': {'value': ['df', 'df[c]', 'df[a]+df[b]', 'df[c]'], 'line': [None, None, 6, None]}}
        call_list = [call(mock_graph(), {3: ['df[a]', 'df[a]2', 'df[a]+df[b]+1'], 4: ['df[b]', 'df[b]2', '10'], 6: ['df[c]', 'df[c]2', 'df[a]+df[b]']}),
                     call(mock_graph(), {3: ['df[a]', 'df[a]2', 'df[a]+df[b]+1'], 4: ['df[b]', 'df[b]2', '10'], 6: ['df[c]', 'df[c]2', 'df[a]+df[b]']})]

        test_object = graph(test_script)

        test_object.form_subgraphs(mock_graph(), test_dict_assignments)
        mock_graph().subgraph.assert_called_with()
        self.assertEqual(mock_link_transversal_assignments.mock_calls, call_list)


