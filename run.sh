#!/bin/bash

.venv/bin/uwsgi --http :8893 --wsgi-file xsvds.py --callable app
