#!/bin/sh
# Decompile raw/RealmGrinderDesktop.swf into out/ (deobfuscated scripts, binary data, images)
# Copy the SWF from the game folder into raw/ first.
cd "$(dirname "$0")/.."
F=tools/ffdec/ffdec-cli.exe
"$F" -config autoDeobfuscate=1 -export script out/script raw/RealmGrinderDesktop.swf
"$F" -export binaryData out/binaryData raw/RealmGrinderDesktop.swf
"$F" -export image out/image raw/RealmGrinderDesktop.swf
echo DONE
