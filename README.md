# OpenROAD Flow Runner
OpenROAD flow runner is a Docker-based flow runner that orchestrates the RTL-to-GDS flow. It is used in our cloud-based infrastructure. For more information about the software architecture of the flow, refer to the [documentation](https://docs.theopenroadproject.org)

### How to deploy
1. Create a virtual environment `python3 -m venv env`
2. Activate virtual environment `source env/bin/activate`
3. Install dependencies `pip install -r requirements.txt`
4. Copy `src/.env-example` to `src/.env` and modify deployment credentials accordingly.
5. Build using `docker-compose build`
6. Run using `docker-compose up`. Use the `-d` option to run as daemon.

## Help
In the issues tab, create a new issue with your question. If you need to send attachments with private IPs, contact us through [https://docs.theopenroadproject.org/#questions-support](https://docs.theopenroadproject.org/#questions-support)

## License
BSD 2-Clause License

Copyright (c) 2019, The OpenROAD Project
All rights reserved.