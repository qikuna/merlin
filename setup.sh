#!/usr/bin/env bash

echo "Initializing bootstrap process..."

BIN_PATH="$HOME/.local/bin"
LAUNCHER_FILE="$BIN_PATH/merlin"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTRY_POINT="$SOURCE_DIR/merlin.py"

if [ ! -d "$BIN_PATH" ]; then
    mkdir -p "$BIN_PATH"
    echo "Created missing binary path directory: $BIN_PATH"
fi

cat <<EOF > "$LAUNCHER_FILE"
#!/usr/bin/env bash
python3 "$ENTRY_POINT" "\$@"
EOF

chmod +x "$LAUNCHER_FILE"
chmod +x "$ENTRY_POINT"

echo "==> Success! Application launcher successfully linked to: $LAUNCHER_FILE"
echo -e "\nYou can now open a new terminal session and type 'merlin'."
