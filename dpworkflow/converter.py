import json
import ast
from ast2json import ast2json

data = open('../venv/test_df.py', 'r').read()

script = ast2json(ast.parse(data))

for line in script['body']:
    print(line)

def get_slice(dict_ver):
    """Tries to get the column of context dataframe

    Args:
        dict_ver (dict): Dictionary to be analyzed

    Returns (str): The column value

    """
    if 'slice' in dict_ver:
        return dict_ver['slice']['value']['s']


def get_name_num(edge_dict, pd_module_name):
    """

    Args:
        edge_dict: A dictionary that is either a name or value
        pd_module_name: Name of Pandas module on code

    Returns (tuple): The assigned df name and its respective column
    """
    output = {'kind': {'Name': {'id': None, 's': None}, 'Num': None}, 'lineno': None, 'main': None}
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
            if (edge_dict['func']['value']['id']) == pd_module_name and \
                    (edge_dict['func']['attr'] in ['read_csv']):
                output['main'] = True

    return output


# This recursion function needs a global var list to hold values

def assignment_digger(value_dict, global_op_list, global_stats_list, pd_module_name):
    """Gets the operations and assignment variables of a script assignment

    Args:
        value_dict: Dictionary with the assignment values
        global_op_list: A list with the operations of the assignment variables
        global_stats_list: A list with dictionaries about the assignment variables
    """
    if 'left' in value_dict and 'right' in value_dict:
        assignment_digger(value_dict['left'], global_op_list, global_stats_list, pd_module_name)
        assignment_digger(value_dict['right'], global_op_list, global_stats_list, pd_module_name)
        global_op_list.append(value_dict['op']['_type'])
    elif 'left' in value_dict:
        assignment_digger(value_dict['left'], global_op_list, global_stats_list, pd_module_name)
    else:
        global_stats_list.append(get_name_num(value_dict, pd_module_name))


def assignment_analyzer(line, pd_module_name):
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
            raise RuntimeError('This package only supports simple assignments')
        target = get_name_num(line['targets'][0], 'pd')
        assignment_digger(line['value'], global_op_list, global_stats_list, pd_module_name)
    return target, global_op_list, global_stats_list


def assignment_graph(script_body):
    # Here we can deal with any kind of assignment
    pd_module_name = 'pd'

    assignment_history = []
    for script_line in script_body:
        if script_line['_type'] == 'Assign':
            assignment_history.append(assignment_analyzer(script_line, pd_module_name))

    # Create a very simple graph to separate target assignments
    dict_graph = {}
    for asgn in assignment_history:
        idt = asgn[0]['kind']['Name']['id']
        if idt not in dict_graph:
            dict_graph[idt] = [asgn]
        else:
            dict_graph[idt].append(asgn)

    return dict_graph


def get_slices(list_calls, df_name):
    initial_df_seeds = []
    for parent_call in list_calls:
        calls = parent_call[2]
        calls.append(parent_call[0])
        for call in calls:
            if (df_name == call['kind']['Name']['id']) and (call['kind']['Name']['s']):
                df_slice = [call['kind']['Name']['id'], call['kind']['Name']['s']]
                if df_slice not in initial_df_seeds:
                    initial_df_seeds.append(df_slice)
    return initial_df_seeds

def get_slice_assignments(slice_desc, list_calls):
    slice_assignments = []
    for parent_call in list_calls:
        if (parent_call[0]['kind']['Name']['id'] == slice_desc[0]) and \
                (parent_call[0]['kind']['Name']['s'] == slice_desc[1]):
            slice_assignments.append(parent_call[2])

    return slice_assignments

print(json.dumps(assignment_graph(script['body'])))


for key, value in assignment_graph(script['body']).items():
    # Now we have to find what is a df
    initial_df_seeds = []
    if value[0][2][0]['main']:
        # See the slices
        df_name = key
        initial_df_seeds = get_slices(value, df_name)

    # Now, separate assignments by each slice
    dict_slice_assignments = {}
    if initial_df_seeds:
        for df_slice in initial_df_seeds:
            dict_slice_assignments[str(df_slice[0])+str(df_slice[1])] = get_slice_assignments(
                df_slice, value)
    print(dict_slice_assignments)




import os
from graphviz import Digraph

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'


dot = Digraph(comment='Test')

with dot.subgraph() as s:
    s.attr(rank='same')

    s.node('df0', 'df')
    s.node('df1', 'df')
    s.node('df2', 'df')

with dot.subgraph() as s:
    s.attr(rank='same')

    s.node('dfa', 'df[a]')
    s.node('dfb', 'df[b]')
    s.node('dfc', 'df[c]')

with dot.subgraph() as s:
    s.attr(rank='same')

    s.node('dfa1', 'df[a]+1')
    s.node('dfb1', 'df[b]+1')
    s.node('dfc1', 'df[a]+df[b]')

with dot.subgraph() as s:
    s.attr(rank='same')

    s.node('dfaf', 'df[a]')
    s.node('dfbf', 'df[b]')
    s.node('dfcf', 'df[c]')


dot.edge('df0', 'dfa')
dot.edge('dfa', 'dfa1')
dot.edge('dfa1', 'dfaf')

dot.edge('df1', 'dfb')
dot.edge('dfb', 'dfb1')
dot.edge('dfb1', 'dfbf')

dot.edge('df2', 'dfc')
dot.edge('dfc', 'dfc1')
dot.edge('dfa', 'dfc1')
dot.edge('dfb1', 'dfc1')
dot.edge('dfc1', 'dfcf')


#dot.view()

