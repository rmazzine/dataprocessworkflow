
# Pandas Data Process Workflow

This script analyzes a Pandas script and its operations and converts it to a graph chart.

The script is currently in a very early version, but updates are made constantly. :smiley:

**YOU NEED TO INSTALL THE GRAPHVIZ SOFTWARE AND PYTHON PACKAGE BEFORE USING THIS SCRIPT.**

The main objective its to have a better picture of data processing using the Pandas package. This is specially useful when large datasets have multiple and complex operations that make difficult to have a clear understanding of data transformation. 

For now it supports assignment and arithmetic operations, but complex method operations will be added soon.

## 1 - Installation

After cloning the repository, install script requirements with pip
```bash
pip install -r requirements.txt
```
Then, you will need to install Graphviz Graph Visualization Software:
[https://graphviz.gitlab.io/download/](https://graphviz.gitlab.io/download/)

*Pay attention to the Graphviz installation folder, as you will need it to run the script

## 2 - Usage example

A simple example is shown below:

For the example, we will analyzes the script on `sample_test_script/sample_test_df.py`

```python
import pandas as pd  
  
df = pd.read_csv('sample_data.csv', delimiter=';')  
  
# Calculate the Age from the birth year  
df['Age'] = 2019-df['Birth_Year']  
print(df['Age'])  
  
df['Monthly_Salary'] = df['Salary']/12  
  
df['Monthly_Salary_by_Ed_Year'] = df['Monthly_Salary']/df['Years_Education']  
df['Monthly_Salary_by_Age'] = df['Monthly_Salary']/df['Age']
```

Now, with the `test_make_graph.py` script on sample_test_script folder we simply where we import the `graph_generator` class of `dpworkflow` module, includes the script to be analyzed and the bin path of Graphviz software (in Windows it is "C:/Program Files (x86)/Graphviz2.38/bin", in MacOS can be something like "/usr/local/Cellar/graphviz/2.42.2/bin"), then includes the additional method `create_graph()` to create the DataFrame graph chart.

```python
from dpworkflow import graph_generator

graph_generator.graph('sample_test_df.py', graphviz2_path='C:/Program Files (x86)/Graphviz2.38/bin').create_graph()
```
Then, just run the script:
```bash
python test_make_graph.py
```

In this example, the chart will be like the one below: 

![Example image of script output](img/example1.png?raw=true "Output Example")
