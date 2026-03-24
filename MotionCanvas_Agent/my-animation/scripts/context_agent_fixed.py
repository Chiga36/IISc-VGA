import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Assumes the 'examples' folder is in the parent directory ('my-animation/')
EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples'))

# --- Gemini API Configuration ---
try:
    import google.generativeai as genai
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except ImportError:
    print("Fatal Error: google-generativeai not installed. Run: pip install google-generativeai")
    model = None
except Exception as e:
    print(f"Fatal Error configuring Gemini API in Context Agent: {e}")
    model = None

CONTEXT_SELECTION_PROMPT = """
You are a Motion Canvas animation framework expert. Select the most technically relevant example files for this animation scene.

ANIMATION SCENE SPECIFICATION:
{scene_data}

SELECTION CRITERIA:
- Select the examples that best match the scene specification.
- Always include a foundational setup file if required (001_basic_scene_setup.tsx).
- Match files strictly to components, animations, or visual elements in the scene.
- Prioritize Core Framework > Geometry & Styling > Media Integration > Typography > Basic Animations > Layout & Composition > Mathematical Visualizations.
- Avoid duplicates or irrelevant selections.
- If no file is relevant, return an empty list.

OUTPUT FORMAT (JSON only):
{{
  "selected_examples": ["001_basic_scene_setup.tsx", "002_simple_rectangle.tsx", "004_basic_text.tsx"]
}}
"""

def get_relevant_examples(scene_data: Dict) -> Optional[Dict]:
    """Get relevant examples using the Gemini API."""
    if not model:
        print("❌ Gemini model not available. Cannot select examples.")
        return None

    try:
        # Format the scene data for the prompt
        formatted_scene = json.dumps(scene_data, indent=2)
        prompt = CONTEXT_SELECTION_PROMPT.format(
            scene_data=formatted_scene
        )

        # Get response from Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Try to parse JSON response
        import re
        json_match = re.search(r'\{[^}]*"selected_examples"[^}]*\}', response_text)
        if json_match:
            json_str = json_match.group()
            selected_files = json.loads(json_str)

            # Load the selected example files
            examples = {}
            if "selected_examples" in selected_files:
                for filename in selected_files["selected_examples"]:
                    file_path = os.path.join(EXAMPLES_DIR, filename)
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                examples[filename] = {
                                    "content": f.read(),
                                    "path": file_path
                                }
                        except Exception as e:
                            examples[filename] = {
                                "error": f"Failed to read file: {e}"
                            }
                    else:
                        examples[filename] = {
                            "error": "File not found"
                        }

            return {"examples": examples}
        else:
            print(f"❌ Could not parse JSON from response: {response_text}")
            return None

    except Exception as e:
        print(f"❌ Error getting examples: {e}")
        return None

def format_examples_for_prompt(examples: Dict[str, Dict]) -> str:
    """Format example files for inclusion in prompts."""
    if not examples:
        return "No examples found."

    formatted_examples = []
    for filename, data in examples.items():
        if data.get("error"):
            formatted_examples.append(f"**{filename}**: ERROR - {data['error']}")
            continue

        formatted_examples.append(f"**{filename}**:")
        formatted_examples.append("```tsx")
        # Escape curly braces in the content to prevent format string issues
        escaped_content = data["content"].replace("{", "{{").replace("}", "}}")
        formatted_examples.append(escaped_content)
        formatted_examples.append("```\n")

    return "\n".join(formatted_examples)

# --- Main Test Function ---
if __name__ == "__main__":
    test_scene = {
        "scene_title": "Colorful Shapes Introduction",
        "scene_description": "A complex scene with multiple blue rectangles, red circles, animated text with typewriter effect, gradient backgrounds, and smooth bounce animations",
        "visual_elements": ["Rect", "Circle", "Txt", "gradient"],
        "animations": ["fade_in", "position", "typewriter", "bounce", "scale", "rotate"],
        "colors": ["blue", "red", "gradient"],
        "text_content": ["Hello World", "Motion Canvas Demo", "Animated Introduction"]
    }

    print("Testing Enhanced Context Agent...")
    result = get_relevant_examples(test_scene)
    if result and result.get("examples"):
        examples = result["examples"]
        print(f"SUCCESS: Retrieved {len(examples)} examples with content")
        for filename, data in examples.items():
            if data.get("error"):
                print(f"  - {filename} (ERROR: {data['error']})")
            else:
                content = data.get("content")
                if isinstance(content, str):
                    content_preview = content[:100].replace('\n', ' ')
                    print(f"  - {filename} ({len(content)} chars): {content_preview}...")
                else:
                    print(f"  - {filename} (ERROR: No valid content found)")
    else:
        print("FAILED: No examples retrieved")
