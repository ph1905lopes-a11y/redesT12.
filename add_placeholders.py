import re
import json

# Read the file
with open('/home/pedrolopes/Downloads/T12-GitHub/script.js', 'r') as f:
    content = f.read()

# We'll try to extract the LESSON_VIDEOS object using a regex that matches from the start to the end of the object.
# However, note that the object might be nested and we don't want to match too much.
# Instead, we can look for the pattern: const LESSON_VIDEOS = { ... };
# We'll use a simple approach: find the start and then count braces until we match the end.

# Find the start of the LESSON_VIDEOS assignment
start_pattern = r'const LESSON_VIDEOS = {'
match = re.search(start_pattern, content)
if not match:
    print("Could not find LESSON_VIDEOS")
    exit(1)

start_pos = match.end()  # position after the '{'

# Now we need to find the matching closing brace for this object.
brace_count = 1
pos = start_pos
while pos < len(content) and brace_count > 0:
    if content[pos] == '{':
        brace_count += 1
    elif content[pos] == '}':
        brace_count -= 1
    pos += 1

if brace_count != 0:
    print("Could not find matching brace for LESSON_VIDEOS")
    exit(1)

end_pos = pos  # position after the closing brace

# Extract the LESSON_VIDEOS object string
lesson_videos_str = content[start_pos-1:end_pos]  # includes the braces

# Now we need to parse this string as JSON. However, note that it's a JavaScript object, not JSON.
# We can try to convert it to JSON by:
#   - Adding quotes around keys that don't have them (but in this case, the keys are already quoted? Actually, in the file we saw: "aula-01": [ ... ],
#   - The values are arrays of objects, and the objects have quoted keys.

# Actually, the LESSON_VIDEOS object in the file is valid JSON? Let's check a snippet:
#   "aplicativos-computacionais": {
#     "aula-01": [
#       { ... },
#       ...
#     ],
#     ...
#   }
# This is valid JSON if we remove the 'const LESSON_VIDEOS = ' and the trailing semicolon.

# So we can take the string between the braces and parse it as JSON.

# But note: the object we extracted includes the outer braces. We want to parse the content inside.
# Actually, we extracted from the '{' to the matching '}', so it's a JSON object.

# However, there might be trailing commas? In JavaScript, trailing commas in objects and arrays are allowed, but not in JSON.
# Let's check the file for trailing commas in the LESSON_VIDEOS object.

# We'll do a simple fix: remove trailing commas inside arrays and objects.

# Instead of writing a full JSON fixer, we can use the `demjson` library, but we don't have it installed.
# Alternatively, we can use `ast.literal_eval` after converting to a Python dict? Not straightforward.

# Let's try to parse as JSON and if it fails, we'll try to fix common issues.

# First, let's try to parse the extracted string as JSON.
try:
    lesson_videos = json.loads(lesson_videos_str)
except json.JSONDecodeError as e:
    print(f"Failed to parse as JSON: {e}")
    # Try to fix by removing trailing commas
    # We'll do a simple regex to remove trailing commas before closing braces and brackets.
    # This is not perfect but might work for our case.
    fixed = re.sub(r',\s*([}\]])(?:(?!\}].)*$)', r'\1', lesson_videos_str, flags=re.DOTALL)
    try:
        lesson_videos = json.loads(fixed)
    except json.JSONDecodeError as e2:
        print(f"Still failed: {e2}")
        exit(1)

# Now we have the lesson_videos as a Python dict.
# Ensure the 'aplicativos-computacionais' key exists.
if 'aplicativos-computacionais' not in lesson_videos:
    print("Key 'aplicativos-computacionais' not found in LESSON_VIDEOS")
    exit(1)

# Process each lesson in aplicativos-computacionais
aplicacoes = lesson_videos['aplicativos-computacionais']
for lesson_id, videos in aplicacoes.items():
    # Ensure videos is a list
    if not isinstance(videos, list):
        print(f"Lesson {lesson_id} does not have a list of videos")
        continue
    # While the length is less than 3, add placeholder videos
    while len(videos) < 3:
        placeholder_id = f'placeholder{len(videos)+1:02d}'
        placeholder_title = f'Vídeo explicativo {len(videos)+1}'
        placeholder_description = 'Vídeo de apoio à aula'
        placeholder = {
            'id': placeholder_id,
            'title': placeholder_title,
            'description': placeholder_description,
            'platform': 'YouTube',
            'language': 'Português'
        }
        videos.append(placeholder)
        print(f"Added placeholder to {lesson_id}: {placeholder_id}")

# Now we need to update the content with the modified LESSON_VIDEOS object.
# We'll convert the lesson_videos back to a JSON string and replace the old one.
# We want to keep the same formatting as much as possible, but for simplicity, we'll just replace the entire object.

# Convert back to JSON with indentation of 2 spaces.
new_lesson_videos_str = json.dumps(lesson_videos, indent=2)
# The original had the outer braces and the assignment. We'll replace from the start of the '{' to the end of the '}' with the new string.
# But note: we extracted the string including the outer braces. So we replace from start_pos-1 to end_pos with the new string.
new_content = content[:start_pos-1] + new_lesson_videos_str + content[end_pos:]

# Write back to the file
with open('/home/pedrolopes/Downloads/T12-GitHub/script.js', 'w') as f:
    f.write(new_content)

print("Successfully updated script.js with placeholder videos.")