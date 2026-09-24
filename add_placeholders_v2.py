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

# Extract the LESSON_VIDEOS object string (including the outer braces)
lesson_videos_str = content[match.start():end_pos]  # from "const LESSON_VIDEOS = {" to the closing brace

# Now we want to parse the JSON part (without the variable assignment and semicolon).
# The string we have is: "const LESSON_VIDEOS = { ... };"
# We need to extract the { ... } part and then parse it as JSON.

# Actually, we have the entire assignment including the variable name and the equals sign.
# Let's adjust: we want the JSON string that is assigned.
# We can do: remove the "const LESSON_VIDEOS = " and the trailing ";"

# But note: the string we extracted is from the start of "const LESSON_VIDEOS = {" to the closing brace.
# So we can remove the first part until the '{' and then we have the JSON object string.

# Let's get the JSON object string by removing the prefix until the first '{'
json_str = lesson_videos_str[lesson_videos_str.index('{'):]  # This will be the JSON object including the outer braces.

# Now try to parse it as JSON.
try:
    lesson_videos = json.loads(json_str)
except json.JSONDecodeError as e:
    print(f"Failed to parse as JSON: {e}")
    # Try to fix by removing trailing commas
    # We'll do a simple regex to remove trailing commas before closing braces and brackets.
    # This is not perfect but might work for our case.
    fixed = re.sub(r',\s*([\]\}])(?:(?!\}].)*$)', r'\1', json_str, flags=re.DOTALL)
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
new_json_str = json.dumps(lesson_videos, indent=2)
# Now we need to put it back into the assignment.
# The original assignment was: "const LESSON_VIDEOS = " + json_str + ";"
# We'll replace the json_str part with new_json_str, keeping the rest.

# We have the original lesson_videos_str which is "const LESSON_VIDEOS = " + json_str + ";"
# We want to replace the json_str inside it with new_json_str.

# Let's reconstruct the new assignment:
new_lesson_videos_str = "const LESSON_VIDEOS = " + new_json_str + ";"

# Now replace the old lesson_videos_str in the content with the new one.
new_content = content.replace(lesson_videos_str, new_lesson_videos_str, 1)

# Write back to the file
with open('/home/pedrolopes/Downloads/T12-GitHub/script.js', 'w') as f:
    f.write(new_content)

print("Successfully updated script.js with placeholder videos.")