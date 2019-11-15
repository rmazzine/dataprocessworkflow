import os
import ast

from ast2json import ast2json
from graphviz import Digraph
from dpworkflow._converter import script_parse

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'


class graph():

    def __init__(self, script_path):
        """Creates a graph from a script body

        Args:
            script_path: Path of script
        """

        data = open(script_path, 'r').read()

        script = ast2json(ast.parse(data))

        self.script_parse_obj = script_parse(script)

    def create_graph(self):
        df_slice_assignments = self.script_parse_obj.pandas_df_slice_assignments
        for df_name, assignments in df_slice_assignments.items():
            if assignments:
                dict_assignments = self._create_nodes(df_name, assignments)
                graph = Digraph()
                self._form_subgraphs(graph, dict_assignments)

                graph.view()

    def _form_subgraphs(self, graph, dict_assignments):
        """Create subgraphs for each operation step

            This also manages the vertical and transversal edges for each node

        Args:
            graph: Graph object
            dict_assignments (dict): Dictionary with assignments for each DataFrame slice
        """

        list_dfslices = list(dict_assignments.keys())
        max_len = self.max_value_dict_len(dict_assignments)
        middle_assignments = {}
        for i in range(max_len):
            with graph.subgraph() as s:
                s.attr(rank='same')
                for dfslice in list_dfslices:
                    try:
                        s.node(dfslice + str(i), dict_assignments[dfslice]['value'][i])
                        self.link_vertical_nodes(graph, dfslice,
                                                 dict_assignments[dfslice]['value'], i)
                        if dict_assignments[dfslice]['line'][i]:
                            # DF[slice],  nodecode, expression, linenumber
                            middle_assignments[dict_assignments[dfslice]['line'][i]] = \
                                [dfslice, dfslice + str(i), dict_assignments[dfslice]['value'][i]]
                    except IndexError:
                        pass
        self.link_transversal_assignments(graph, middle_assignments)

    def _create_nodes(self, df_name, dict_slice_assignment):
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
                    node_expression += self.kind_to_node(assignment[1][n])
                    node_expression += self.replace_operations(assignment[0][n])
                node_expression += self.kind_to_node(assignment[1][-1])
                dict_node_expression[df_slice]['value'].append(node_expression)
                dict_node_expression[df_slice]['line'].append(assignment[1][0]['lineno'])
            dict_node_expression[df_slice]['value'].append(df_slice)
            dict_node_expression[df_slice]['line'].append(None)
        return dict_node_expression

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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