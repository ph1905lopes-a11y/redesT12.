#!/usr/bin/env python3
import sys
import re

def find_matching_brace(s, start_idx, open_char='{', close_char='}'):
    """Return index of matching close_char for open_char at start_idx."""
    depth = 0
    i = start_idx
    while i < len(s):
        ch = s[i]
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def find_matching_bracket(s, start_idx, open_char='[', close_char=']'):
    """Return index of matching close_char for open_char at start_idx."""
    depth = 0
    i = start_idx
    while i < len(s):
        ch = s[i]
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def main():
    filename = '/home/pedrolopes/Downloads/T12-GitHub/script.js'
    with open(filename, 'r') as f:
        content = f.read()

    # Find start of LESSON_VIDEOS
    start_pattern = r'const LESSON_VIDEOS = \{'
    match = re.search(start_pattern, content)
    if not match:
        print("ERROR: Could not find LESSON_VIDEOS start")
        sys.exit(1)
    start_idx = match.start()
    # Find the opening brace after '= '
    brace_start = content.find('{', start_idx)
    if brace_start == -1:
        print("ERROR: Could not find opening brace")
        sys.exit(1)
    # Find matching closing brace
    brace_end = find_matching_brace(content, brace_start)
    if brace_end == -1:
        print("ERROR: Could not find matching closing brace")
        sys.exit(1)

    # Extract the object string (including outer braces)
    object_str = content[brace_start:brace_end+1]
    # Remove outer braces
    inner = object_str[1:-1]

    # Find aplicativos-computacionais block
    apps_pattern = r'"aplicativos-computacionais"\s*:\s*\{'
    apps_match = re.search(apps_pattern, inner)
    if not apps_match:
        print("ERROR: Could not find aplicativos-computacionais")
        sys.exit(1)
    apps_start = apps_match.end()
    # Find matching closing brace for apps block
    apps_end = find_matching_brace(inner, apps_start)
    if apps_end == -1:
        print("ERROR: Could not find matching closing brace for aplicativos-computacionais")
        sys.exit(1)

    # Extract apps inner content
    apps_inner = inner[apps_start:apps_end]

    # We'll process the apps_inner by finding each lesson array
    # We'll build a new apps_inner string
    new_apps_parts = []
    last_pos = 0
    i = 0
    total_added = 0
    while i < len(apps_inner):
        # Look for the start of a lesson array: pattern '"aula-XX": ['
        # We'll use a simple search
        match_arr = re.search(r'"aula-\d+"\s*:\s*\[', apps_inner[i:])
        if not match_arr:
            # No more lesson arrays, append the rest
            new_apps_parts.append(apps_inner[i:])
            break
        # Append text before the match
        new_apps_parts.append(apps_inner[i:i+match_arr.start()])
        arr_start = i + match_arr.start()
        # Find matching closing bracket for this array
        arr_end = find_matching_bracket(apps_inner, arr_start)
        if arr_end == -1:
            # Should not happen
            new_apps_parts.append(apps_inner[i:])
            break
        # Extract the array string (including brackets)
        array_str = apps_inner[arr_start:arr_end+1]
        # Count video objects inside the array
        inner_array = array_str[1:-1]  # remove '[' and ']'
        # Count lines that contain 'id:' (each video object has an id line)
        video_count = sum(1 for line in inner_array.splitlines() if 'id:' in line)
        needed = max(0, 3 - video_count)
        if needed > 0:
            # Determine indentation for placeholders
            # We'll look at the first line of the inner_array to guess the indentation
            lines = inner_array.splitlines()
            indent_obj = None
            indent_prop = None
            for line in lines:
                if line.lstrip().startswith('{'):
                    # This is the start of an object
                    indent_obj = len(line) - len(line.lstrip())
                    # The next non-empty line that starts with a property (like 'id:')
                    for j in range(lines.index(line)+1, len(lines)):
                        prop_line = lines[j]
                        if prop_line.lstrip().startswith('id:'):
                            indent_prop = len(prop_line) - len(prop_line.lstrip())
                            break
                    break
            if indent_obj is None:
                # Fallback: compute from the array start line indentation
                # Find the line that contains the array start in apps_inner
                line_start = apps_inner.rfind('\n', 0, arr_start) + 1
                if line_start == 0:
                    line_start = 0
                line_content = apps_inner[line_start:arr_start]
                indent_array = len(line_content) - len(line_content.lstrip())
                indent_obj = indent_array + 2  # two more spaces for the object inside the array
                indent_prop = indent_obj + 2
            # Generate placeholder lines
            for k in range(needed):
                placeholder_id = f'placeholder{video_count + k + 1:02d}'
                placeholder_title = f'Vídeo explicativo {video_count + k + 1}'
                placeholder_description = 'Vídeo de apoio à aula'
                # Build lines with proper indentation
                new_apps_parts.append(' ' * indent_obj + '{')
                new_apps_parts.append(' ' * indent_prop + f'id: "{placeholder_id}",')
                new_apps_parts.append(' ' * indent_prop + f'title: "{placeholder_title}",')
                new_apps_parts.append(' ' * indent_prop + f'description: "{placeholder_description}",')
                new_apps_parts.append(' ' * indent_prop + 'platform: "YouTube",')
                new_apps_parts.append(' ' * indent_prop + 'language: "Português",')
                new_apps_parts.append(' ' * indent_obj + '},')
                total_added += 1
        # Append the original array string
        new_apps_parts.append(array_str)
        i = arr_end + 1

    # Join the new apps inner
    new_apps_inner = ''.join(new_apps_parts)
    # Rebuild inner: replace the old apps_inner with new
    inner_new = inner[:apps_start] + new_apps_inner + inner[apps_end:]
    # Rebuild object_str
    object_str_new = '{' + inner_new + '}'
    # Replace in content
    new_content = content[:brace_start] + object_str_new + content[brace_end+1:]
    # Write back
    with open(filename, 'w') as f:
        f.write(new_content)
    print(f"SUCCESS: Updated LESSON_VIDEOS, added {total_added} placeholders")

if __name__ == '__main__':
    main()