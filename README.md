# OpenROAD Flow Runner
OpenROAD flow runner is a Docker-based flow runner that orchestrates the RTL-to-GDS flow. It can be run locally on a machine with Docker installed. The same flow runner is used in our cloud-based infrastructure. 

## Run Locally
### Prerequisites
1. Install [Docker](https://docs.docker.com/install/)
2. Install `python` >= 3.x along with `pip`, the package manager for python

### How to run
1. Create a virtual environment `python3 -m venv env`
2. Activate virtual environment `source env/bin/activate`
3. Install dependencies `pip install -r requirements`
4. Modify `openroad-flow.yml` file with your input
5. Run `python cli.py openroad-flow.yml`

### Where to find the output
The output of the flow will be placed in the folder named `output_folder` from the `openroad-flow.yml` file. It is organized in the same sequence the flow is run.

## Run from OpenROAD web app
Documentation on running the flow from the web app is available at [OpenROAD Cloud Flow](https://github.com/The-OpenROAD-Project/BROWN-flow.theopenroadproject.org)

## Help
Contact abdelrahman+openroad@brown.edu for questions.

## License
© 2018-2019 The OpenROAD Project & contributors.