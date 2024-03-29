# ISCRAM: Supply Chain Risk Analysis and Mitigation Tool

The ISCRAM tool performs risk modeling for supply chain security risks, given a specified system, risk and trust values for system entities. The tool includes also a decision support function that recommends optimal risk mitigating choices among available suppliers, subject to budget constraints. For documentation, please refer to the papers describing the modeling approach implemented here:

- T. Kieras, M.J. Farooq, Q. Zhu. RIoTS: Risk Analysis of IoT Supply Chain Threats. IEEE 6th World Forum on the Internet of Things, 2020. <https://arxiv.org/abs/1911.12862>
- T. Kieras, M.J. Farooq, Q. Zhu. Modeling and Assessment of IoT Supply Chain Security Risks: The Role of Structural and Parametric Uncertainties. IEEE Security & Privacy CReSCT Workshop, 2020. <https://arxiv.org/abs/2003.12363>
- T. Kieras, J. Farooq and Q. Zhu, "I-SCRAM: A Framework for IoT Supply Chain Risk Analysis and Mitigation Decisions," in IEEE Access, vol. 9, pp. 29827-29840, 2021. <https://ieeexplore.ieee.org/document/9350583>

This repository holds code implementing various analysis and optimization functions which can be accessed through a REST API or directly invoked as a CLI for local usage.

## Usage

### Setup

The project requires Python 3.8+.

`git clone https://github.com/tkieras/iscram`

`cd iscram`

#### Setup with Docker

`docker-compose --build iscram-dev`

#### Setup Without Docker

Install dependencies:

`pip install -r requirements/dev/requirements.txt`

* Note: In addition to the requirements listed explicitly, the package `dd` and its module `dd.cudd` must be manually installed.
* Refer to `dd` documentation for installation instructions: https://github.com/tulip-control/dd .
* To verify proper installation of `dd.cudd`, the following command should execute without error:

`python -c "import dd.cudd" `

(Recommended) Install ISCRAM Python package from source:

`pip install .`

Alternately, set the `PYTHONPATH` environment variable:

- `export PYTHONPATH=$(PYTHONPATH):$(pwd)`

### Run a local ISCRAM server with Docker

After building the container image, run it.

`docker-compose up iscram-dev`

Run a smoke test with curl to verify server health:

`curl localhost:8000/status`

- If successfully running, the server should return:
	- `{"health":"alive"}`

API documentation can be found by visiting:

- `localhost:8000/docs`

### Run a local ISCRAM server without Docker

After setup (above), do the following.

Run the server:

`python -m uvicorn iscram.entrypoints.api.main:app --port 8000 --host localhost`

Run a smoke test with curl to verify server health:

`curl localhost:8000/status`

- If successfully running, the server should return:
	- `{"health":"alive"}`

API documentation can be found by visiting:

- `localhost:8000/docs`

### Usage as stand-alone CLI application

For local usage of the ISCRAM functions, it is possible to run analysis without a server.

After setup (above, without docker), do the following.

`python -m iscram.entrypoints.cli.app -i <path/to/system-graph.json>`

A sample input file can be found at the top level directory of this repository. Additional information on the expected data structure is included below.

## System Graph Data Structure

API documentation can be found by visiting:

- `localhost:8000/docs`

The input for ISCRAM function is split into two data structures:
	- a System Graph, which is a collection of nodes and edges representing the different features of the system being analyzed.
	- an optional data object.

Whether run as a CLI application or as a server, all ISCRAM functions require the input to be valid JSON containing a valid System Graph, optional data and optional preferences, as follows:
``` 
{
	"system_graph": ...,
	"data": ...,
	"preferences": ...,
}
```

This schema can be found in the documentation as 'RequestBody.'

A full example can be found in `iscram/sample-file.json`.

### System Graph IDs, Mutability and Associated Data

A system graph is uniquely identified by an ID obtained from the ISCRAM server.

In general the system graph is treated as an immutable data structure. If, for example, optimization is requested and results in a graph with different nodes, edges or tags, then a new graph is returned with a new ID.

In addition to a system graph, a data object is needed to provide parameters for data such as risk or cost. This data object is also treated as immutable and may be a superset of data needed to analyze a particular graph. For example, data for suppliers that are available but not chosen may be present in data. After optimization, a new graph results that may use a different subset of the data. 

An example workflow would consist of:

	- specifying an initial system graph A
	- specifying a dataset Z including but not limited to data needed to analyze A
	- analyzing A against dataset Z
	- optimizing A -> A'
	- analyzing A' against dataset Z
	- optimizing A' -> A''
	- analyzing A'' against dataset Z

The portion of the dataset that is relevant is determined by the nodes/edges in the system graph.

### System Graph

A System Graph is structured as follows:

```
{
	"nodes": {},
	"edges": []
}
```

Both fields are required.

#### Node

The items in the node field are key, value pairs where the key is the name of the node, and the value is an object with the following properties.

```
{
	"tags" : []
	"logic" : {"node_type": "logic_type"},
}
```

The key may be any string that begins with an alphabetic character (i.e., a-z or A-Z).

The tags list contains any number of relevant tags. For ISCRAM each node must be tagged as exactly one of the following node types:
	
	- component
	- supplier
	- indicator

One node must be tagged as indicator, and its name must be indicator as well.

The tags specify the type of node and its role in the system.

The logic field contains key, value pairs where the key is a node type (one of the above required tags), and the value is one of:
	
	- and
	- or

As an example, the following object defines a component node where logical or defines its dependence on other components.
```
{
	"tags": ["component"],
	"logic": {"component": "or"}
}
```
Each component node must have a component logic function provided explicitly. Supplier nodes may omit this, and use "and" by default for other suppliers.

#### Edge

Each object in the edge list should have the following form:
```
{
	"src": nodeId,
	"dst": nodeId
	"tags: []
}
```

The src and dst fields must match keys in the node object.
The tags field is optional, but if it is present and if the tag "potential" is included, then the edge is treated as irrelevant for the purpose of risk analysis.

### Data

Data is provided in the form of a second object with the following basic structure, similar to a system graph:

``` 
{
	"nodes": {},
	"edges": [],
}
```

The nodes object contains key, value pairs where the key must match an existing node in the system graph, and the value contains a data object:

The fields in the data object are flexible but should include risk.
``` 
{
	"risk": 0 <= float <= 1,
	"attributes": {}
}
```

An additional field in the data object may be "attributes", which contains key, value pairs as follows.
``` 
{
	attribute_name: attribute_value
}
```

The attribute name may be any string, and the attribute_value should be true or false (boolean).

Edge data may be provided as well, where each item in the edge data list has the following form:

``` 
{
	"src": nodeId,
	"dst": dstId,
	"risk": 0 <= float <= 1,
	"cost": 0 <= integer
}
```

Note that there are two places where a component node risk value may be provided:

- data.nodes
- data.edges

If the edge data indicates an edge from a supplier to a component node, then the edge represents an "offering" where the supplier may be contracted to provide this particular component. If the supplier is chosen, the component risk becomes the risk specified on the edge.

Since risk analysis may be desirable in situations where the supplier is not known, risk data in data.nodes may be added even when suppliers are not present in the graph.

The risk values provided in data.edges always has priority, and all risk analysis and optimization will use available edge data before resorting to data provided directly on nodes.
If no risk value is provided in either location, then 0.0 is used.

For example, in a system with x1, x2, x3 as components and s1 as supplier of x1, suppose the following data is provided:
```
{ 
	nodes: {
		"x1": {"risk": 0.9},
		"x2": {"risk": 0.8},
		},
	edges: [
		{"src": "s1", "dst": "x1", "risk": 0.01, "cost": 30}
	]
}
```

The risk value for x1 will be 0.01 because s1 is the supplier of x1, and the edge from s1 to x1 holds a risk of 0.01.

The risk value for x2 will be 0.8 because no supplier or supplier edge exists for x2, and so we fall back to data specified directly on the node itself.

Lastly, x3 will have a risk of 0.0 because although it is declared as  a node in the system, no data is provided.


## API Documentation

Further details on the API and data structures can be found by viewing the OpenAPI documentation at:

- `localhost:8000/docs`
