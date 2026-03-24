import os
import json
import re
import subprocess

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    print("Warning: google.generativeai not available. Install with `pip install google-generativeai`")
    GENAI_AVAILABLE = False
    genai = None

from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional
import time
import datetime  # For prompt logging timestamps

# Try to import context agent (it will call this script, so we check if it's available)
try:
    from context_agent import get_relevant_examples
    CONTEXT_AGENT_AVAILABLE = True
except ImportError:
    print("Warning: context_agent not available")
    CONTEXT_AGENT_AVAILABLE = False
    get_relevant_examples = None  # You will call the context agent from run_pipeline.py

load_dotenv()  # This script is now a library, so we load env vars when it's imported.

# Get the absolute path of the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (which is one level up from the script's directory)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# **NEW: Create prompt logs directory for debugging**
PROMPT_LOGS_DIR = os.path.join(PROJECT_ROOT, "prompt_logs")
os.makedirs(PROMPT_LOGS_DIR, exist_ok=True)
print(f"📝 Prompt logging enabled: {PROMPT_LOGS_DIR}")

# Define all paths as absolute paths based on the project root
PROJECT_FILE = os.path.join(PROJECT_ROOT, "src", "project.ts")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
SCENES_DIR = os.path.join(PROJECT_ROOT, "src", "scenes")
EXAMPLES_DIR = os.path.join(SCRIPT_DIR, "examples")
SSML_DIR = os.path.join(SCRIPT_DIR, "ssml")

# --- Gemini API Configuration ---
if GENAI_AVAILABLE:
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found in .env file or environment variables.")
            GENAI_AVAILABLE = False
            model = None
        else:
            genai.configure(api_key=api_key)
            # Corrected model name to a valid one, assuming flash is desired.
            model = genai.GenerativeModel('gemini-2.5-pro')
    except Exception as e:
        print(f"Warning: Error configuring Gemini API: {e}")
        GENAI_AVAILABLE = False
        model = None
else:
    model = None
# --- Enhanced Code Generation Prompt ---
CODE_GENERATION_PROMPT = r"""

### ROLE AND PURPOSE
- **Role**: You are an Expert Motion Canvas Layout Engineer, Visual Choreographer, and Code Generator.
- **Purpose**: Your primary goal is to take a high-level SEMANTIC plan from the provided JSON and convert it into a visually stunning, precisely calculated, flawlessly animated, and highly educational Motion Canvas scene. You are solely responsible for all coordinate calculations, layout logic, and ensuring the visual narrative is captivating and on-point.

### CANVAS LAYOUT:
- Canvas size: 1920 × 1080, centered coordinates (0,0 at center).
- Visualization Zone (Left 40%): x coordinates must be < -192.
- Writing Zone (Right 60%): x coordinates must be > -192.

### INPUT FORMAT
- **Scene Description JSON**: {json_data} - A high-level semantic plan describing the scene's intent, layout framework, and sequence of actions.
- **Reference Example Code Files**: {reference_examples} - A collection of correct code patterns.

### CRITICAL IMPORTS (USE EXACTLY THESE)
```typescript
import {{{{makeScene2D}}}} from '@motion-canvas/2d/lib/scenes';
import {{{{Rect, Circle, Txt, Layout, Line, Latex}}}} from '@motion-canvas/2d/lib/components';
import {{{{all, waitFor, chain}}}} from '@motion-canvas/core/lib/flow';
import {{{{createRef}}}} from '@motion-canvas/core/lib/utils';
import {{{{Vector2, Color}}}} from '@motion-canvas/core/lib/types';
import * as easing from '@motion-canvas/core/lib/tweening';
```

### **CONTENT INJECTION (CRITICAL)**
- **ALL** text content (e.g., `Txt` components, labels, descriptions) and numerical values (e.g., for `Rect` or `Circle` sizes, positions, or `action.value` for nodes/cells) **MUST** be extracted directly from the provided `Scene Description JSON` (`{json_data}`).
- **NEVER** use placeholder text like "Scene 1 text", "Node 1", "Data", "Next", or generic numerical values unless explicitly specified in the `json_data`.
- If the `json_data` provides a `value` for an element, use that `value` as the text content for the corresponding `Txt` component.
- If the `json_data` provides `scene_title` or `scene_description`, use those exact strings for the respective `Txt` components.
- **Example**: To access the label for an element, you would typically find it at `scene_data.elements[index].label` or `action.label` depending on the context of the action.

---

### **VISUALIZATION FRAMEWORK LIBRARY (MANDATORY)**
- **CRITICAL VISUAL PLACEMENT**: All visual elements generated using these frameworks **MUST** be strictly confined to the Visualization Zone (Left 40%, `x < -192`). Their coordinates and sizes must be calculated precisely to fit within this area without overflow or overlap with the Writing Zone.
When the JSON specifies a `visual_metaphor`, you **MUST** use the corresponding framework below to calculate all positions and generate the visualization.

#### **Framework for Metaphor: "a container being filled" or "stack"**
- **Container (`Rect`):**
  - Position: `x: -550`, `y: 0`
  - Size: `width: 200`, `height: 450`
  - Style: `stroke: '#1E293B'`, `lineWidth: 8`
- **Items (`Rect` with `Txt` child):**
  - Size: `width: 180`, `height: 70`
  - **Labeling**: Each item `Rect` **MUST** contain a `Txt` child displaying its `label` (from JSON `element.label`), centered within the `Rect`.
  - Initial Position (before push): `x: -550`, `y: -300` (above the container)
  - **Push Logic**: The first item's target `y` is `200`. Each subsequent item's target `y` is `(previous_item.y) - (item_height + 10)`. Items are placed from the bottom up.
  - **Pop Logic**: Animate the top-most item's position to `x: -250` (to the right) and `y: -300` (up), then fade its opacity to 0.

#### **Framework for Metaphor: "an indexed list" or "array"**
- **Cells (`Rect`):**
  - Initial Position: `x: -700`, `y: -100`
  - Size: `width: 100`, `height: 100`
  - **Labeling**: Each cell `Rect` **MUST** contain a `Txt` child displaying its `label` (from JSON `element.label`), centered within the `Rect`.
  - **Placement Logic**: The first cell is at the initial `x`. Each subsequent cell's `x` is `(previous_cell.x) + (cell_width + 10)`. All cells share the same `y`.
- **Item Labels (`Txt`):**
  - Position: Same `x` as the corresponding cell, `y: -100` (centered with the cell).
- **Index Labels (`Txt`):**
  - Position: Same `x` as the corresponding cell, `y: -25` (75px below the cell's center).

#### **Framework for Metaphor: "connected nodes" or "graph"**
- **Nodes (`Circle` with `Txt` child):**
  - Size: `100`
  - **Labeling**: Each node `Circle` **MUST** contain a `Txt` child displaying its `label` (from JSON `element.label`), centered within the `Circle`.
  - **Placement Logic**: Distribute nodes evenly in the Visualization Zone. Avoid overlaps. A simple grid or circular pattern is effective.
- **Edges (`Line`):**
  - Use the `from` and `to` properties in the action to get the `id`s of the start and end nodes.
  - The line's `points` should be `[startNodeRef().position(), endNodeRef().position()]`. Animate the line drawing using the `end` property.

---

### **ANIMATION DETAIL & PRECISION (MANDATORY)**
- **Captivating Animations**: Animations are the core of visual explanation. They **MUST** be dynamic, engaging, and clearly illustrate the concept. Think about how to make the visuals "pop" and guide the viewer's eye.
- **Descriptive Animations**: Animations should go beyond basic movements. Use visual cues like temporary highlights, color changes, or subtle scaling to emphasize actions and transitions.
- **Intermediate States**: Where applicable, animate through intermediate states to clearly show how a transformation occurs (e.g., an element moving from A to B should show its path, not just appear at B).
- **Purposeful Easing**: Utilize `easing` functions (e.g., `easing.easeOutBounce`, `easing.easeInOutCubic`) to give animations a natural and professional feel, reflecting the action's nature.

---

### ❌ ABSOLUTELY FORBIDDEN - TEXT OVERLAP PATTERNS ❌
**These patterns cause text overlap and are BANNED:**
<Txt x={300} y={-450} text="Title" fontSize={48} />
<Txt x={300} y={-380} text="Description" fontSize={32} />

**✅ ONLY ALLOWED PATTERN - USE THIS EXACT STRUCTURE:**
<Layout x={300} y={-200} direction={'column'} gap={50} alignItems={'flex-start'} width={'60%'}>
  <Txt text="Scene Title" fontSize={48} fontWeight={700} fill={'#333'} />
  <Txt text="Scene description text" fontSize={32} fill={'#555'} wrap={true} />
</Layout>

**VIOLATION = AUTOMATIC FAILURE. FOLLOW EXACTLY.**

---

### **TEXT LAYOUT AND WRAPPING RULES (MANDATORY)**
**CRITICAL: SINGLE LAYOUT CONTAINER ENFORCEMENT**
1. **MANDATORY POSITIONING PATTERN:**
<Txt ref={titleRef} x={300} y={-300} text={formatText(scene_data.scene_title)} fontSize={36} fontWeight={700} fill={'#333'} opacity={0} />
<Txt ref={descRef} x={300} y={-150} text={formatText(scene_data.scene_description)} fontSize={24} fill={'#555'} opacity={0} />
<Txt ref={contentRef} x={300} y={0} text={formatText("Additional explanation")} fontSize={20} fill={'#666'} opacity={0} />

2. **ABSOLUTE PROHIBITIONS:**
   - NEVER use Layout containers (they're causing overlap)
   - NEVER use y coordinates closer than 150px apart
   - NEVER put text at y > 400 or y < -400

3. **MANDATORY SPACING:** Title at y={-300}, Description at y={-150}, Content at y={0}

4. **Content Generation**: Generate comprehensive educational text derived from `actions` and `explanations` in the `json_data`

5. **Text Wrapping**: Long strings MUST NOT use `wrap={true}` property (it causes compilation errors). Manual line breaks with `\n` if needed

6. **AUTOMATIC LINE BREAKING**: ALL text strings MUST be broken into lines at sentence boundaries:
   - Split long sentences at periods (.) into separate lines
   - Maximum 50 characters per line for readability  
   - Use \n for line breaks in text strings
   - Example: "This is sentence one.\nThis is sentence two.\nThis is sentence three."

7. **TEXT PROCESSING FUNCTION**: ALWAYS include this function:
function formatText(text: string): string {
    // Simple sentence splitting for Motion Canvas
    return text.replace(/\. /g, '.\n').replace(/\n+/g, '\n').trim();
}

8. **MANDATORY TEXT FORMATTING**: Every Txt component MUST use formatted text:
<Txt ref={descRef} x={300} y={-150} text={formatText(scene_description)} fontSize={24} fill={'#555'} opacity={0} />

9. **CRITICAL: DO NOT RENDER METADATA/ENHANCEMENT MARKERS**: 
   - scene_description may contain enhancement markers enclosed in brackets or special delimiters:
     * "[Enhanced: ...]"
     * "--- USER REQUESTED ENHANCEMENTS ---"
     * "[SYSTEM INSTRUCTION ...]"
     * "[INTERNAL NOTE ...]"
     * Any text within square brackets [ ]
   
   - **THESE ARE INSTRUCTIONS FOR YOU, NOT CONTENT TO RENDER**
   - **NEVER create Txt components displaying these markers in the video**
   - Parse enhancement requests and implement them as VISUAL ELEMENTS (Circle, Rect, Line, etc.)
   - Only render the actual educational content text
   
   - **CRITICAL PARSING RULE**: 
     * Extract ONLY the core educational text from scene_description
     * Remove all bracketed instructions before creating Txt components
     * Implement enhancement requests by adding corresponding visual components
   
   - **Example Parsing:**
     ```
     Input scene_description: 
     "This scene shows gravity. [Enhanced: add a small ball] Gravity attracts objects."
     
     ✅ CORRECT Implementation:
     - Create Txt: "This scene shows gravity. Gravity attracts objects."
     - Add Circle component (the requested ball)
     
     ❌ WRONG Implementation:
     - Create Txt: "This scene shows gravity. [Enhanced: add a small ball] Gravity attracts objects."
     ```
   
   - **Additional Examples:**
     ```
     Input: "Introduction to arrays.\n--- USER REQUESTED ENHANCEMENTS ---\n1. add red circle\n--- END ENHANCEMENTS ---\nArrays store data."
     
     ✅ CORRECT:
     - Txt: "Introduction to arrays. Arrays store data."
     - Add Circle with fill={'#FF0000'}
     
     ❌ WRONG:
     - Txt showing "--- USER REQUESTED ENHANCEMENTS ---"

---

### **THE ANIMATION BLUEPRINT (MANDATORY)**
You **MUST** construct the `makeScene2D` generator function by following this exact, step-by-step blueprint.

#### **STEP 0: PRE-PROCESS SCENE DATA (MANDATORY)**
1.  **Clean scene_description**: Before using scene_description in any Txt component:
    - Remove all text between and including "[Enhanced:" and the next "]"
    - Remove all lines containing "USER REQUESTED ENHANCEMENTS"
    - Remove all text between and including "[SYSTEM INSTRUCTION" and "[END SYSTEM INSTRUCTION]"
    - Remove all text between and including "[INTERNAL NOTE" and "[END INTERNAL NOTE]"
    - Extract enhancement keywords (e.g., "add a small ball") and store them for creating visual components

2.  **Parse Enhancement Requests**: 
    - If scene_description contains enhancement instructions, parse them to understand what visual elements to add
    - Example: "[Enhanced: add red ball]" means create a Circle component with fill={'#FF0000'}
    - Example: "[Enhanced: make elements bounce]" means add bounce easing to animations

3.  **Store Clean Text**: Use the cleaned scene_description for all Txt components


#### **STEP 1: STAGING THE SCENE**
1.  **Background**: Add the white background.
2.  **Reference Declaration**: Create `createRef` variables for every `id` in the JSON's `elements`, `actions` and `explanations`. **Additionally, create `createRef` variables for the scene title and scene description.**
3.  **Calculate Positions**: **Before writing any JSX**, perform all necessary coordinate calculations based on the specified `visual_metaphor` from the library above. Store these calculated positions in variables.
    *   **MANDATORY FIXED TEXT POSITIONS**: 
        - Scene Title: x={300}, y={-300} (fontSize={48})
        - Scene Description: x={300}, y={-150} (fontSize={32}) 
        - Additional Content: x={300}, y={50} (fontSize={24})
    *   **ABSOLUTE RULE**: Text elements MUST be exactly 150px apart vertically
    *   **Visual Elements**: Calculate positions for visual elements within left 40% zone only
4.  **Initial Composition**: Add all elements to the scene using `view.add()`. Every element **MUST** be created with `opacity={{0}}` and positioned using your calculated coordinates. **Ensure the scene title and description are added here.** **Crucially, ensure all visual elements (Rect, Circle, Line, etc.) derived from `scene_data.elements` are created and placed within the Visualization Zone (left 40%).**

#### **STEP 2: CHOREOGRAPHING THE ANIMATION**
1.  **Initial Scene Introduction**: At the very beginning of the scene, animate the ENTIRE Layout container fading in.
    *   ALL text (scene_title, scene_description, content) goes inside ONE Layout component
    *   `scene_title` styling: `fontSize: 48`, `fontWeight: 700`, `fill: '333'`
    *   `scene_description` styling: `fontSize: 32`, `fill: '555'`
    *   Layout automatically handles spacing - NO individual positioning
2.  **Follow the Actions & Explanations (CRITICAL)**: Iterate through the `actions` array from the JSON. Each action corresponds to an animation block. **Crucially, for each action, you MUST also identify and animate its corresponding explanation text from the `explanations` array (if present in the JSON).**
3.  **Synchronize Visuals and Text**: For each action (e.g., `CREATE_NODE`), create a `yield* all(...)` block. Inside this block, animate the visual element (e.g., the node appearing) AND its corresponding explanation text (from the `explanations` array) fading in. **Ensure the text appears in the Writing Zone (right 60%) and is synchronized with the visual animation.**
4.  **Pace for Clarity**: After each `yield* all(...)` block, you **MUST** add a `yield* waitFor(1);` to create a deliberate pause.

#### **STEP 3: SCENE CONCLUSION**
1.  **Final Wait**: The last line **MUST** be `yield* waitFor(duration);` using the scene `duration` from the JSON.

### OUTPUT INSTRUCTIONS
- Generate ONLY the raw TypeScript code.
- You **MUST** strictly follow the blueprint and use the Visualization Framework Library for all layout calculations.
- The resulting code must produce a precisely calculated, well-paced, and narratively coherent animation.
"""


ERROR_ANALYSIS_PROMPT = r"""
### ROLE AND GOAL
- **Role**: You are an expert Motion Canvas v3.17.29 debugger.
- **Goal**: Your sole purpose is to analyze the provided code, errors, and feedback to generate a fully corrected, compilable, and logically sound version of the Motion Canvas scene.

### CONTEXT & INPUTS

1.  **Original Scene Description:** The user's original intent.
    ```json
    {scene_data}
    ```

2.  **Faulty Generated Code:** The code that needs to be fixed.
    ```typescript
    {code}
    ```

3.  **Compilation/Runtime Errors:** The specific errors thrown by the compiler or at runtime.
    ```
    {errors}
    ```

4.  **Validation Feedback:** Additional issues found during validation.
    ```
    {validation_feedback}
    ```

5.  **Reference Code Examples:** Correct code patterns to follow.
    ```json
    {reference_examples}
    ```

### PRIMARY TASK
Analyze all the inputs provided above. Your task is to meticulously review the **Faulty Generated Code** in light of the **Compilation/Runtime Errors** and **Validation Feedback**. You **MUST** identify the root cause of each error and generate a **completely corrected and improved version** of the Motion Canvas scene. The final output must be a complete, error-free TypeScript scene that respects the **Original Scene Description** and resolves ALL reported issues.

### CRITICAL DEBUGGING CHECKLIST & API RULES

**1. Address All Provided Issues:**
   - You **MUST** fix every point mentioned in the **Compilation/Runtime Errors**.
   - You **MUST** address every piece of **Validation Feedback**.

**1.5. Iterative Correction & Prioritization:**
   - When presented with compilation errors, your absolute top priority is to resolve them first. Do not attempt to fix other issues until the code compiles successfully.
   - Consider the previous faulty code and identify the minimal changes required to fix the reported errors. Avoid unnecessary modifications.


**2. Fix Logical & Runtime Errors:**
   - **Scene Title/Description**: Ensure the scene title and description are present, correctly positioned, and readable at the beginning of the scene.
   
   - **METADATA FILTERING**: Before creating any Txt components from scene_description:
     * Remove all bracketed enhancement markers: [Enhanced: ...], [SYSTEM INSTRUCTION ...], etc.
     * Remove delimiter lines: "--- USER REQUESTED ENHANCEMENTS ---"
     * Only display the actual educational content in Txt components
     * Implement enhancement requests as visual components, not text
   
   - **MANDATORY**: Every element created with `createRef()` **MUST** be added to the scene...


**3. Animation & Timing Corrections:**
   - **VISIBILITY**: Ensure all elements are visible on the canvas and animate as intended. Fix properties that might cause them to be off-screen or have zero opacity incorrectly.
   - **DURATION**: Adjust animation timings to be smooth and perceptible. Individual animations should last at least 1 second.
   - **PACING**: Insert `yield* waitFor(1);` between major, distinct animation steps to improve the scene's rhythm.
   - **TOTAL DURATION**: The entire scene's runtime should be between 3 to 5 seconds. End the scene with a final `yield* waitFor(...)`.

**4. Adhere to Motion Canvas v3.17.2 API (NO HTML/CSS HALLUCINATIONS):**
   - **MENTAL MODEL**: The syntax is JSX-like, but it is **NOT** a web DOM. Do not use CSS properties.

### **SELF-CORRECTION & LEARNING (CRITICAL)**
- **Review Previous Attempt**: Carefully examine the `Faulty Generated Code` provided. This is your previous attempt at generating or fixing the code.
- **Identify Root Cause of Failure**: Based on the `Compilation/Runtime Errors` and `Validation Feedback`, pinpoint exactly *why* your previous code failed. What specific lines or logic were incorrect?
- **Avoid Repetition**: You **MUST NOT** reintroduce the same errors or logical flaws that were present in the `Faulty Generated Code`. Ensure your new code directly addresses and rectifies those specific issues.

**5. Adhere to Motion Canvas v3.17.2 API (NO HTML/CSS HALLUCINATIONS):**
   - **VALID PROPERTIES ONLY**:
     - For Shapes (`Rect`, `Circle`): Use `fill`, `stroke`, `lineWidth`, `size`.
     - For Text (`Txt`): Use `fill` (for color), `fontSize`, `fontFamily`, `fontWeight`.
     - For Lines (`Line`): Use `points`, `stroke`, `lineWidth`, `start`, `end`.
   - **UNSUPPORTED PROPERTIES**: The following are **NOT** valid in v3.17.29 and must be removed or replaced: `strokeDasharray`, `strokeDashOffset`, `lineDash`, `lineDashOffset`. Animate the `start` and `end` properties of a `<Line />` or `<Path />` instead.
   - **TRANSPARENCY**: To make a `fill` or `stroke` transparent, set it to `null`, not the string `"transparent"`.
   - **`view.add()`**: This method only takes **one** argument. To add multiple nodes, wrap them in an array: `view.add([rectRef, circleRef]);`.
   - **REFS**: Refs are functions. Call them directly: `myRef().position(100, 1)`. **NEVER** use `myRef.current`.

### OUTPUT INSTRUCTIONS
- Generate **ONLY** the corrected, raw TypeScript code.
- Do not include any explanations, comments, or markdown fences in your output.
- The final code must be ready to compile and run without any errors.
"""

class CodeGeneratorAgent:
    def __init__(self):
        self.max_retry_attempts = 6
        self.generated_scenes = {}
        self.processed_scene_names = []
        self._is_first_save = True
        self.context_examples_cache = {}  # Cache for loaded example files

        # CONSISTENCY MANAGEMENT SYSTEM
        self.scene_consistency_data = {
            'colors_used': set(),
            'character_positions': {},
            'visual_elements': {},
            'text_styles': {},
            'animation_patterns': [],
            'coordinate_ranges': {'x_min': -960, 'x_max': 960, 'y_min': -540, 'y_max': 540},
            'previous_scene_summary': ""
        }
        self.previous_scene_code = None
        self.scene_transitions = {}
        
    def _log_prompt_to_file(self, prompt: str, scene_name: str, attempt: int, prompt_type: str, 
                        scene_data: Dict = None, errors: List[str] = None, 
                        validation_feedback: Dict = None, generated_code: str = None):
        """
        Log the exact prompt sent to Gemini for debugging purposes.
        
        Args:
            prompt: The actual prompt string sent to Gemini
            scene_name: Name of the scene being generated
            attempt: Attempt number (1-indexed)
            prompt_type: Either "initial_generation" or "error_correction"
            scene_data: The scene data dict (optional)
            errors: List of errors from previous attempt (optional)
            validation_feedback: Validation feedback dict (optional)
            generated_code: The code that Gemini generated (optional, for logging response)
        """
        try:
            # Create timestamp for unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create scene-specific directory
            scene_log_dir = os.path.join(PROMPT_LOGS_DIR, scene_name.lower())
            os.makedirs(scene_log_dir, exist_ok=True)
            
            # Create filename with attempt number and type
            log_filename = f"attempt_{attempt:02d}_{prompt_type}_{timestamp}.md"
            log_path = os.path.join(scene_log_dir, log_filename)
            
            # Build the log content
            log_content = f"""# Prompt Log for {scene_name}
    ## Attempt: {attempt}
    ## Type: {prompt_type}
    ## Timestamp: {timestamp}

    ---

    ## 1. PROMPT SENT TO GEMINI

    {prompt}

    text

    ---

    ## 2. CONTEXT INFORMATION

    ### Scene Data:
    {json.dumps(scene_data, indent=2) if scene_data else "N/A"}

    text

    ### Errors from Previous Attempt:
    {chr(10).join(errors) if errors else "N/A"}

    text

    ### Validation Feedback:
    {json.dumps(validation_feedback, indent=2) if validation_feedback else "N/A"}

    text

    ---

    ## 3. GENERATED CODE (Response from Gemini)

    {generated_code if generated_code else "Not yet generated"}

    text

    ---

    ## 4. METADATA

    - Scene: {scene_name}
    - Attempt: {attempt}
    - Prompt Type: {prompt_type}
    - Timestamp: {timestamp}
    - Prompt Length: {len(prompt)} characters
    - Scene Data Present: {bool(scene_data)}
    - Errors Present: {bool(errors and len(errors) > 0)}
    - Validation Feedback Present: {bool(validation_feedback)}

    """
            
            # Write to file
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            print(f"📝 Prompt logged to: {log_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to log prompt: {e}")

    def validate_typescript_compilation(self, scene_name: str) -> Tuple[bool, List[str]]:
        """CRITICAL: TypeScript Compilation Validation

        Validates that the generated TypeScript code compiles without errors.
        This MUST pass before attempting video generation.

        Returns:
            - bool: True if compilation succeeds, False if errors found
            - List[str]: List of compilation error messages
        """

        # Ensure scene name is lowercase to match file naming convention
        scene_file_name = scene_name.lower()
        scene_file = os.path.join(SCENES_DIR, f"{scene_file_name}.tsx")

        if not os.path.exists(scene_file):
            return False, [f"Scene file not found: {scene_file}"]

        print(f"🔍 TYPESCRIPT VALIDATION: Checking {scene_file_name}.tsx for compilation errors...")

        try:
            # Change to project root directory (where tsconfig.json and check-types.js are located)
            original_cwd = os.getcwd()
            os.chdir(PROJECT_ROOT)

            # Use our custom type checking script that handles Motion Canvas configuration properly
            relative_scene_path = f"src/scenes/{scene_file_name}.tsx"
            result = subprocess.run(
                ["node", "check-types.js", relative_scene_path],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )

            os.chdir(original_cwd)

            if result.returncode == 0:
                print(f"✅ TYPESCRIPT VALIDATION: {scene_file_name}.tsx compiles successfully!")
                return True, []
            else:
                # Parse TypeScript errors
                error_output = result.stderr.strip()
                if not error_output:
                    error_output = result.stdout.strip()

                # Split errors into individual lines and clean them up
                error_lines = [line.strip() for line in error_output.split('\n') if line.strip()]

                # Filter out summary lines and keep actual errors
                filtered_errors = []
                for line in error_lines:
                    if line.startswith("Found") and "error" in line:
                        continue  # Skip summary lines
                    if line and not line.startswith("Command exited"):
                        filtered_errors.append(line)

                print(f"❌ TYPESCRIPT VALIDATION: Found {len(filtered_errors)} compilation errors in {scene_file_name}.tsx")
                for i, error in enumerate(filtered_errors[:10], 1):  # Show first 10 errors
                    print(f"   {i}. {error}")
                if len(filtered_errors) > 10:
                    print(f"   ... and {len(filtered_errors) - 10} more errors")

                return False, filtered_errors

        except subprocess.TimeoutExpired:
            error = "TypeScript compilation timed out after 30 seconds"
            print(f"❌ TYPESCRIPT VALIDATION: {error}")
            return False, [error]
        except FileNotFoundError:
            error = "TypeScript compiler (tsc) not found. Please ensure Node.js and TypeScript are installed."
            print(f"❌ TYPESCRIPT VALIDATION: {error}")
            return False, [error]
        except Exception as e:
            error = f"Unexpected error during TypeScript validation: {str(e)}"
            print(f"❌ TYPESCRIPT VALIDATION: {error}")
            return False, [error]

    def _load_example_files(self, selected_data: dict) -> str:
        """
        Given a dict with:
        - 'selected_files': List[str] of filenames (including extension)
        - 'examples': Dict[str, dict] mapping filenames to info dicts containing 'content'
        Return a single string where each selected file is represented as:

        <basename>
        <code content>

        for each file in the order of selected_files.
        """
        if not selected_data or not selected_data.get('selected_files'):
            return "No reference examples available."

        selected_files = selected_data['selected_files']
        examples_data = selected_data.get('examples', {})
        formatted_parts = []

        for filename in selected_files:
            # Derive base name without extension
            base = filename.rsplit('.', 1)[0]
            info = examples_data.get(filename, {})
            content = info.get('content')

            if content:
                # Append "<basename>\n<code>" block
                formatted_parts.append(f"{base}\n{content}")
            else:
                # Fallback message if content is missing
                formatted_parts.append(f"{base}\n-- No content found --")

        # Join each block with two newlines for readability
        return "\n\n".join(formatted_parts)



    def _extract_consistency_info(self, scene_code: str, scene_data: Dict) -> None:
        """
        Extract visual consistency information from generated scene code.
        This builds up a knowledge base for maintaining consistency across scenes.
        """
        if not scene_code:
            return

        # Extract colors used
        import re
        color_patterns = [
            r'fill\s*[:=]\s*[\'"]([#\w]+)[\'"]',
            r'stroke\s*[:=]\s*[\'"]([#\w]+)[\'"]',
            r'color\s*[:=]\s*[\'"]([#\w]+)[\'"]',
        ]

        for pattern in color_patterns:
            matches = re.findall(pattern, scene_code, re.IGNORECASE)
            for match in matches:
                self.scene_consistency_data['colors_used'].add(match)

        # Extract positioning patterns
        position_patterns = [
            r"x\s*[:=]\s*([-\d.]+)",
            r"y\s*[:=]\s*([-\d.]+)",
            r"position\s*[:=]\s*\[([-\d.,\s]+)\]"
        ]

        positions = []
        for pattern in position_patterns:
            matches = re.findall(pattern, scene_code)
            positions.extend(matches)

        # Extract visual elements created
        element_patterns = [
            r"<(\w+)",  # JSX elements like <Rect, <Circle, etc.
            r"createRef<(\w+)>",  # TypeScript refs
        ]

        elements = set()
        for pattern in element_patterns:
            matches = re.findall(pattern, scene_code, re.IGNORECASE)
            elements.update(matches)

        self.scene_consistency_data['visual_elements'][len(self.generated_scenes)] = {
            'elements': list(elements),
            'positions': positions,
            'scene_title': scene_data.get('scene_title', ''),
            'transitions': scene_data.get('transitions', [])
        }

        # Store previous scene summary for next scene
        self.scene_consistency_data['previous_scene_summary'] = f"""
            Scene: {scene_data.get('scene_title', 'Unknown')}
            Elements: {', '.join(elements)}
            Colors: {', '.join(list(self.scene_consistency_data['colors_used'])[-3:])}
            Transitions: {scene_data.get('transitions', [])}
            """

    def _build_consistency_prompt_section(self) -> str:
        """
        Build a prompt section with consistency information for the next scene.
        """
        if not self.scene_consistency_data['colors_used'] and not self.previous_scene_code:
            return ""

        consistency_prompt = "\n**CONSISTENCY REQUIREMENTS:**\n"

        # Color consistency
        if self.scene_consistency_data['colors_used']:
            colors_list = ', '.join(list(self.scene_consistency_data['colors_used']))
            consistency_prompt += f"- Use established colors: {colors_list}\n"

        # Previous scene context
        if self.scene_consistency_data['previous_scene_summary']:
            consistency_prompt += f"- Previous scene context: {self.scene_consistency_data['previous_scene_summary']}\n"

        # Visual consistency
        if self.scene_consistency_data['visual_elements']:
            last_scene = max(self.scene_consistency_data['visual_elements'].keys())
            last_elements = self.scene_consistency_data['visual_elements'][last_scene]
            consistency_prompt += f"- Consider transitions from previous elements: {last_elements.get('elements', [])}\n"

        # Previous code reference
        if self.previous_scene_code:
            consistency_prompt += f"\n**PREVIOUS SCENE CODE (for reference):**\n```typescript\n{self.previous_scene_code}...\n```\n"

        return consistency_prompt

    def generate_code_from_json(self, scene_data: Dict, errors: Optional[List[str]] = None,
                            validation_feedback: Optional[Dict] = None,
                            selected_examples: Optional[List[str]] = None, token_tracker = None,
                            attempt_number: int = 1) -> str:  # Added attempt_number parameter
        """
        Enhanced code generation with context examples, error handling, and scene consistency.
        """
        scene_title = scene_data.get('scene_title', 'Untitled')
        scene_name = re.sub(r'[^a-zA-Z0-9_]', '_', scene_title).lower()  # Sanitize for filename
        print(f"  -> Generating code for scene: {scene_title}")
        
        reference_examples = self._load_example_files(selected_examples or [])
        
        if reference_examples:
            print(f"  -> Using {len(reference_examples)} reference examples")
        else:
            print("  -> No reference examples found")
        
        # BUILD CONSISTENCY INFORMATION
        consistency_section = self._build_consistency_prompt_section()
        
        if errors or validation_feedback:
            return self._generate_fixed_code(scene_data, errors or [],
                                            validation_feedback or {}, reference_examples, 
                                            consistency_section, token_tracker, attempt_number)
        
        enhanced_prompt = f"""
    {CODE_GENERATION_PROMPT}

    Generate TypeScript code for this scene data:
    {json.dumps(scene_data, indent=2)}

    **REFERENCE EXAMPLES (use as patterns - first 2 only):**
    {reference_examples[:5000]}

    Generate complete, compilable Motion Canvas TypeScript code that follows ALL layout requirements above.
    """
        
        if selected_examples:
            print(f"  -> Using {len(selected_examples)} reference examples + consistency info")
        else:
            print(f"  -> Using base prompt + consistency info")
        
        try:
            if not GENAI_AVAILABLE:
                return "// Error: Google Generative AI not available", ""
            
            # **NEW: Log prompt before sending to Gemini**
            self._log_prompt_to_file(
                prompt=enhanced_prompt,
                scene_name=scene_name,
                attempt=attempt_number,
                prompt_type="initial_generation",
                scene_data=scene_data
            )
            
            response = model.generate_content(enhanced_prompt)
            
            # Track token usage if token_tracker is provided
            if token_tracker:
                try:
                    input_tokens = response.usage_metadata.prompt_token_count
                    output_tokens = response.usage_metadata.candidates_token_count
                    scene_title = scene_data.get('scene_title', 'UnknownScene')
                    token_tracker.add("CodeGenerator", scene_title, input_tokens, output_tokens)
                except AttributeError:
                    pass
            
            generated_code = self._clean_code_response(response.text)
            
            # **NEW: Log generated code**
            self._log_prompt_to_file(
                prompt=enhanced_prompt,
                scene_name=scene_name,
                attempt=attempt_number,
                prompt_type="initial_generation_response",
                scene_data=scene_data,
                generated_code=generated_code
            )
            
            # EXTRACT CONSISTENCY INFO FROM GENERATED CODE
            self._extract_consistency_info(generated_code, scene_data)
            self.previous_scene_code = generated_code
            
            return generated_code, enhanced_prompt
            
        except Exception as e:
            print(f"  -> Error during code generation: {e}")
            return f"// Error generating code: {e}", ""

    def _generate_fixed_code(self, scene_data: Dict, errors: List[str],
                            validation_feedback: Dict, reference_examples: str, 
                            consistency_section: str = "", token_tracker = None,
                            attempt_number: int = 1) -> str:  # Added attempt_number
        """Generate fixed code based on errors, validation feedback, context examples, and consistency info."""
        
        scene_title = scene_data.get('scene_title', 'Untitled')
        scene_name = re.sub(r'[^a-zA-Z0-9_]', '_', scene_title).lower()
        
        original_code = self.generated_scenes.get(scene_data.get('scene_title', ''), "// No original code available")
        
        # Handle structured validation feedback
        if isinstance(validation_feedback, dict):
            feedback_text = self._format_structured_feedback(validation_feedback)
            # Use corrected scene description if provided
            if validation_feedback.get('corrected_scene_description'):
                scene_data = scene_data.copy()
                scene_data['scene_description'] = validation_feedback['corrected_scene_description']
        else:
            feedback_text = str(validation_feedback) if validation_feedback else ""
        
        prompt = ERROR_ANALYSIS_PROMPT.format(
            scene_data=json.dumps(scene_data, indent=2),
            code=original_code,
            errors="\n".join(errors),
            validation_feedback=feedback_text,
            reference_examples=reference_examples
        ) + consistency_section  # Add consistency information
        
        try:
            if not GENAI_AVAILABLE:
                return "// Error: Google Generative AI not available", ""
            
            # **NEW: Log error correction prompt before sending**
            self._log_prompt_to_file(
                prompt=prompt,
                scene_name=scene_name,
                attempt=attempt_number,
                prompt_type="error_correction",
                scene_data=scene_data,
                errors=errors,
                validation_feedback=validation_feedback
            )
            
            response = model.generate_content(prompt)
            
            # Track token usage if token_tracker is provided
            if token_tracker:
                try:
                    input_tokens = response.usage_metadata.prompt_token_count
                    output_tokens = response.usage_metadata.candidates_token_count
                    scene_title = scene_data.get('scene_title', 'UnknownScene')
                    token_tracker.add("CodeGenerator", scene_title, input_tokens, output_tokens)
                except AttributeError:
                    pass
            
            fixed_code = self._clean_code_response(response.text)
            
            # **NEW: Log the corrected code response**
            self._log_prompt_to_file(
                prompt=prompt,
                scene_name=scene_name,
                attempt=attempt_number,
                prompt_type="error_correction_response",
                scene_data=scene_data,
                errors=errors,
                validation_feedback=validation_feedback,
                generated_code=fixed_code
            )
            
            # EXTRACT CONSISTENCY INFO FROM FIXED CODE
            self._extract_consistency_info(fixed_code, scene_data)
            self.previous_scene_code = fixed_code
            
            return fixed_code, prompt
            
        except Exception as e:
            print(f"  -> Error during fixed code generation: {e}")
            return f"// Error generating fixed code: {e}", ""


    def _format_structured_feedback(self, feedback: Dict) -> str:
        """Format structured feedback into readable text for the prompt."""
        if not feedback or feedback.get('valid', True):
            return "No issues found."

        formatted = "VALIDATION ISSUES FOUND:\n"

        for issue in feedback.get('issues', []):
            formatted += f"- {issue['type'].upper()}: {issue['description']}\n"
            formatted += f"  Fix suggestion: {issue['fix_suggestion']}\n"

        if feedback.get('code_improvement_hints'):
            formatted += "\nCODE IMPROVEMENT HINTS:\n"
            for hint in feedback['code_improvement_hints']:
                formatted += f"- {hint}\n"

        return formatted

    def _clean_code_response(self, response_text: str) -> str:
        """Clean and validate the code response from the AI."""
        code = response_text.strip()
        if code.startswith("```typescript") or code.startswith("```ts"):
            lines = code.split('\n')
            code = '\n'.join(lines[1:])
        if code.endswith("```"):
            code = code[:-3].strip()
        return code

    def update_project_file(self, scene_names) -> bool:
        """
        Updates the project file to include the specified scenes.
        Can handle both a single scene name (str) or a list of scene names (List[str]).
        Appends new scenes to existing ones instead of overwriting.
        """
        # Handle both single scene name and list of scene names
        if isinstance(scene_names, str):
            scene_names = [scene_names]

        print(f"  -> Updating project file with scenes: {', '.join(scene_names)}")
        try:
            if not os.path.exists(PROJECT_FILE):
                self._create_default_project_file()

            with open(PROJECT_FILE, 'r',encoding='utf-8') as f:
                content = f.read()

            # Normalize scene names to strip `.tsx` if already present
            new_scenes = [name.replace(".tsx", "") for name in scene_names]

            # Only include the new scene(s) in the project file
            all_scenes = new_scenes

            # Generate import lines for all scenes
            imports = "\n".join(
                [f"import {name} from './scenes/{name}.tsx?scene';" for name in all_scenes]
            )

            # Build the scene list string properly (comma-separated, no weird spacing)
            scene_list_str = ", ".join(all_scenes)

            # Insert AUTOMATED markers if missing
            if "// --- AUTOMATED SCENES START ---" not in content:
                content = content.replace(
                    "import {makeProject} from '@motion-canvas/core';",
                    "import {makeProject} from '@motion-canvas/core';\n\n"
                    "// --- AUTOMATED SCENES START ---\n"
                    "// --- AUTOMATED SCENES END ---"
                )

            # Replace everything between markers with all scenes (existing + new)
            content = re.sub(
                r"// --- AUTOMATED SCENES START ---.*?// --- AUTOMATED SCENES END ---",
                f"// --- AUTOMATED SCENES START ---\n{imports}\n\n// --- AUTOMATED SCENES END ---",
                content,
                flags=re.DOTALL
            )

            # Fix the scenes list properly with all scenes
            content = re.sub(
                r"(scenes\s*:\s*\[)[^\]]*(\])",
                r"\1" + scene_list_str + r"\2",
                content,
                flags=re.DOTALL
            )

            with open(PROJECT_FILE, 'w',encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Project file updated. Current scenes: {scene_list_str}")
            return True

        except Exception as e:
            print(f"❌ ERROR: Could not update project file: {e}")
            return False

    def _create_default_project_file(self):
        """Create a default project.ts file if it doesn't exist."""
        default_content = """
import {makeProject} from '@motion-canvas/core';

// --- AUTOMATED SCENES START ---
// --- AUTOMATED SCENES END ---

export default makeProject({
  scenes: [],
});
"""
        os.makedirs(os.path.dirname(PROJECT_FILE), exist_ok=True)
        with open(PROJECT_FILE, 'w',encoding='utf-8') as f:
            f.write(default_content)

    def save_scene_code(self, scene_name: str, code: str, scene_data: Dict) -> bool:
        """
        Save the generated code. On the first call in a script execution,
        it will first wipe all existing .tsx files from the scenes directory.
        """
        if self._is_first_save:
            print(f"--- First scene save of this run, preparing clean slate ---")
            try:
                if os.path.isdir(SCENES_DIR):
                    print(f"  -> Deleting old .tsx files from {SCENES_DIR}...")
                    files_removed = 0
                    for filename in os.listdir(SCENES_DIR):
                        if filename.endswith(".tsx"):
                            os.remove(os.path.join(SCENES_DIR, filename))
                            files_removed += 1
                    print(f"  -> Removed {files_removed} old scene file(s).")
                print(f"  -> Resetting project file {PROJECT_FILE}...")
                self._create_default_project_file()
            except Exception as e:
                print(f"❌ ERROR during initial cleanup: {e}")
                return False
            finally:
                self._is_first_save = False

        try:
            file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}.tsx")
            os.makedirs(SCENES_DIR, exist_ok=True)
            with open(file_path, 'w',encoding='utf-8') as f:
                f.write(code)
            self.generated_scenes[scene_data.get('scene_title', scene_name)] = code
            print(f"✅ Code for {scene_name} saved to {file_path}")

            # Automatically update project.ts with the new scene
            if self.update_project_file(scene_name.lower()):
                print(f"✅ Project file updated with {scene_name}")
            else:
                print(f"⚠️ Warning: Could not update project file for {scene_name}")

            return True
        except Exception as e:
            print(f"❌ Error saving scene code: {e}")
            return False

    def _log_subprocess_output(self, process, scene_name):
        stdout, stderr = process.communicate()
        if stdout:
            print(f"--- STDOUT from {scene_name} renderer ---")
            print(stdout)
            print("------------------------------------------")
        if stderr:
            print(f"--- STDERR from {scene_name} renderer ---")
            print(stderr)
            print("------------------------------------------")

    def render_scene(self, scene_name: str) -> Tuple[Optional[List[str]], Optional[str]]:
            """
            Renders a single scene using the browser renderer which creates videos directly.
            """
            # Ensure the scene name is capitalized correctly
            cli_scene_name = scene_name[0].upper() + scene_name[1:]
            video_path = os.path.join(OUTPUT_DIR, f"{scene_name.lower()}.mp4")
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            try:
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

                print(f" 🎬 -> Starting video generation for {cli_scene_name}...")

                # Remove old video file if it exists
                if os.path.exists(video_path):
                    os.remove(video_path)
                    print(f"🗑️ Removed old video: {video_path}")

                # Use browser renderer that generates video directly
                renderer_path = os.path.join(os.path.dirname(__file__), 'simple_browser_renderer.js')
                render_command = ["node", renderer_path, cli_scene_name]

                print(f"🚀 Starting video generation: {' '.join(render_command)}")

                # FIXED APPROACH: Simple detection with proper process handling
                import time

                # Start the browser renderer process, capturing stdout and stderr for debugging
                process = subprocess.Popen(render_command, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

                print(f"⏳ Waiting for video file: {video_path}")
                start_time = time.time()
                timeout = 300  # 2 minutes should be plenty

                video_found = False

                while time.time() - start_time < timeout:
                    # Primary check: Does the video file exist and have content?
                    if os.path.exists(video_path):
                        try:
                            file_size = os.path.getsize(video_path)
                            if file_size > 10000:  # At least 10KB means it's a real video
                                print(f"✅ Video file detected: {video_path} ({file_size / (1024*1024):.1f}MB)")
                                video_found = True
                                break
                        except Exception as e:
                            print(f"Warning: Error checking file size: {e}")

                    # Secondary check: Has the process finished?
                    if process.poll() is not None:
                        if process.returncode == 0:
                            # Process finished successfully - wait a moment for file system
                            print("🔄 Renderer process completed, checking for video file...")
                            time.sleep(5)  # Give filesystem time to sync

                            # Final check for video file
                            if os.path.exists(video_path):
                                try:
                                    file_size = os.path.getsize(video_path)
                                    if file_size > 10000:
                                        print(f"✅ Video file ready: {video_path} ({file_size / (1024*1024):.1f}MB)")
                                        video_found = True
                                        break
                                    else:
                                        print(f"⚠️ Video file too small: {file_size} bytes")
                                except Exception as e:
                                    print(f"Error checking final video file: {e}")

                            # If still no video after process completion, wait a bit longer
                            print("⏳ Process completed but no video yet, waiting a bit more...")
                            time.sleep(10)

                            # One more check
                            if os.path.exists(video_path) and os.path.getsize(video_path) > 10000:
                                print(f"✅ Video file found after delay: {video_path}")
                                video_found = True
                                break
                            else:
                                print("❌ Process completed but no valid video file found")
                                break
                        else:
                            error_message = f"❌ Browser renderer failed for {scene_name} (exit code: {process.returncode})"
                            print(error_message)
                            self._log_subprocess_output(process, scene_name)
                            return [error_message], None

                    # Wait and show progress
                    time.sleep(3)
                    elapsed = int(time.time() - start_time)
                    if elapsed % 15 == 0 and elapsed > 0:
                        print(f"⏳ Still waiting for video... ({elapsed}s elapsed)")

                # Clean up process if still running
                if process.poll() is None:
                    print("🛑 Terminating renderer process...")
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()

                # Final validation
                if not video_found:
                    # Last-ditch effort: check if video exists now
                    if os.path.exists(video_path) and os.path.getsize(video_path) > 10000:
                        print(f"✅ Video file found in final check: {video_path}")
                        video_found = True
                    else:
                        error_message = f"❌ Video generation failed for {scene_name} - no valid video file created"
                        print(error_message)
                        self._log_subprocess_output(process, scene_name)
                        return [error_message], None

                print("✅ Video generation completed successfully!")            # Final check - ensure video file exists and is valid
                if not os.path.exists(video_path):
                    error_message = f"❌ Video file not created at {video_path}"
                    print(error_message)
                    print(f"📁 Looking for files in output directory:")
                    try:
                        output_files = os.listdir(OUTPUT_DIR)
                        for f in output_files:
                            if f.endswith('.mp4'):
                                print(f"   📹 Found: {f}")
                    except:
                        pass
                    return [error_message], None

                # Check video file size for validation
                file_size = os.path.getsize(video_path)
                print(f"   📊 Generated video size: {file_size / (1024*1024):.1f}MB")

                print(f"🎥 Video available at: {video_path}")
                return None, video_path  # Return video path

            except Exception as e:
                error_message = f"❌ ERROR rendering {scene_name}: {str(e)}"
                print(error_message)
                return [error_message], None

    def process_scene_with_retry(self, scene_data: Dict, scene_name: str,
                               validation_agent=None, selected_examples: Optional[List[str]] = None,
                               feedback: Optional[Dict] = None, token_tracker = None) -> Tuple[bool, Optional[str], Optional[List[str]], Optional[Dict]]:
        self.validation_agent = validation_agent
        """
        ENHANCED: Process a scene with TypeScript compilation validation BEFORE video generation.

        This ensures we never attempt to render videos with broken TypeScript code.
        The process now includes:
        1. Code generation
        2. TypeScript compilation validation
        3. Video rendering (only if TypeScript compiles)
        4. Video validation (optional)
        """
        errors = []
        validation_feedback = feedback
        previous_code = None

        for attempt in range(self.max_retry_attempts):
            print(f"\n--- 🎬 Attempt {attempt + 1}/{self.max_retry_attempts} for {scene_name} ---")
            
            # STEP 1: Generate TypeScript Code
            code, formatted_code_gen_prompt = self.generate_code_from_json(
                scene_data, errors, validation_feedback, selected_examples, token_tracker,
                attempt_number=attempt + 1  # Pass attempt number for logging
            )

            if code.startswith("// Error"):
                print(f"❌ Could not generate code for {scene_name} on attempt {attempt + 1}")
                continue

            # STEP 2: Save the generated code
            if not self.save_scene_code(scene_name, code, scene_data):
                print(f"❌ Could not save code for {scene_name} on attempt {attempt + 1}")
                continue


            # STEP 3: CRITICAL - TypeScript Compilation Validation
            print(f"\n🔍 STEP 3: TypeScript Compilation Validation")
            compilation_success, compilation_errors = self.validate_typescript_compilation(scene_name)

            if not compilation_success:
                print(f"❌ TYPESCRIPT COMPILATION FAILED on attempt {attempt + 1}")
                print(f"   Found {len(compilation_errors)} compilation errors")

                # Feed compilation errors back to the code generator for the next attempt
                errors = [
                    f"TypeScript Compilation Error {i+1}: {error}"
                    for i, error in enumerate(compilation_errors[:15])  # Limit to first 15 errors
                ]

                # Add a summary message explaining the issue
                errors.insert(0,
                    f"CRITICAL: The generated TypeScript code does not compile. "
                    f"Found {len(compilation_errors)} compilation errors. "
                    f"You MUST fix these syntax/type errors before proceeding:"
                )

                previous_code = code
                continue  # Retry with compilation errors as feedback

            print(f"✅ TYPESCRIPT COMPILATION: {scene_name}.tsx compiles successfully!")

            # STEP 3.5: Generate SSML from the compiled TypeScript scene
            print(f"\n📝 STEP 3.5: Generating SSML from TypeScript scene")
            scene_file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}.tsx")
            ssml_file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}.ssml")

            ssml_success = self.generate_ssml_file(scene_file_path, ssml_file_path)
            if not ssml_success:
                print(f"⚠️ SSML generation failed, but continuing with video generation...")

            # STEP 4: Update project file and render video (only after successful compilation)
            print(f"\n🎬 STEP 4: Video Generation (TypeScript validation passed)")

            # Render scene and generate video
            render_errors, video_path = self.render_scene(scene_name)
            if render_errors:
                print(f"❌ VIDEO RENDERING FAILED on attempt {attempt + 1}")
                errors = render_errors
                previous_code = code
                continue

            # STEP 5: Video Validation (optional, only if validation agent provided)
            if validation_agent and video_path:
                print(f"\n🔍 STEP 5: Video Content Validation")
                print(f"   Running validation for {scene_name}...")

                # Get code examples for validation
                code_examples = ""
                if selected_examples:
                    try:
                        examples_text = []
                        for example_file in selected_examples:
                            example_path = os.path.join(EXAMPLES_DIR, example_file)
                            if os.path.exists(example_path):
                                with open(example_path, 'r') as f:
                                    examples_text.append(f"// {example_file}\n{f.read()}")
                        code_examples = "\n\n".join(examples_text)
                    except Exception as e:
                        print(f"⚠️ Could not load code examples: {e}")

                # Call validation with all required inputs as per professor's spec
                validation_result = self.validation_agent.validate_scene( # Changed from validate_scene to validate_video
                    scene_data=scene_data,
                    video_path=video_path,
                    generated_code=code,
                    errors=errors if errors else [],
                    code_examples=code_examples,
                    formatted_code_gen_prompt=formatted_code_gen_prompt, # Pass the formatted prompt
                    token_tracker=token_tracker
                )

                is_valid, feedback = validation_result

                if is_valid:
                    print(f"✅ Scene {scene_name} validated successfully!")
                    print(f"📹 Video available at: {video_path}")
                    return True, video_path, None, None
                else:
                    print(f"❌ Validation failed on attempt {attempt + 1}")

                    # Handle structured feedback
                    if isinstance(feedback, dict):
                        print("Issues found:")
                        for issue in feedback.get('issues', []):
                            print(f"   - {issue['description']}")
                        validation_feedback = feedback
                    else:
                        # Legacy string feedback
                        validation_feedback = {"valid": False, "issues": [{"type": "general", "description": str(feedback), "fix_suggestion": "Review and fix the identified issues"}]}

                    print(f"--- Feedback from Validation Agent (Attempt {attempt + 1}) ---")
                    import json
                    print(json.dumps(validation_feedback, indent=2))
                    print("---------------------------------------------------")

                    previous_code = code
                    # Reset errors for next iteration since we're using structured feedback now
                    errors = []
                    continue

            # STEP 4.5: After video is generated, run SSML-to-audio and stitch audio/video for sync
            print(f"\n🔊 STEP 4.5: Generating audio from SSML and stitching with video for sync")
            ssml_file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}.ssml")
            audio_file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}.wav")
            timing_file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}_timing.json")

            # Regenerate SSML if it doesn't exist (in case STEP 3.5 failed)
            if not os.path.exists(ssml_file_path):
                print(f"  -> SSML file missing, regenerating...")
                scene_file_path = os.path.join(SCENES_DIR, f"{scene_name.lower()}.tsx")
                self.generate_ssml_file(scene_file_path, ssml_file_path)

            if os.path.exists(ssml_file_path):
                # Generate audio from SSML
                audio_success = self.run_ssml_to_audio(ssml_file_path, audio_file_path)

                if audio_success and os.path.exists(audio_file_path):
                    # Stitch audio with video
                    stitched_video_path = os.path.join(OUTPUT_DIR, f"{scene_name.lower()}_final.mp4")
                    stitch_success = self.stitch_audio_video(video_path, audio_file_path, stitched_video_path, timing_file_path)

                    if stitch_success:
                        print(f"✅ Final video with synced audio saved to: {stitched_video_path}")
                        video_path = stitched_video_path  # Update video_path to the final version
                    else:
                        print(f"⚠️ Audio stitching failed, using video without audio sync")
                else:
                    print(f"⚠️ Audio generation failed, using video without audio sync")
            else:
                print(f"⚠️ SSML file not found at {ssml_file_path}, skipping audio generation")

            print(f"✅ Scene {scene_name} processed successfully!")
            print(f"📹 Video available at: {video_path}")
            return True, video_path, None, None

        print(f"❌ FAILED to process {scene_name} after {self.max_retry_attempts} attempts")
        print(f"CRITICAL: No error-free video could be generated for {scene_name}")
        print(f"   Possible issues:")
        print(f"   - TypeScript compilation errors (most common)")
        print(f"   - Motion Canvas syntax errors")
        print(f"   - Video rendering failures")
        print(f"   - Video validation failures")
        print(f"📋 Final error summary: {len(errors) if errors else 0} errors reported")

        return False, None, errors, validation_feedback

    def extract_embedded_json(self, code: str) -> dict:
        """Extract the embedded JSON data from the TypeScript code."""
        try:
            # Find the JSON data declaration (case-insensitive for various variable names)
            json_patterns = [
                r'const json_data = ({.*?});',
                r'const sceneData = ({.*?});',
                r'const SCENE_DATA = ({.*?});',
                r'const scene_data = ({.*?});',
            ]

            for pattern in json_patterns:
                match = re.search(pattern, code, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    # Parse the JSON data
                    return json.loads(json_str)

            print("  -> Warning: Could not find embedded JSON data in TypeScript code")
            return {}
        except Exception as e:
            print(f"  -> Error extracting embedded JSON: {e}")
            return {}

    def analyze_typescript_code(self, code: str) -> list:
        """
        Analyze the generated TypeScript code to extract actual text content from Txt components.
        """
        print("  -> Analyzing TypeScript code to extract text content...")

        extracted_texts = []

        # First, extract the embedded JSON data from the TypeScript code
        embedded_json = self.extract_embedded_json(code)

        # Pattern 1: Extract text from hardcoded strings: text="Some text" or text='Some text'
        hardcoded_pattern = r'<Txt[^>]*text=["\'](.*?)["\'][^>]*>'
        hardcoded_matches = re.finditer(hardcoded_pattern, code, re.DOTALL)
        for match in hardcoded_matches:
            text_content = match.group(1).strip()
            if text_content and len(text_content) > 1:
                extracted_texts.append({
                    'type': 'hardcoded',
                    'text': text_content,
                    'reference': 'direct_string',
                    'position_in_code': match.start()
                })

        # Pattern 2: Extract text from variable references: text={variable_name}
        variable_pattern = r'<Txt[^>]*text=\{([^}]+)\}[^>]*>'
        variable_matches = re.finditer(variable_pattern, code, re.DOTALL)
        for match in variable_matches:
            var_name = match.group(1).strip()

            # Find the variable definition
            var_definition_pattern = rf'const\s+{re.escape(var_name)}\s*=\s*(.+?);'
            var_match = re.search(var_definition_pattern, code, re.DOTALL)

            if var_match:
                var_value = var_match.group(1).strip()

                # Check if it's a direct string
                if (var_value.startswith('"') and var_value.endswith('"')) or \
                   (var_value.startswith("'") and var_value.endswith("'")):
                    # Remove quotes
                    text_content = var_value[1:-1]
                    extracted_texts.append({
                        'type': 'variable_string',
                        'text': text_content,
                        'reference': var_name,
                        'position_in_code': match.start()
                    })
                elif 'scene.scene_title' in var_value:
                    # Extract from embedded JSON using scene.scene_title
                    if embedded_json and 'scenes' in embedded_json:
                        for scene in embedded_json['scenes']:
                            if 'scene_title' in scene:
                                extracted_texts.append({
                                    'type': 'scene_title_ref',
                                    'text': scene['scene_title'],
                                    'reference': f"{var_name} -> scene.scene_title",
                                    'position_in_code': match.start()
                                })
                elif var_value.startswith('wrapText('):
                    # Extract text from wrapText function call
                    # Look for the fulltext variable
                    fulltext_match = re.search(r'(\w+)_fulltext', var_value)
                    if fulltext_match:
                        fulltext_var = fulltext_match.group(1) + '_fulltext'
                        fulltext_pattern = rf'const\s+{re.escape(fulltext_var)}\s*=\s*["\'](.*?)["\']'
                        fulltext_match = re.search(fulltext_pattern, code, re.DOTALL)
                        if fulltext_match:
                            text_content = fulltext_match.group(1)
                            extracted_texts.append({
                                'type': 'wrapped_text',
                                'text': text_content,
                                'reference': f"{var_name} -> {fulltext_var}",
                                'position_in_code': match.start()
                            })

        # Pattern 3: Extract text from animation calls like ref().text("content", duration)
        animation_pattern = r'\.text\(\s*([^,)]+)\s*,'
        animation_matches = re.finditer(animation_pattern, code, re.DOTALL)
        for match in animation_matches:
            animation_text = match.group(1).strip()

            # Remove quotes if present
            if (animation_text.startswith('"') and animation_text.endswith('"')) or \
               (animation_text.startswith("'") and animation_text.endswith("'")):
                text_content = animation_text[1:-1]
                if text_content and len(text_content) > 1:
                    extracted_texts.append({
                        'type': 'animation_text',
                        'text': text_content,
                        'reference': 'animation_call',
                        'position_in_code': match.start()
                    })
            elif animation_text.endswith('_fulltext'):
                # It's a reference to a fulltext variable
                fulltext_pattern = rf'const\s+{re.escape(animation_text)}\s*=\s*["\'](.*?)["\']'
                fulltext_match = re.search(fulltext_pattern, code, re.DOTALL)
                if fulltext_match:
                    text_content = fulltext_match.group(1)
                    extracted_texts.append({
                        'type': 'animation_fulltext_ref',
                        'text': text_content,
                        'reference': animation_text,
                        'position_in_code': match.start()
                    })

        # Sort by position in code to maintain order
        extracted_texts.sort(key=lambda x: x['position_in_code'])

        print(f"  -> Extracted {len(extracted_texts)} text elements from TypeScript code")
        for i, text_item in enumerate(extracted_texts):
            print(f"     {i+1}. {text_item['type']}: {text_item['text'][:50]}...")

        return extracted_texts

    def generate_ssml_file(self, scene_file_path: str, ssml_file_path: str) -> bool:
        """
        Generate SSML file from TypeScript scene file by extracting text content.
        """
        print(f"  -> Generating SSML from scene file: {scene_file_path}")

        try:
            # Read the TypeScript scene file
            with open(scene_file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()

            # Extract text elements
            extracted_texts = self.analyze_typescript_code(code_content)

            if not extracted_texts:
                print("  ❌ No text elements found to generate SSML")
                return False

            # Generate SSML content
            ssml_parts = []
            for text_item in extracted_texts:
                text = text_item['text'].strip()
                if text:
                    # Add emphasis based on text type
                    if text_item['type'] in ['scene_title_ref', 'hardcoded']:
                        ssml_parts.append(f'<p><emphasis level="strong">{text}</emphasis></p>')
                    else:
                        ssml_parts.append(f'<p><emphasis level="moderate">{text}</emphasis></p>')

                    # Add break between text elements
                    ssml_parts.append('<break time="500ms"/>')

            if not ssml_parts:
                print("  ❌ No valid text content found for SSML generation")
                return False

            # Create SSML document
            ssml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                           http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"
       xml:lang="en-US">
  <voice name="en-US-Neural2-F">
    <prosody rate="medium" pitch="medium">
{"".join(f"      {part}\n" for part in ssml_parts)}
    </prosody>
  </voice>
</speak>'''

            # Write SSML file
            with open(ssml_file_path, 'w', encoding='utf-8') as f:
                f.write(ssml_content)

            print(f"  ✅ SSML file generated successfully: {ssml_file_path}")
            print(f"     Contains {len([p for p in ssml_parts if not p.startswith('<break')])} text elements")
            return True

        except Exception as e:
            print(f"  ❌ Error generating SSML file: {e}")
            return False

    def run_ssml_to_audio(self, ssml_path: str, audio_path: str):
        """
        Convert SSML file to audio using Gemini TTS Preview API.
        """
        print(f"  -> Converting SSML to audio: {ssml_path} -> {audio_path}")

        try:
            # Import the conversion function
            import subprocess
            import sys
            import os

            # Get the path to the ssml_to_audio.py script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ssml_script = os.path.join(script_dir, 'ssml_to_audio.py')

            if not os.path.exists(ssml_script):
                print(f"  ❌ SSML to audio script not found: {ssml_script}")
                return False

            # Run the SSML to audio conversion
            cmd = [sys.executable, ssml_script, ssml_path, audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)

            # Check both return code and if file was actually created
            if result.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                print(f"  ✅ Audio generated successfully: {audio_path}")
                return True
            else:
                print(f"  ❌ SSML to audio conversion failed:")
                print(f"     Return code: {result.returncode}")
                print(f"     STDOUT: {result.stdout}")
                print(f"     STDERR: {result.stderr}")

                # Additional checks
                if not os.path.exists(audio_path):
                    print(f"     Audio file was not created: {audio_path}")
                elif os.path.getsize(audio_path) == 0:
                    print(f"     Audio file is empty: {audio_path}")

                return False

        except Exception as e:
            print(f"  ❌ Error running SSML to audio conversion: {e}")
            return False

    def stitch_audio_video(self, video_path: str, audio_path: str, output_path: str, timing_path: str = None):
        """
        Stitch audio and video together using FFmpeg.
        """
        print(f"  -> Stitching audio and video: {audio_path} + {video_path} -> {output_path}")

        try:
            import subprocess

            # FFmpeg command to combine video and audio
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output file
                '-i', video_path,  # Input video
                '-i', audio_path,  # Input audio
                '-c:v', 'copy',    # Copy video codec (no re-encoding)
                '-c:a', 'aac',     # Encode audio as AAC
                '-shortest',       # Finish when shortest input ends
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"  ✅ Video with audio stitched successfully: {output_path}")
                return True
            else:
                print(f"  ❌ FFmpeg stitching failed:")
                print(f"     STDOUT: {result.stdout}")
                print(f"     STDERR: {result.stderr}")
                return False

        except Exception as e:
            print(f"  ❌ Error stitching audio and video: {e}")
            return False

def main():
    # --- USER CONFIGURABLE ---
    # Change this path to the scene description JSON you want to process.
    scene_data_json_path = os.path.join(PROJECT_ROOT, "my-animation", "reports", "pulley_system_where_we_have_two_circles_that_act_as_pulley,_and_a_rope_attached_to_it,_and_they_show_the_pulley_system_concept_semantic_plan.json")
    # --- END USER CONFIGURABLE ---

    if not os.path.exists(scene_data_json_path):
        print(f"Error: Scene data file not found at {scene_data_json_path}")
        return

    with open(scene_data_json_path, 'r') as f:
        scene_data = json.load(f)

    # Extract scene name from the data, fallback to a default
    scene_name = scene_data.get("scene_title", "default_scene_name")
    # Sanitize scene_name to be a valid file name
    scene_name = re.sub(r'[^a-zA-Z0-9_]', '_', scene_name).lower()


    # Instantiate the agent
    agent = CodeGeneratorAgent()

    # Get relevant examples using the context agent if available
    selected_examples = None
    if CONTEXT_AGENT_AVAILABLE and get_relevant_examples:
        try:
            # The context agent expects a dictionary with 'scenes'
            context_query = {"scenes": [scene_data]}
            selected_examples = get_relevant_examples(context_query)
            print(f"Context agent found {len(selected_examples.get('selected_files', []))}" + " relevant examples.")
        except Exception as e:
            print(f"Warning: Could not get relevant examples from context agent: {e}")


    # Process the scene
    success, video_path, errors, validation_feedback = agent.process_scene_with_retry(
        scene_data=scene_data,
        scene_name=scene_name,
        selected_examples=selected_examples
    )

    if success:
        print(f"\n\n--- ✅ Successfully generated video! ---")
        print(f"Video saved at: {video_path}")
    else:
        print(f"\n\n--- ❌ Failed to generate video. ---")
        if errors:
            print("Final errors:")
            for error in errors:
                print(f"- {error}")
        if validation_feedback:
            print("Final validation feedback:")
            print(json.dumps(validation_feedback, indent=2))

if __name__ == "__main__":
    main()
