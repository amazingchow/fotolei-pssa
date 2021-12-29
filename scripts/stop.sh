#!/bin/bash

lsof -i:8888 | grep node | awk '{print $2}' | xargs kill
lsof -i:15555 | grep flask | awk '{print $2}' | xargs kill
