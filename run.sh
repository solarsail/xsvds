#!/bin/bash

uwsgi --http :9000 --wsgi-file vds/xsvds.py --callable app