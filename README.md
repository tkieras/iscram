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

The input for ISCRAM function is called a System Graph, which is a collection of nodes and edges representing the different features of the system being analyzed.

Whether run as a CLI application or as a server, all ISCRAM functions require the input to be valid JSON containing a valid System Graph.

### The Basic Structure of a System Graph

A System Graph is structured as follows:

```
{
	"name": name,
	"components": [],
	"suppliers": [],
	"security_dependencies": [],
	"offerings": [],
	"indicator": {
		"logic_function" : logic_function_option,
		"dependencies" : []
	}
}
```

The above fields are all required.

The name may be any string.

The logic_function_option must be either "and" or "or".

The above will be accepted as valid but without producing any results since the graph is empty.

#### Component

Each item in the component list has the following data:

```
{
	"identifier" : name,
	"logic_function" : logic_function_option,
	"risk" : risk,
	"cost" : cost
}
```

The name may be any string that begins with an alphabetic character (i.e., a-z or A-Z).

The logic_function_option must be either "and" or "or".

The risk must be a float between 0.0 and 1.0.

The cost may be any positive integer.


#### Supplier

Each supplier has the following data.

```
{
	"identifier": name,
	"trust": trust,
	"traits": []
}
```

The name may be any string that begins with an alphabetic character (i.e., a-z or A-Z).

The trust must be a float between 0.0 and 1.0.

Each item in the traits list must have the following data:

```
{ 
	key: name, 
	value: trait_value
}
```

The key may be any string. The trait_value must be either true or false.

#### Security Dependencies

Edges in the graph are involved in two places in the System Graph:

- security_dependencies
- indicator.dependencies

Each item in both lists must have the following data:

```
{
	"risk_src_id": src_name,
	"risk_dst_id": dst_name
}
```

The src_name and dst_name must be equal to the identifier values of components or suppliers that exist in the system. 


#### Offerings

Each item in the offering list must have the following data:

```
{
	"supplier_id": supplier_name,
	"component_id": component_name,
	"risk": risk,
	"cost": cost
}
```

The supplier name must match a supplier's identifier; likewise for the component name.

The risk must be a float between 0.0 and 1.0.

The cost may be any positive integer.

Offerings are used only for optimization related functions and have no effect on risk analysis unless they are first converted to security dependencies as an explicit step in an optimization process.
