#!/bin/sh
# Decompile raw/<version>/RealmGrinderDesktop.swf into <dest> (deobfuscated scripts, binary data, images).
#   sh tools/extract.sh 4.3.15                  -> out/            (the version the tools and pages are built from)
#   sh tools/extract.sh 4.3.14 out_4.3.14       -> out_4.3.14/     (an older build kept for comparison)
# Copy the SWF from the game folder into raw/<version>/ first.
VER="${1:?usage: sh tools/extract.sh <version> [dest]}"
DEST="${2:-out}"
cd "$(dirname "$0")/.."
SWF="raw/$VER/RealmGrinderDesktop.swf"
[ -f "$SWF" ] || { echo "missing $SWF"; exit 1; }
F=tools/ffdec/ffdec-cli.exe
"$F" -config autoDeobfuscate=1 -export script "$DEST/script" "$SWF"
"$F" -export binaryData "$DEST/binaryData" "$SWF"
"$F" -export image "$DEST/image" "$SWF"
echo "$VER" > "$DEST/VERSION"
echo DONE
