#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import PyInstaller.__main__
import datetime
import json
import platform

version = "0.0"

target_platform = platform.system()
if target_platform == "Darwin":
    target_platform = "Mac"

if os.path.exists("version.json"):
    with open("version.json") as version_text:
        version_json = json.load(version_text)
        version = version_json['version']

date = datetime.datetime.now().strftime("%m%d%Y")
filename = os.path.join("release",f"difm_{target_platform}_{version}_{date}")

PyInstaller.__main__.run(['main.spec','--onefile','--clean'])
shutil.make_archive(filename, 'zip', "dist")