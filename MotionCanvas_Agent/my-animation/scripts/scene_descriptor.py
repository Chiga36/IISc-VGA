import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env file or environment variables.")
        exit()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    exit()


PROMPT_TEMPLATE = """
You are a WORLD-CLASS Motion Graphics Architect and Instruction Translator.
Your role is to take a complex educational or technical topic and convert it into a fully-structured, step-by-step JSON animation script.
This JSON script will be consumed directly by an AI-powered animation engine (Motion Canvas), meaning that every detail you provide will translate directly into shapes, text, and animations on screen.

Your primary purpose is:
1. To break down the input topic *"{topic}"* into a series of logically connected animated scenes(5-6 scenes).
2. To design the scenes so they form a **continuous explainer video** with smooth visual and conceptual flow.
3. To output the animation plan as a **valid JSON array of scene objects**, following strict formatting and schema rules.
4. To act as a hyper-literal translator: every element, placement, style, and transition must be explicitly defined. Nothing is left to assumption.

{feedback_section}

============================
INPUT SPECIFICATION
============================
The input provided to you will consist of the following:
- **Topic:** A string that describes the overall concept to explain. Example: "How a sine wave works"
- **Content Description:** A detailed explanation of the topic, broken down into steps, concepts, or parts.
- **Target Audience:** The intended viewers (e.g., high school students, engineering students, general public).
- **Design Style:** Any constraints or preferences for visuals (e.g., minimal, colorful, dark mode, whiteboard style).

You must read this input carefully and use it to construct scenes that are accurate, clear, and visually consistent.

============================
LAYOUT & DESIGN RULES
============================
Follow these layout rules step by step to maintain clarity and avoid ambiguity:
1. Divide the screen into two regions:
   - Left (40%): For visualizations such as shapes, diagrams, or animations.
   - Right (60%): For text content such as titles, definitions, explanations, or formulas.
2. Always align text content to the right region in a readable format.
3. Keep visuals on the left simple and directly tied to the explanation. Avoid irrelevant graphics.
4. Each new concept should either:
   - Introduce a **new visual element**, or
   - **Modify an existing one** (using transitions for continuity).
5. Ensure balance: visuals should not overlap text. Maintain padding and clean spacing.
6. Colors should be consistent across scenes. Do not randomly change them unless the change communicates meaning.
7. Use stepwise build-ups: text or visuals appear progressively instead of all at once.

Example (few-shot style):
- Scene 1 introduces axes and a sine curve outline.
- Scene 2 modifies the same sine curve to animate wave motion, while keeping axes.
- Scene 3 fades out the sine curve and introduces the equation on the right.

============================
BEST PRACTICES
============================
Follow these best practices at all times to maintain precision and predictable results:
1. Always match visual elements to the exact text explanation being presented.
2. Reuse existing elements whenever possible instead of redrawing them, to keep continuity.
3. Use clear, simple transitions ("fadeOut", "modify", "keep") to manage scene flow.
4. Maintain consistent identifiers (target_id) for the same object across multiple scenes.
5. Keep scene durations practical (5–15 seconds depending on complexity).
6. Avoid unnecessary effects or randomness. Stick to clarity and teaching value.
7. Every object must have a purpose. Do not add decoration-only visuals unless explicitly requested.

============================
JSON SCHEMA
============================
The output JSON must strictly follow this schema:
{JSON_SCHEMA}

*JSON Schema Explanation:*
-   scene_number: The order of the scene.
-   scene_title: A descriptive title.
-   duration: Estimated time in seconds.
-   transitions: An array describing how to handle elements from the previous scene.
-   actions: An object containing 'visualization' and 'writing' arrays.
-   Each action in these arrays is an object with:
    -   command: The action to perform (e.g., 'create', 'animate', 'modify', 'highlight', 'fadeOut').
    -   type: The kind of object (e.g., 'path', 'line', 'circle', 'text', 'latex').
    -   target_id: A UNIQUE, descriptive ID for the element (e.g., "costCurve", "titleText").
    -   properties: A dictionary of all visual attributes (position, color, text content, coordinates, etc.).
-   In the `writing` actions, the `properties` object **MUST** contain a `text` property with the string to be displayed.

============================
PRINCIPLE OF CONTINUITY
============================
Continuity ensures that the viewer can follow the animation smoothly across scenes.
To maintain continuity, follow these simple rules:

1. **Scene Linking:** Each new scene must either keep existing objects, modify them, or fade them out — never remove or replace objects abruptly.
2. **Transitions:** Use the `transitions` field in the schema to specify what happens to each object.
   - Example: An axis stays in place → action: "keep".
   - Example: A circle changes color → action: "modify" with new_properties.
   - Example: A title is removed → action: "fadeOut".
3. **Consistency:** The same `target_id` should always represent the same object throughout the video.
4. **Few-Shot Prompting Example:**
   - Scene 1: Introduce X and Y axes (target_id: "axes").
   - Scene 2: Keep "axes", add sine curve (target_id: "sine_curve").
   - Scene 3: Modify "sine_curve" to animate wave, keep "axes".
   - Scene 4: FadeOut "sine_curve", keep "axes", add equation text.

============================
OUTPUT FORMAT
============================
The final output must be a valid JSON array, where each element is one scene following the schema.
Do not include explanations or commentary outside the JSON.
"""

# --- The JSON Schema Definition (FIXED) ---
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "scene_number": {"type": "integer"},
        "scene_title": {"type": "string"},
        "duration": {"type": "number"},
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["keep", "fadeOut", "modify"]},
                    "target_id": {"type": "string"},
                    "new_properties": {
                        "type": "object",
                        "properties": {
                            "placeholder": {"type": "string"}
                        }
                    }
                },
                "required": ["action", "target_id"]
            }
        },
        "actions": {
            "type": "object",
            "properties": {
                "visualization": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "type": {"type": "string"},
                            "target_id": {"type": "string"},
                            "properties": {
                                "type": "object",
                                "properties": {
                                    "placeholder": {"type": "string"}
                                }
                            }
                        },
                        "required": ["command", "type", "target_id", "properties"]
                    }
                },
                "writing": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "type": {"type": "string"},
                            "target_id": {"type": "string"},
                            "properties": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"}
                                }
                            }
                        },
                        "required": ["command", "type", "target_id", "properties"]
                    }
                }
            }
        }
    },
    "required": ["scene_number", "scene_title", "duration", "transitions", "actions"]
}

def generate_scene_description(topic: str, feedback: dict = None, token_tracker = None) -> dict:
    """
    Generates a scene description JSON for a given topic using the Gemini API.
    """
    print(f"Generating professional JSON script for topic: {topic}...")

    feedback_section = ""
    if feedback:
        feedback_section = f"""
============================
FEEDBACK FROM PREVIOUS ATTEMPT
============================

The previous attempt to generate the animation had the following issues:
{json.dumps(feedback, indent=2)}

Please analyze this feedback carefully and generate a new, improved scene description that addresses these issues.
"""

    final_prompt = PROMPT_TEMPLATE.format(topic=topic, feedback_section=feedback_section, JSON_SCHEMA=json.dumps(JSON_SCHEMA, indent=2))

    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "array",
            "items": JSON_SCHEMA
        }
    }

    try:
        response = model.generate_content(
            final_prompt,
            generation_config=generation_config
        )

        # Track token usage if token_tracker is provided
        if token_tracker:
            try:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                token_tracker.add("SceneDescriptor", topic, input_tokens, output_tokens)
            except AttributeError:
                # Fallback if usage_metadata is not available
                pass

        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred during API call or JSON parsing: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print("Raw API response text:", response.text)
        return {"error": str(e)}

if __name__ == "__main__":
    user_topic = input("Enter the topic for the explainer video: ")

    if user_topic:
        scene_script_json = generate_scene_description(user_topic)

        # Check for error before proceeding
        if "error" not in scene_script_json:
            pretty_json_output = json.dumps(scene_script_json, indent=2)

            print("\n--- Generated Scene Script (JSON) ---")
            print(pretty_json_output)

            # Save the pretty-printed JSON to a file
            file_name = f"{user_topic.replace(' ', '_').lower()}_script.json"
            with open(file_name, "w") as f:
                f.write(pretty_json_output)
            print(f"\nScript also saved to {file_name}")
        else:
            print(f"\nCould not generate script due to an error: {scene_script_json['error']}")
