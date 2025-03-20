#!/bin/sh
taskiq scheduler app.tasks:scheduler &
taskiq worker app.tasks:broker
