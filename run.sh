#!/bin/bash

.venv/bin/uwsgi --http :8893 --wsgi-file vds/xsvds.py --callable app
