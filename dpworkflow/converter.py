import json
import ast
import os

from graphviz import Digraph
from ast2json import ast2json

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'

data = open('../venv/test_df.py', 'r').read()

script = ast2json(ast.parse(data))


# for line in script['body']:
#      print(line)

class script_parse():
    """Parses a script function returning several information related to a dataframe

    Args:
        script (object): The script with a dataframe to be evaluated

    """

    def __init__(self, script):
        self.script_body = script['body']
        self.pandas_import_name = self._get_import_name()
        self.pandas_dataframes = self._get_dataframes()
        self.pandas_df_assignments = self._get_df_assignments()
        self.pandas_dataframe_slices = self._get_slices()
        self.pandas_df_slice_assignments = self._get_df_slice_assignments()

    def _get_df_assignments(self):
        """Gets the assignments of a specific dataframe

        Returns:
            (dict) : A dictionary with assignments, where each key is a dataframe
        """
        df_assignments = {}

        assignments = self.assignment_graph()

        for dataframe in self.pandas_dataframes:
            df_assignments[dataframe] = assignments[dataframe]

        return df_assignments

    def assignment_graph(self):
        """For a given dataframe assignment create a graph for each target and assignment and
        operation, like [Target, Operations, Assignment]

        Returns:
            (dict) : A dictionary divided with DataFrame : [Target, Operations and Assignment]
        """
        # Here we can deal with any kind of assignment
        assignment_history = []
        for script_line in self.script_body:
            if script_line['_type'] == 'Assign':
                assignment_history.append(self._assignment_analyzer(script_line))

        # Create a very simple graph to separate target assignments
        dict_graph = {}
        for asgn in assignment_history:
            idt = asgn[0]['kind']['Name']['id']
            if idt not in dict_graph:
                dict_graph[idt] = [asgn]
            else:
                dict_graph[idt].append(asgn)

        return dict_graph

    def _get_import_name(self):
        """Gets the pandas import name (like pandas or pd)

        Returns:
            (str) : The import name or alias for pandas

        Raises:
            RuntimeError : Raised when the pandas module is not found


        """
        pandas_import_name = None
        for script_line in self.script_body:
            if script_line['_type'] == 'Import':
                if script_line['names'][0]['asname'] and \
                        script_line['names'][0]['name'] == 'pandas':
                    pandas_import_name = script_line['names'][0]['asname']
                elif script_line['names'][0]['name'] == 'pandas':
                    pandas_import_name = 'pandas'

        if pandas_import_name:
            return pandas_import_name

        raise RuntimeError('No pandas module import found')

    def _get_dataframes(self):
        """Get the name of dataframe assignments

        Returns:
            (list) : List containing the name of pandas dataframe assignments

        """
        pandas_dataframes = []
        load_df_attrs = ['read_csv', 'DataFrame']
        for script_line in self.script_body:
            if script_line['_type'] == 'Assign':
                if script_line['value']['_type'] == 'Call':
                    if script_line['value']['func']['value']['id'] == self.pandas_import_name and \
                            script_line['value']['func']['attr'] in load_df_attrs:
                        pandas_dataframes.append(script_line['targets'][0]['id'])
        return pandas_dataframes

    def _assignment_analyzer(self, line):
        """Analyze a line, if assignment type, and get the target and operations,assignments

        Args:
            line (dict): The script line

        Returns:
            (dict, list, list): A dictionary with the target variables, a list with the assignment
            operations and a list with dictionaries with the assign variables
        """
        global global_op_list
        global global_stats_list
        global_op_list = []
        global_stats_list = []
        target = None
        if line['_type'] == 'Assign':
            if 'elts' in line['targets'][0]:
                raise NotImplementedError('This package only supports simple assignments')
            target = self._get_name_num(line['targets'][0])
            self._assignment_digger(line['value'], global_op_list, global_stats_list)
        return target, global_op_list, global_stats_list

    def _get_name_num(self, edge_dict):
        """

        Args:
            edge_dict: A dictionary that is either a name or value

        Returns:
             (tuple): The assigned df name and its respective column
        """
        output = {'kind': {'Name': {'id': None, 's': None}, 'Num': None}, 'lineno': None,
                  'main': None}
        if edge_dict['_type'] == 'Name':
            output['kind']['Name']['id'] = edge_dict['id']
            output['lineno'] = edge_dict['lineno']
        if edge_dict['_type'] == 'Subscript':
            output['kind']['Name']['id'] = edge_dict['value']['id']
            output['lineno'] = edge_dict['lineno']
            if 's' in edge_dict['slice']['value']:
                output['kind']['Name']['s'] = edge_dict['slice']['value']['s']
            if 'n' in edge_dict['slice']['value']:
                output['kind']['Name']['s'] = edge_dict['slice']['value']['n']
        if edge_dict['_type'] == 'Num':
            output['kind']['Num'] = edge_dict['n']
            output['lineno'] = edge_dict['lineno']
        if edge_dict['_type'] == 'Call':
            if 'value' in edge_dict['func']:
                if (edge_dict['func']['value']['id']) == self.pandas_import_name and \
                        (edge_dict['func']['attr'] in ['read_csv']):
                    # This is needed to find who is the line that defines the DataFrame
                    output['main'] = True

        return output

    # This recursion function needs a global var list to hold values

    def _assignment_digger(self, value_dict, global_op_list, global_stats_list):
        """Gets the operations and assignment variables of a script assignment

        Args:
            value_dict: Dictionary with the assignment values
            global_op_list: A list with the operations of the assignment variables
            global_stats_list: A list with dictionaries about the assignment variables
        """
        if 'left' in value_dict and 'right' in value_dict:
            self._assignment_digger(value_dict['left'], global_op_list, global_stats_list)
            self._assignment_digger(value_dict['right'], global_op_list, global_stats_list)
            global_op_list.append(value_dict['op']['_type'])
        elif 'left' in value_dict:
            self._assignment_digger(value_dict['left'], global_op_list, global_stats_list)
        else:
            global_stats_list.append(self._get_name_num(value_dict))

    def _get_slices(self):
        """Gets a list with the slices being used in a DataFrame assignment

        Returns:
            list : A list with the name of DataFrame slices used on the assignments
        """
        pandas_dataframe_slices = {}
        for df_name, list_calls in self.pandas_df_assignments.items():
            initial_df_seeds = []
            for parent_call in list_calls:
                calls = parent_call[2].copy()
                calls.append(parent_call[0])
                for call in calls:
                    if (df_name == call['kind']['Name']['id']) and (call['kind']['Name']['s']):
                        df_slice = [call['kind']['Name']['id'], call['kind']['Name']['s']]
                        if df_slice not in initial_df_seeds:
                            initial_df_seeds.append(df_slice)
            pandas_dataframe_slices[df_name] = initial_df_seeds

        return pandas_dataframe_slices

    def _slice_assignments(self, slice_desc, list_calls):
        """Returns a dictionary with assignments divided by slice

        Args:
            slice_desc (list): A list with unique DataFrame slices detected in the call
            list_calls (list): Calls made by a DataFrame

        Returns:
            dict : A dictionary with operations and assignments for a given DataFrame slice

        """
        slice_assignments = []
        for parent_call in list_calls:
            if (parent_call[0]['kind']['Name']['id'] == slice_desc[0]) and \
                    (parent_call[0]['kind']['Name']['s'] == slice_desc[1]):
                slice_assignments.append([parent_call[1], parent_call[2]])

        return slice_assignments

    def _get_df_slice_assignments(self):
        """Returns a dictionary with assignments divided by slice

        Returns:
            dict : A dictionary with operations and assignments for a given DataFrame slice

        """
        pandas_dataframe_slice_assignments = {}
        for df_name, df_slices in self.pandas_dataframe_slices.items():
            value = self.pandas_df_assignments[df_name]
            dict_slice_assignments = {}
            for df_slice in df_slices:
                dict_slice_assignments[f'{df_slice[0]}[{df_slice[1]}]'] = \
                    self._slice_assignments(df_slice, value)
            pandas_dataframe_slice_assignments[df_name] = dict_slice_assignments
        return pandas_dataframe_slice_assignments


def kind_to_node(kind_dict):
    """Converts a dictionary with variable info to a understandable string

    Args:
        kind_dict (dict): Dictionary with information about a varaible

    Returns:
        (str): Plain representation of what that dictionary variable mean

    Raises:
        RuntimeError: Raised when the kind is not recognized

    """
    if kind_dict['kind']['Name']['id'] and kind_dict['kind']['Name']['s']:
        return f'{kind_dict["kind"]["Name"]["id"]}[{kind_dict["kind"]["Name"]["s"]}]'
    if kind_dict['kind']['Num']:
        return str(kind_dict['kind']['Num'])
    raise RuntimeError('Kind not identified')


def replace_operations(text):
    """Replace fully writen operations to its respective symbol

    Args:
        text (str): Fully writen operation

    Returns:
        (str): Symbolic representation of the operation
    """
    dic_op = {'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/'}
    for i, j in dic_op.items():
        text = text.replace(i, j)
    return text


def create_nodes(df_name, dict_slice_assignment):
    """Create a dictionary with node information for each operation line

    Args:
        df_name (str): Name of DataFrame being evaluated
        dict_slice_assignment (dict): Dictionary with information of assignments of each slide

    Returns:
        (dict): Information about the operation for each slice
    """
    dict_node_expression = {}
    for df_slice, assignments in dict_slice_assignment.items():
        dict_node_expression[df_slice] = {}
        dict_node_expression[df_slice]['value'] = [df_name, df_slice]
        dict_node_expression[df_slice]['line'] = [None, None]
        for assignment in assignments:
            node_expression = ''
            for n in range(len(assignment[0])):
                node_expression += kind_to_node(assignment[1][n])
                node_expression += replace_operations(assignment[0][n])
            node_expression += kind_to_node(assignment[1][-1])
            dict_node_expression[df_slice]['value'].append(node_expression)
            dict_node_expression[df_slice]['line'].append(assignment[1][0]['lineno'])
        dict_node_expression[df_slice]['value'].append(df_slice)
        dict_node_expression[df_slice]['line'].append(None)
    return dict_node_expression


def max_value_dict_len(dict):
    """Get the maximum number of elements of an slice assignments dict

    Args:
        dict (dict): A dictionary with slice assignments

    Returns:
        (int): The maximum number of operations of all slice assignments
    """
    max_len = 0
    for key, value in dict.items():
        if len(value['value']) > max_len:
            max_len = len(value['value'])
    return max_len


def link_vertical_nodes(graph, dfslice, list_assignments, index_slice):
    """Link vertical nodes

    Args:
        graph: Graph object
        dfslice (str): DataFrame slice being assigned on operation
        list_assignments (list): List of assignments for that DataFame slice
        index_slice (int): Line number for that operation
    """
    try:
        list_assignments[index_slice + 1]
        graph.edge(f'{dfslice}{index_slice}', f'{dfslice}{index_slice + 1}')
    except IndexError:
        pass


def form_subgraphs(graph, dict_assignments):
    """Create subgraphs for each operation step

        This also manages the vertical and transversal edges for each node

    Args:
        graph: Graph object
        dict_assignments (dict): Dictionary with assignments for each DataFrame slice
    """
    list_dfslices = list(dict_assignments.keys())
    max_len = max_value_dict_len(dict_assignments)
    middle_assignments = {}
    for i in range(max_len):
        with graph.subgraph() as s:
            s.attr(rank='same')
            for dfslice in list_dfslices:
                try:
                    s.node(dfslice + str(i), dict_assignments[dfslice]['value'][i])
                    link_vertical_nodes(graph, dfslice, dict_assignments[dfslice]['value'], i)
                    if dict_assignments[dfslice]['line'][i]:
                        # DF[slice],  nodecode, expression, linenumber
                        middle_assignments[dict_assignments[dfslice]['line'][i]] = \
                            [dfslice, dfslice + str(i), dict_assignments[dfslice]['value'][i]]
                except IndexError:
                    pass
    link_transversal_assignments(graph, middle_assignments)


def link_transversal_assignments(graph, middle_assignments):
    """Adds transversal edges for the graph nodes

    Args:
        graph: Graph object
        middle_assignments (dict): Dictionaty containing assignment operations for a specific
        DataFrame slice
    """
    lines_idxs = list(middle_assignments.keys())
    lines_idxs.sort()
    for i in range(len(lines_idxs)):
        for y in range(i + 1, len(lines_idxs)):
            if middle_assignments[lines_idxs[i]][0] == middle_assignments[lines_idxs[y]][0]:
                break
            if middle_assignments[lines_idxs[i]][0] in middle_assignments[lines_idxs[y]][2]:
                graph.edge(middle_assignments[lines_idxs[i]][1],
                           middle_assignments[lines_idxs[y]][1])


def create_graph(script):
    """Creates a graph from a script body

    Args:
        script: Text of script
    """
    df_slice_assignments = script_parse(script).pandas_df_slice_assignments
    for df_name, assignments in df_slice_assignments.items():
        if assignments:
            dict_assignments = create_nodes(df_name, assignments)
            graph = Digraph(comment='Test')
            form_subgraphs(graph, dict_assignments)

            graph.view()


#create_graph(script)
