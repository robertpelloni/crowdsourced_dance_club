with open("src/main.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Oh! `elif action == "VOTE_TRACK":` is duplicated at the bottom!
    if i == 1034 and "elif action == \"VOTE_TRACK\":" in line:
        skip = True

    if skip and "def run_offline_compiler_worker" in line:
        skip = False
        new_lines.append("        except Exception as e:\n")
        new_lines.append("            print(f'[ERROR] WebSocket logic failure: {e}')\n")
        new_lines.append("    except Exception as e:\n")
        new_lines.append("        manager.disconnect(websocket)\n")
        new_lines.append("        print(f'[WS] Client {display_name} disconnected: {e}')\n\n")

    if not skip:
        # Wrap everything in a try block
        if i == 853:
            new_lines.append("            try:\n")
            new_lines.append("                " + line.strip() + "\n")
            continue

        if i == 854:
            new_lines.append("                action = message.get(\"action\")\n")
            continue

        if i == 855:
            new_lines.append(line)
            continue

        if i >= 856 and i <= 1033:
            # We don't need to indent! Look, line 856 is `            if action == "GET_VIBE_SCORE":\n`
            # This is already indented by 12 spaces.
            # But the `try:` we just added is at 12 spaces.
            # So the block needs to be indented by 16 spaces!
            new_lines.append("    " + line)
            continue

        new_lines.append(line)

with open("src/main.py", "w") as f:
    f.writelines(new_lines)
