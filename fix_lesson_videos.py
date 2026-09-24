#!/usr/bin/env python3
import sys
import re
import json

try:
    import json5
except ImportError:
    print("json5 not installed, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "json5"])
    import json5

def main():
    filename = '/home/pedrolopes/Downloads/T12-GitHub/script.js'
    with open(filename, 'r') as f:
        content = f.read()

    # Find the LESSON_VIDEOS assignment
    # We'll look for: const LESSON_VIDEOS = { ... };
    pattern = r'const LESSON_VIDEOS\s*=\s*(\{.*?\});'
    # Use DOTALL to match across lines
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("ERROR: Could not find LESSON_VIDEOS")
        sys.exit(1)

    # The JSON-like string is in group 1
    json_like = match.group(1)

    # Parse with json5 (which handles trailing commas, etc.)
    try:
        lesson_videos = json5.loads(json_like)
    except Exception as e:
        print(f"ERROR: Failed to parse LESSON_VIDEOS with json5: {e}")
        sys.exit(1)

    # Ensure aplicativos-computacionais exists
    if 'aplicativos-computacionais' not in lesson_videos:
        print("ERROR: Key 'aplicativos-computacionais' not found")
        sys.exit(1)

    # Process each lesson
    apps = lesson_videos['aplicativos-computacionais']
    total_added = 0
    for lesson_id, videos in apps.items():
        if not isinstance(videos, list):
            print(f"WARNING: Lesson {lesson_id} does not have a list of videos, skipping")
            continue
        # Count current videos
        current_len = len(videos)
        if current_len < 3:
            needed = 3 - current_len
            for i in range(needed):
                placeholder_id = f'placeholder{current_len + i + 1:02d}'
                placeholder_title = f'Vídeo explicativo {current_len + i + 1}'
                placeholder_description = 'Vídeo de apoio à aula'
                placeholder = {
                    'id': placeholder_id,
                    'title': placeholder_title,
                    'description': placeholder_description,
                    'platform': 'YouTube',
                    'language': 'Português'
                }
                videos.append(placeholder)
                total_added += 1
            print(f"Added {needed} placeholders to {lesson_id} (now {len(videos)} videos)")

    # Convert back to JSON-like string with json5's dumps (which outputs standard JSON)
    # We want to keep the same formatting as much as possible, but json5.dumps will produce valid JSON.
    # We'll then replace the old JSON-like string with the new one.
    new_json_like = json5.dumps(lesson_videos, indent=2, trailing_comma=False)
    # Note: json5.dumps does not add trailing commas by default.

    # Replace the old JSON-like string in the content
    new_content = content[:match.start(1)] + new_json_like + content[match.end(1):]

    # Write back
    with open(filename, 'w') as f:
        f.write(new_content)

    print(f"SUCCESS: Updated LESSON_VIDEOS, added {total_added} placeholders total.")

if __name__ == '__main__':
    main()