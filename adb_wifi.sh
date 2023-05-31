#!/bin/sh

ANDROID_HOME="$HOME/Library/Android/sdk"

$ANDROID_HOME/platform-tools/adb kill-server
$ANDROID_HOME/platform-tools/adb start-server
$ANDROID_HOME/platform-tools/adb tcpip 5555
$ANDROID_HOME/platform-tools/adb connect 192.168.2.2:5555
