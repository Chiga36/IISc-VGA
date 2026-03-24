# Motion Canvas Agent: Automated Animation Pipeline

This project is a sophisticated, multi-agent system designed to automate the creation of high-quality, educational animations using the Motion Canvas framework. It takes a high-level topic as input and orchestrates a series of specialized AI agents to handle every step of the production process, from conceptualization and scriptwriting to code generation, validation, and final video rendering.

The pipeline is built on a foundation of advanced prompt engineering and a modular agent architecture, enabling it to generate complex, visually consistent, and narratively coherent animations with minimal human intervention. This `README.md` provides a comprehensive guide for developers looking to understand, use, and contribute to this project.

## Pipeline Workflow

The entire animation generation process is orchestrated by the `run_pipeline.py` script. It guides the user's topic through a series of specialized agents, each responsible for a specific task. The diagram below illustrates the complete workflow, including the critical feedback loop for self-correction.

The process unfolds in the following steps:

1.  **Initiation**: The user provides an educational topic to the `run_pipeline.py` script.
2.  **Scene Planning**: The `SceneDescriptorAgent` receives the topic and generates a detailed, multi-scene JSON "blueprint" that outlines the narrative and visual structure of the animation.
3.  **Contextual Asset Gathering**: For each scene in the blueprint, the `ContextAgent` analyzes the requirements and selects a set of relevant code examples from the `/examples` library. These examples serve as a technical reference for the next agent.
4.  **Code Generation**: The `CodeGeneratorAgent` takes both the scene blueprint and the selected code examples to write the actual TypeScript (`.tsx`) code for the animation scene.
5.  **Compilation and Rendering**: The generated TypeScript code is compiled to check for errors. If it's valid, the system renders the scene and produces an `.mp4` video file.
6.  **Quality Assurance**: The `ValidationAgent` inspects the rendered video, comparing it against the original scene blueprint and a strict set of quality criteria.
7.  **Feedback or Completion**:
    *   If the video passes validation, it is saved as the final output.
    *   If the video fails, the `ValidationAgent` generates a detailed feedback report. This report is sent back to the start of the pipeline to trigger a self-correction cycle, allowing the agents to refine the scene plan and regenerate the code to fix the identified issues.

## The Agents

The power of this pipeline lies in its modular, agent-based architecture. Each agent is a specialized Python script that performs a single, well-defined task. The agents communicate through structured data (primarily JSON), passing the results of their work to the next agent in the chain.

### 1. SceneDescriptorAgent: The Architect

-   **Script:** `scripts/scene_descriptor.py`
-   **Role:** To act as a "Motion Graphics Architect." This is the first and most critical agent in the pipeline. It takes the user's high-level topic and transforms it into a detailed, structured JSON "blueprint" for the entire animation. This blueprint dictates the narrative flow, scene-by-scene breakdown, visual elements, and timing for the entire video.

#### Prompt Analysis

The `SceneDescriptorAgent` uses a highly detailed prompt to instruct the AI model. The key components of this prompt are:

*   **Persona:** The prompt assigns the AI a clear role: a "WORLD-CLASS Motion Graphics Architect and Instruction Translator." This sets the context and expectation for high-quality, professional output.
*   **Core Purpose:** It explicitly tells the AI to break the topic into logically connected scenes, design for a continuous flow, and output a strictly formatted JSON array.
*   **Layout & Design Rules:** The prompt enforces a consistent visual structure by providing hard-coded rules, most importantly the **60/40 screen split** (40% for visuals on the left, 60% for text on the right). This rule is fundamental to the visual identity of all animations produced by the pipeline.
*   **JSON Schema:** It provides a complete JSON schema that the AI's output *must* conform to. This ensures the output is machine-readable and can be reliably parsed by the downstream agents.
*   **Principle of Continuity:** The prompt teaches the AI how to create smooth transitions between scenes by telling it to "keep," "modify," or "fadeOut" elements, ensuring a professional and non-jarring viewing experience.
*   **Feedback Mechanism:** The prompt includes a placeholder for feedback from the `ValidationAgent`. This allows the agent to learn from its mistakes and refine a scene plan if the initial version resulted in a failed validation.

This comprehensive prompt is the key to the agent's ability to generate high-quality, structured, and consistent scene plans.

<details>
<summary>Click to view the full prompt</summary>

```
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
{{JSON_SCHEMA}}

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
```

</details>

### 2. ContextAgent: The Librarian

-   **Script:** `scripts/context_agent.py`
-   **Role:** To act as an expert "Librarian" or "Framework Expert." This agent's job is to bridge the gap between the high-level scene plan and the low-level code generation. It analyzes the requirements of a single scene and selects a list of the most relevant code examples from the `examples` directory. These examples provide the `CodeGeneratorAgent` with a "cookbook" of proven patterns to follow.

#### Prompt Analysis

The `ContextAgent`'s prompt is a masterclass in providing the AI with the necessary context to make an informed decision.

*   **Persona:** It assigns the AI the role of a "Motion Canvas animation framework expert."
*   **In-Context Learning:** The prompt includes a comprehensive list of all available example files (`001_...` to `105_...`), complete with a description of the code and its function. This is a powerful technique that effectively gives the AI the "documentation" it needs to understand the available tools.
*   **Selection Priority Guidelines:** The prompt provides clear instructions on how to prioritize examples, telling the AI to focus on **complex and advanced techniques** over basic ones. It guides the model to select examples based on the scene's domain (e.g., math, typography).
*   **Robust Fallback:** The agent's Python script includes a `_smart_fallback_selection` function. If the AI fails to return a useful list of examples, this function uses keyword matching to select relevant examples, making the agent more resilient to failure.


<details>
<summary>Click to view the full prompt</summary>

```
You are a Motion Canvas animation framework expert. Your task is to intelligently select the most relevant example files that would help implement this animation scene, with a focus on COMPLEX ANIMATIONS and ADVANCED TECHNIQUES.

ANIMATION SCENE SPECIFICATION:
{scene_data}

SELECTION PRIORITY GUIDELINES:
1. **PRIMARY FOCUS - Complex & Advanced Examples**: Prioritize sophisticated animations, advanced techniques, and specialized features that match the scene requirements
2. **SECONDARY FOCUS - Domain-Specific Examples**: If the scene involves mathematical visualizations, data charts, typography effects, or geometric transformations, heavily prioritize those domain examples
3. **TERTIARY FOCUS - Foundational Examples**: Only include basic setup examples if they're truly necessary for understanding the implementation pattern
4. **Animation Complexity Priority**:
   - Advanced animations (morphing, complex paths, mathematical functions) > Basic animations (fade, scale, rotate)
   - Multi-step sequences and coordinated animations > Single transformations
   - Dynamic and data-driven content > Static presentations

Core Framework (1-15):
001_basic_scene_setup.tsx:
-Code Description: This file defines and exports a simple Motion Canvas 2D scene using makeScene2D. The scene is currently empty, serving as a starting point where visual elements and animations can later be added. It sets up the structure for building animations but does not yet include any shapes, text, or actions.
-Function Description: The key function here is makeScene2D, which creates a 2D scene in Motion Canvas. It accepts a generator function that controls how the scene is built and animated. The view parameter acts as the root container, where all visual components and animations are placed.

002_simple_rectangle.tsx:
-Code Description: This file creates a Motion Canvas 2D scene that demonstrates step-by-step visualization with synchronized text. It introduces a rectangle whose outline gradually appears while explanatory text simultaneously fades in, ensuring that the visual and textual elements progress together in sync. The example highlights how animations and explanations can be tightly coupled for teaching or demonstration purposes.
-Function Description: The key code here is the yield* all(...) animation block. It synchronizes the rectangle's outline animation with the explanatory text's opacity fade-in. This simultaneous progression forms the central feature of the scene—linking the visual changes of the rectangle with the textual explanation to maintain alignment between demonstration and narration.

003_multiple_shapes.tsx:
-Code Description: This file builds a Motion Canvas 2D scene that introduces the three fundamental shape components—rectangle, circle, and triangle. Each shape appears one after another, with its corresponding explanatory text fading in at the same time. The scene is designed as a teaching demonstration to illustrate the properties of basic shapes while maintaining synchronization between the visuals and their explanations.
-Function Description: The key code here is the stepwise use of yield* all(...) combined with waitFor(...). This sequence controls the synchronized fade-in animations of each shape alongside its explanatory text, ensuring that the rectangle, circle, and triangle are introduced in a structured, timed progression. This synchronization between shapes and text is the core functionality of the scene.

004_basic_text.tsx:
-Code Description: This file creates a Motion Canvas 2D scene that compares two different font styles: sans-serif (Arial) and monospace (Courier New). Each font sample appears alongside an explanatory note, highlighting their typical use cases and readability differences. The scene is designed to visually demonstrate the contrast between these font families in an educational or design-focused context.
-Function Description: The key code here is the synchronized yield* all(...) animation calls, which fade in each font sample at the same time as its explanation. This ensures that the appearance of the text and the corresponding note are perfectly aligned, reinforcing the comparison between sans-serif and monospace fonts.

005_color_basics.tsx:
-Code Description: This file defines a Motion Canvas 2D scene that demonstrates three different shape styles: a filled shape, a stroked shape, and a shape that combines both fill and stroke. Each shape appears alongside explanatory text, visually reinforcing the differences between the styles. The example is designed to illustrate how fill and stroke properties can be applied individually or together to shapes.
-Function Description: The key code is the sequence of yield* all(...) animations, which fade in each shape simultaneously with its corresponding explanation. This synchronization ensures that viewers immediately connect the visual example of the shape style with the descriptive text, making the comparison between fill, stroke, and combined styles clear and effective.

006_opacity_control.tsx:
-Code Description: This file defines a Motion Canvas 2D scene that demonstrates a basic animation cycle of a rectangle: fading in, holding visibility for a short period, and then fading out. Each stage of the animation is synchronized with explanatory text, making it clear what is happening at each step. The example is meant to showcase simple timing and sequencing of animations.
-Function Description: The key code here is the stepwise animation sequence controlled with yield* all(...) and waitFor(...). These functions synchronize the rectangle's fade-in, hold, and fade-out with corresponding updates to the explanatory text, ensuring that the visual change and explanation progress together in a smooth and clear timeline.

007_position_setting.tsx:
-Code Description: This file defines a Motion Canvas 2D scene that demonstrates how basic shapes (rectangle, circle, and triangle) can be introduced sequentially, each paired with an explanatory text. The scene highlights the symbolic meaning of each shape and uses synchronized animations to smoothly transition between them. It serves as an educational demo for linking geometric visuals with conceptual explanations.
-Function Description: The key code here is the sequential animation flow built with yield* all(...) and waitFor(...). These steps ensure that each shape fades in while its corresponding text appears, then transitions out as the next shape and explanation replace it. This coordination between shape visibility and text updates is the central functionality of the scene.

008_scale_transformations.tsx:
-Code Description: This file creates a Motion Canvas 2D scene that demonstrates a scaling animation of a rectangle, synchronized with explanatory text. The rectangle smoothly grows and then shrinks while the text fades in to explain the animation, showing how visual transformations can be paired with descriptive narration in real time.
-Function Description: The key code lies in the synchronized animation sequence built with yield* all(...). It makes the rectangle scale up while the text simultaneously fades in, ensuring both actions are aligned. The following steps then shrink the rectangle back to its original size while keeping the explanation visible, highlighting the concept of synchronized animation between visuals and text.

009_rotation_basics.tsx:
-Code Description: This file defines a Motion Canvas 2D scene where a rectangle rotates a full 360 degrees while explanatory text fades in simultaneously. The purpose of the animation is to demonstrate synchronization between visual motion and descriptive narration, showing how rotation can be paired with explanatory text in real time.
-Function Description: The key code is the synchronized execution using yield* all(...). It ensures the rectangle completes a smooth two-second rotation while the text gradually fades in during the same interval, keeping both elements aligned and reinforcing the concept of visual-text synchronization.

010_anchor_points.tsx:
-Code Description: This file creates a Motion Canvas animation that demonstrates how a rectangle behaves when rotated or scaled around different anchor points. It compares transformations performed around the default center anchor with those around the top-left corner, while synchronized explanatory text updates alongside the visual changes to clarify the effect of anchor point manipulation.
-Function Description: The key code here is the manipulation of the rectangle's anchor point using rectRef().offset([...]) combined with rotation and scaling. By shifting the anchor to different positions (center vs top-left) and applying transformations, the animation highlights how anchor points influence the pivot and scaling behavior of shapes, making the concept visually intuitive.

011_parent_child_hierarchy.tsx:
-Code Description: This file demonstrates a parent-child transformation where a rectangle and an offset circle are grouped together. When the parent group rotates, the circle orbits around the rectangle, visually showing how transformations applied to a parent affect all its child elements. Explanatory text fades in during the orbit to reinforce the concept.
-Function Description: The key code is the rotation of the parent group using parentGroup().rotation(...). By rotating the container rather than individual shapes, the rectangle stays fixed while the offset circle follows an orbital path, clearly illustrating hierarchical transformations in animations.

012_view_management.tsx:
-Code Description: This file creates an animation where a rectangle is always present, while a circle is introduced with a fade-in and scale-up effect, then later removed with a fade-out and shrink. The sequence is synchronized with explanatory text, ensuring the visual transformation and narration occur in parallel for clarity.
-Function Description: The key code is the circle's lifecycle animation handled through circleRef().opacity(...) and circleRef().scale(...). These transformations control the circle's appearance, growth, disappearance, and removal, effectively illustrating how elements can be dynamically introduced and withdrawn within a scene.

013_basic_timing.tsx:
-Code Description: This file defines an animation where a rectangle moves from off-screen into the center, pauses, and then transitions its color from red to blue. Throughout the sequence, explanatory text appears and updates in synchronization with the rectangle's actions, ensuring the narration aligns with the visual transitions.
-Function Description: The key code is the animation sequence that combines rectRef().position.x(...) and rectRef().fill(...) with synchronized text updates using yield* all(...). These coordinated transformations demonstrate how motion and narration can progress together, clearly illustrating both movement and color change in a timed manner.

014_generator_functions.tsx:
-Code Description: This file defines an animation where a rectangle sequentially moves to the right, scales up, and then rotates while changing its color. Each transformation is synchronized with explanatory text that appears and updates in real time, making the progression of the animation clear and descriptive.
-Function Description: The key code lies in the sequential animation steps applied to the rectangle—rectRef().position.x(...), rectRef().scale(...), rectRef().rotation(...), and rectRef().fill(...)—all executed in coordination with textRef().text(...) updates. Together, these actions demonstrate synchronized movement, resizing, rotation, and color change with explanatory narration.

015_reference_creation.tsx:
-Code Description: This Motion Canvas example demonstrates how to use createRef() to animate specific components. A purple rectangle with a reference can be moved, while an orange circle without a reference remains static.
-Function Description: The main feature here is the use of createRef() for targeted control of elements, allowing direct manipulation of properties like opacity and position, while non-referenced components remain unchanged.
```

</details>

<details>
<summary>Click to view the full prompt</summary>

```
You are a Motion Canvas animation framework expert. Your task is to intelligently select the most relevant example files that would help implement this animation scene, with a focus on COMPLEX ANIMATIONS and ADVANCED TECHNIQUES.

ANIMATION SCENE SPECIFICATION:
{scene_data}

SELECTION PRIORITY GUIDELINES:
1. **PRIMARY FOCUS - Complex & Advanced Examples**: Prioritize sophisticated animations, advanced techniques, and specialized features that match the scene requirements
2. **SECONDARY FOCUS - Domain-Specific Examples**: If the scene involves mathematical visualizations, data charts, typography effects, or geometric transformations, heavily prioritize those domain examples
3. **TERTIARY FOCUS - Foundational Examples**: Only include basic setup examples if they're truly necessary for understanding the implementation pattern
4. **Animation Complexity Priority**:
   - Advanced animations (morphing, complex paths, mathematical functions) > Basic animations (fade, scale, rotate)
   - Multi-step sequences and coordinated animations > Single transformations
   - Dynamic and data-driven content > Static presentations

Core Framework (1-15):
001_basic_scene_setup.tsx:
-Code Description: This file defines and exports a simple Motion Canvas 2D scene using makeScene2D. The scene is currently empty, serving as a starting point where visual elements and animations can later be added. It sets up the structure for building animations but does not yet include any shapes, text, or actions.
-Function Description: The key function here is makeScene2D, which creates a 2D scene in Motion Canvas. It accepts a generator function that controls how the scene is built and animated. The view parameter acts as the root container, where all visual components and animations are placed.

002_simple_rectangle.tsx:
-Code Description: This file creates a Motion Canvas 2D scene that demonstrates step-by-step visualization with synchronized text. It introduces a rectangle whose outline gradually appears while explanatory text simultaneously fades in, ensuring that the visual and textual elements progress together in sync. The example highlights how animations and explanations can be tightly coupled for teaching or demonstration purposes.
-Function Description: The key code here is the yield* all(...) animation block. It synchronizes the rectangle's outline animation with the explanatory text's opacity fade-in. This simultaneous progression forms the central feature of the scene—linking the visual changes of the rectangle with the textual explanation to maintain alignment between demonstration and narration.

003_multiple_shapes.tsx:
-Code Description: This file builds a Motion Canvas 2D scene that introduces the three fundamental shape components—rectangle, circle, and triangle. Each shape appears one after another, with its corresponding explanatory text fading in at the same time. The scene is designed as a teaching demonstration to illustrate the properties of basic shapes while maintaining synchronization between the visuals and their explanations.
-Function Description: The key code here is the stepwise use of yield* all(...) combined with waitFor(...). This sequence controls the synchronized fade-in animations of each shape alongside its explanatory text, ensuring that the rectangle, circle, and triangle are introduced in a structured, timed progression. This synchronization between shapes and text is the core functionality of the scene.

004_basic_text.tsx:
-Code Description: This file creates a Motion Canvas 2D scene that compares two different font styles: sans-serif (Arial) and monospace (Courier New). Each font sample appears alongside an explanatory note, highlighting their typical use cases and readability differences. The scene is designed to visually demonstrate the contrast between these font families in an educational or design-focused context.
-Function Description: The key code here is the synchronized yield* all(...) animation calls, which fade in each font sample at the same time as its explanation. This ensures that the appearance of the text and the corresponding note are perfectly aligned, reinforcing the comparison between sans-serif and monospace fonts.

005_color_basics.tsx:
-Code Description: This file defines a Motion Canvas 2D scene that demonstrates three different shape styles: a filled shape, a stroked shape, and a shape that combines both fill and stroke. Each shape appears alongside explanatory text, visually reinforcing the differences between the styles. The example is designed to illustrate how fill and stroke properties can be applied individually or together to shapes.
-Function Description: The key code is the sequence of yield* all(...) animations, which fade in each shape simultaneously with its corresponding explanation. This synchronization ensures that viewers immediately connect the visual example of the shape style with the descriptive text, making the comparison between fill, stroke, and combined styles clear and effective.

006_opacity_control.tsx:
-Code Description: This file defines a Motion Canvas 2D scene that demonstrates a basic animation cycle of a rectangle: fading in, holding visibility for a short period, and then fading out. Each stage of the animation is synchronized with explanatory text, making it clear what is happening at each step. The example is meant to showcase simple timing and sequencing of animations.
-Function Description: The key code here is the stepwise animation sequence controlled with yield* all(...) and waitFor(...). These functions synchronize the rectangle's fade-in, hold, and fade-out with corresponding updates to the explanatory text, ensuring that the visual change and explanation progress together in a smooth and clear timeline.

007_position_setting.tsx:
-Code Description: This file defines a Motion Canvas 2D scene that demonstrates how basic shapes (rectangle, circle, and triangle) can be introduced sequentially, each paired with an explanatory text. The scene highlights the symbolic meaning of each shape and uses synchronized animations to smoothly transition between them. It serves as an educational demo for linking geometric visuals with conceptual explanations.
-Function Description: The key code here is the sequential animation flow built with yield* all(...) and waitFor(...). These steps ensure that each shape fades in while its corresponding text appears, then transitions out as the next shape and explanation replace it. This coordination between shape visibility and text updates is the central functionality of the scene.

008_scale_transformations.tsx:
-Code Description: This file creates a Motion Canvas 2D scene that demonstrates a scaling animation of a rectangle, synchronized with explanatory text. The rectangle smoothly grows and then shrinks while the text fades in to explain the animation, showing how visual transformations can be paired with descriptive narration in real time.
-Function Description: The key code lies in the synchronized animation sequence built with yield* all(...). It makes the rectangle scale up while the text simultaneously fades in, ensuring both actions are aligned. The following steps then shrink the rectangle back to its original size while keeping the explanation visible, highlighting the concept of synchronized animation between visuals and text.

009_rotation_basics.tsx:
-Code Description: This file defines a Motion Canvas 2D scene where a rectangle rotates a full 360 degrees while explanatory text fades in simultaneously. The purpose of the animation is to demonstrate synchronization between visual motion and descriptive narration, showing how rotation can be paired with explanatory text in real time.
-Function Description: The key code is the synchronized execution using yield* all(...). It ensures the rectangle completes a smooth two-second rotation while the text gradually fades in during the same interval, keeping both elements aligned and reinforcing the concept of visual-text synchronization.

010_anchor_points.tsx:
-Code Description: This file creates a Motion Canvas animation that demonstrates how a rectangle behaves when rotated or scaled around different anchor points. It compares transformations performed around the default center anchor with those around the top-left corner, while synchronized explanatory text updates alongside the visual changes to clarify the effect of anchor point manipulation.
-Function Description: The key code here is the manipulation of the rectangle's anchor point using rectRef().offset([...]) combined with rotation and scaling. By shifting the anchor to different positions (center vs top-left) and applying transformations, the animation highlights how anchor points influence the pivot and scaling behavior of shapes, making the concept visually intuitive.

011_parent_child_hierarchy.tsx:
-Code Description: This file demonstrates a parent-child transformation where a rectangle and an offset circle are grouped together. When the parent group rotates, the circle orbits around the rectangle, visually showing how transformations applied to a parent affect all its child elements. Explanatory text fades in during the orbit to reinforce the concept.
-Function Description: The key code is the rotation of the parent group using parentGroup().rotation(...). By rotating the container rather than individual shapes, the rectangle stays fixed while the offset circle follows an orbital path, clearly illustrating hierarchical transformations in animations.

012_view_management.tsx:
-Code Description: This file creates an animation where a rectangle is always present, while a circle is introduced with a fade-in and scale-up effect, then later removed with a fade-out and shrink. The sequence is synchronized with explanatory text, ensuring the visual transformation and narration occur in parallel for clarity.
-Function Description: The key code is the circle's lifecycle animation handled through circleRef().opacity(...) and circleRef().scale(...). These transformations control the circle's appearance, growth, disappearance, and removal, effectively illustrating how elements can be dynamically introduced and withdrawn within a scene.

013_basic_timing.tsx:
-Code Description: This file defines an animation where a rectangle moves from off-screen into the center, pauses, and then transitions its color from red to blue. Throughout the sequence, explanatory text appears and updates in synchronization with the rectangle's actions, ensuring the narration aligns with the visual transitions.
-Function Description: The key code is the animation sequence that combines rectRef().position.x(...) and rectRef().fill(...) with synchronized text updates using yield* all(...). These coordinated transformations demonstrate how motion and narration can progress together, clearly illustrating both movement and color change in a timed manner.

014_generator_functions.tsx:
-Code Description: This file defines an animation where a rectangle sequentially moves to the right, scales up, and then rotates while changing its color. Each transformation is synchronized with explanatory text that appears and updates in real time, making the progression of the animation clear and descriptive.
-Function Description: The key code lies in the sequential animation steps applied to the rectangle—rectRef().position.x(...), rectRef().scale(...), rectRef().rotation(...), and rectRef().fill(...)—all executed in coordination with textRef().text(...) updates. Together, these actions demonstrate synchronized movement, resizing, rotation, and color change with explanatory narration.

015_reference_creation.tsx:
-Code Description: This Motion Canvas example demonstrates how to use createRef() to animate specific components. A purple rectangle with a reference can be moved, while an orange circle without a reference remains static.
-Function Description: The main feature here is the use of createRef() for targeted control of elements, allowing direct manipulation of properties like opacity and position, while non-referenced components remain unchanged.

Geometry & Styling (16-30):
016_rectangle_variants.tsx:
-Code Description: This Motion Canvas example demonstrates a split-screen layout with animated rectangles on the left (40%) and descriptive text on the right (60%). Three rectangles animate sequentially using properties like height, width, and scale to showcase different transformations.
-Function Description: This code focuses on using createRef() to control rectangles and text elements, enabling synchronized animations such as height growth, width expansion, and scale adjustments for smooth transitions.

017_circle_animations.tsx:
-Code Description: This Motion Canvas example demonstrates animated effects on a circle. The circle performs pulsing (expanding and contracting) and stroke animations, showcasing how to synchronize shape transformations with other elements.
-Function Description: The file illustrates circle animation techniques such as pulsing (size transitions with easing) and stroke manipulation using startAngle and endAngle for dynamic drawing and erasing effects, combined with synchronized animation timing.

018_polygon_creation.tsx:
-Code Description: This Motion Canvas example demonstrates creating and animating polygons using the Line component. Shapes like a triangle, pentagon, and star scale into view sequentially, highlighting how to build complex forms through point coordinates.
-Function Description: The key concept in this file is polygon construction and animation using Line, which allows defining shapes through point arrays and animating their appearance with scaling. This approach supports custom designs and follows best practices by using Line for flexibility instead of fixed Polygon components.

019_line_drawing.tsx:
-Code Description: This Motion Canvas example demonstrates various line styles. It showcases solid, dashed, arrowed, and rounded lines, each animated sequentially with synchronized property changes for visual distinction.
-Function Description: The key concept here is the use of the Line component with different style attributes such as lineDash for dashes, startArrow and endArrow for arrowheads, and lineCap for rounded ends. These variations demonstrate how to customize and animate line appearances effectively.

020_path_creation.tsx:
-Code Description: This Motion Canvas example illustrates animating a custom Bezier curve. The left panel displays the path drawing effect using the Path component, while the right panel shows synchronized explanatory text. The animation employs end property changes for smooth stroke rendering and uses a reusable background component.
-Function Description: The key feature here is path drawing animation using the Path component with SVG-like data (M -400 0 C -200 -200, 200 200, 400 0). The property end is animated from 0 to 1 to reveal the stroke progressively, and yield* all(...) ensures the path and text fade-in occur simultaneously for a coordinated effect.

021_gradient_fills.tsx:
-Code Description: This Motion Canvas example showcases linear and radial gradient animations. The left section visualizes a rectangle with a linear gradient and a circle with a radial gradient, while the right side presents synchronized explanatory text. It demonstrates gradient creation, color stops, and property transitions for dynamic visual effects.
-Function Description: The main feature is gradient animation using the Gradient class applied to shapes. Gradients are defined with type, stops, and positional properties (from, to, fromRadius, toRadius). Animations are performed by updating the fill property of the Rect and Circle elements with new gradient configurations, synchronized using yield* all(...).

022_border_styling.tsx:
-Code Description: This example illustrates stroke and line styling techniques in Motion Canvas. It features a rectangle with animated stroke width, a circle with dynamic dash pattern, and three lines showcasing different lineCap styles (butt, round, square).
-Function Description: The implementation demonstrates how to animate stroke properties and apply varied line styles. Key actions include animating a rectangle's stroke thickness and moving a dashed stroke on a circle, along with presenting multiple line cap variations for visual comparison.

023_shadow_effects.tsx:
-Code Description: This example demonstrates drop shadow and glow effects in Motion Canvas within a split-screen layout. It applies a deep shadow effect to a rectangle and a glowing aura to text using shadowBlur, shadowOffset, and shadowColor animations. The design uses easing functions (easeOutCubic, easeInCubic) to create smooth transitions.
-Function Description: The implementation illustrates how to apply and animate shadow-based visual effects. Key actions include adding a drop shadow to enhance depth perception and applying a glow effect on text for emphasis. Both effects use property transitions for blur, offset, and color opacity.

024_text_mapping.tsx:
-Code Description: This scene demonstrates two visual design concepts in Motion Canvas: repeating patterns and texture mapping. A tiled rectangle illustrates how small elements create larger textures, while layered circles showcase depth and material simulation.
-Function Description: The implementation highlights creating and animating patterns and textures for visual richness. It generates a grid of colored tiles inside a container and concentric circle layers with opacity variations to simulate texture. These elements are revealed step by step with synchronized text and animated pulses using scaling transitions for emphasis.

025_shape_morphing.tsx:
-Code Description: This Motion Canvas scene demonstrates shape morphing with smooth transitions using a split-screen layout. A square progressively transforms into a circle, then a rounded rectangle, and finally returns to its original square shape. The background remains solid white, and the text fades in synchronously with the morphing animations to guide the viewer.
-Function Description: The implementation showcases radius-based morphing and dynamic property updates for shape transformations. The code uses shape().radius(100, 1.5, easeInOutCubic) to turn a square into a circle and later adjusts width and height for creating a rounded rectangle. Animations leverage yield* all(...) to synchronize shape morphing, color changes, and rotations in real time for a fluid effect.

026_composite_shapes.tsx - Shape composition
-Code Description:This Motion Canvas example simulates Boolean operations (Union, Subtraction, Intersection, Difference) using two overlapping shapes because native Boolean path operations are not supported. The layout uses a 40:60 split where the left side shows animated shapes (circle and rectangle) and the right side updates text synchronously to describe each step. The visual effects rely on color changes, opacity transitions, and shape positioning to metaphorically represent Boolean concepts.
-Function Description:The implementation demonstrates dynamic property animations and reference-driven updates for multiple shapes. It uses createRef() to access the circle and rectangle for animating properties like fill and opacity during transitions. Core techniques include yield* all(...) for synchronized animations and easing functions like easeInOutCubic for smooth property changes across all visual states.

027_custom_shape_classes.tsx - Custom components
-Code Description:This example demonstrates a custom LabeledRect component with a dynamic label property and synchronized animations. It highlights creating reusable components and binding text to signals for real-time updates.
-Function Description:The implementation focuses on using signals for dynamic property updates and synchronized animations. The LabeledRect class extends Rect and binds its label to a Txt element through @signal(), enabling smooth updates like myLabeledRect().label('Finished!', 2) alongside other animations using yield* all(...).

028_shape_clipping.tsx - Clipping masks
-Code Description:This file demonstrates a circular mask-based reveal animation using clipping in Motion Canvas. It implements a circular container with clip={{true}} that hides overflow content and animates a rectangle sliding into view through the masked area, showcasing how masking and reveal effects can be synchronized with other elements.
-Function Description:
The implementation focuses on using a Circle with clipping enabled and animating content inside it. The key operation involves clip={{true}} to enforce the mask and an animated transition like revealRect().position.y(0, 2, easeOutCubic) to perform the reveal effect, illustrating how clipping and motion work together for visual emphasis.

029_wireframe_mode.tsx - Outline rendering
-Code Description:This file demonstrates a wireframe-style animation where a rectangle, circle, and line fade in sequentially with slight rotations, followed by a synchronized reset to their original state. The text appears after the shapes animate, maintaining smooth transitions using easing functions.
-Function Description:The implementation highlights animated property transitions such as opacity and rotation using yield* all(rectRef().opacity(1, 1, easeInOutCubic)) and similar calls. These allow multiple elements to animate in parallel while maintaining precise timing and easing for smooth effects.

030_shape_interpolation.tsx - Shape interpolation
-Code Description:This file demonstrates shape morphing animation by smoothly interpolating between two SVG paths (triangle and star) using Motion Canvas. The animation also synchronizes text opacity changes with the shape transformation for a cohesive effect.
-Function Description:The core feature is path interpolation using interpolatingShape().data(starPath, 2, easeInOutCubic), which animates the shape from triangle to star with easing for smooth transitions. This is combined with synchronized opacity changes using explanationText().opacity(1, 2) to create a visually aligned animation and text reveal.


Typography (51-60):
051_font_loading.tsx: - Font loading
-Code Description:This file demonstrates custom font usage in Motion Canvas, combining text and shape animations for a synchronized effect. The example showcases applying different font families (serif and Inter) with animated text opacity and scaling, alongside a rectangle that pulses in sync.
-Function Description:The core feature is text and shape synchronization with font styling. Key actions include animating text opacity and scale using customFontText().scale(1, 1.5, easeOutBack) and combining it with a rectangle pulse animation via vizRect().scale(1.2, 0.5, easeOutBack).to(1, 0.5, easeOutBack), all orchestrated using yield* all(...) for simultaneous effects.

052_text_styling.tsx: - Text styling
-Code Description:This file demonstrates how to render text with varying styles such as small, bold, italic, and fully styled in Motion Canvas, synchronized with a visual element (a horizontal line). It shows how to animate text properties like opacity and scale alongside line effects for a cohesive reveal.
-Function Description:The main feature is synchronizing styled text with a visual line using yield* all(...) for parallel animations. Key actions include text opacity transitions like smallText().opacity(1, 0.6) and combined scale effects such as allStyledText().scale(1, 1, easeOutBack) while animating the line with changes like vizLine().stroke('#42A5F5', 0.6) for color emphasis.

053_text_animation.tsx: - Text animations
-Code Description:This file demonstrates character-by-character text reveal synchronized with a subtle line animation. The text progressively appears while the line reacts dynamically, creating an engaging typing effect paired with visualization changes.
-Function Description:The key feature is incremental text rendering with synchronized property changes using a loop and yield* all(...). For example, textRef().text(fullText.slice(0, i), 0.05) reveals one character at a time while vizLine().lineWidth(10 + (i % 3), 0.05) adds a pulsing effect to the line, maintaining tight sync between text and visualization.

054_typewriter_effect.tsx: - Progressive text
-Code Description:This example implements a typewriter text effect where characters appear one at a time, and a visualization element (line) animates in sync to enhance engagement. Text wrapping is handled dynamically based on available width.
-Function Description:The core feature is incremental text reveal synchronized with line animation using Motion Canvas timeline utilities. For example, textRef().text(displayedText + currentLine) updates text progressively, while yield* waitFor(0.05) controls typing speed, creating a smooth, time-based effect.

055_text_along_path.tsx: - Path text
-Code Description:This example demonstrates text rendering along a complete curve, where each character is positioned and rotated based on the curve's tangent. It uses dynamic calculations for arc length and interpolation to distribute letters precisely across the path.
-Function Description:The implementation provides curve-based positioning and orientation for text using core geometry computations. For instance, getPointAtLength() interpolates positions along the polyline, while getTangentAtLength() calculates the tangent angle for accurate letter rotation, ensuring alignment with the curve's flow.

056_mathematical_notation.tsx - Math rendering
-Code Description: This example demonstrates rendering and animating LaTeX mathematical expressions alongside a simple shape animation, creating synchronized visual and symbolic explanations. Key interactions include animating a line (end property) while equations gradually appear, and applying transformations such as scaling and color changes to enhance the effect.
-Function Description: The implementation uses Latex components for math rendering and createRef() for direct control of shapes and equations during animation. Core operations include lineRef().end(1, 1) to reveal a line progressively and quadraticFormula().opacity(1, 1) to fade in equations, enabling precise, synchronized animations across visual and textual elements.

057_rich_text_formatting.tsx - Rich text
-Code Description:This example demonstrates simulated rich text styling by combining multiple Txt components with different styles (bold, italic, color) into a single line. The styled text fades in while a horizontal line is drawn, ensuring smooth and synchronized animation for both elements.
-Function Description: The implementation uses createRef() to control individual text parts and shapes during the animation. For instance, line().end(1, 2) gradually draws the line, while multiple Txt components like part2().opacity(1, 2) fade in simultaneously, creating the effect of styled text appearing in sync with the line animation.

058_text_measurements.tsx - Text metrics
-Code Description: This example demonstrates dynamic text measurement and visualization, where a bounding box resizes to fit the text and a baseline indicates alignment. Animations synchronize text updates, bounding box adjustments, and explanatory text changes for a clear visual representation of text dimensions.
-Function Description: The implementation uses createRef() to control both text and shapes, enabling responsive animations.Key operations include updating box size relative to text dimensions, ensuring the bounding box adapts whenever the text changes in content or font size.

059_text_justification.tsx - Text alignment
-Code Description: This example demonstrates synchronizing multiple text alignments with an animated visual element. A vertical line animates in three steps, while corresponding text elements (left, center, and right aligned) fade in sequentially, ensuring coordinated timing using yield* all(...).
-Function Description: The implementation uses createRef() to directly manipulate properties of the line and text components during animation. Key operations include synchronizing animations with:
yield* all(visualLine().end(0.33, 1), txtLeft().opacity(1, 1)), which grows the line to one-third while revealing the first text element.

060_dynamic_text_content.tsx - Dynamic text
Code Description: This code creates a synchronized animation where a line grows upward while a numeric value increases from 0 to 100. Both the text and visualization appear together, update in real time, and then fade out simultaneously.

Function Description: The main functionality is powered by createSignal, which links the animated value to both the line’s height and the displayed number, ensuring they stay perfectly synchronized throughout the animation.


Basic Animations (61-75):
061_linear_motion.tsx - Object moving in straight line
-Code Description: This code demonstrates the concept of linear motion by showing a red ball moving steadily from the left end to the right end of a straight horizontal line. As the ball moves, explanatory text appears in sequence, defining linear motion, describing constant velocity, and highlighting key points such as uniform displacement, constant velocity, and straight-line path. The animation ties together the ball’s movement and the explanations to visually reinforce the concept.
-Function Description: The core functionality lies in animating the ball’s horizontal position (ball().position.x) from -300 to 300 using easing for smooth motion, while synchronizing the text appearance with yield* all(). This ensures the motion of the ball and the educational text progress together, effectively illustrating linear motion in both visual and explanatory forms.

062_circular_motion.tsx - Objects moving in circles
-Code Description: This code demonstrates circular motion by animating a blue ball moving smoothly around a circular path centered at a fixed point. As the ball completes its revolution, explanatory text appears step by step to define circular motion and describe its characteristics, such as constant distance from the center, continuous change in velocity direction, and the role of centripetal force. The animation visually connects the motion of the ball with the theoretical concepts.
-Function Description: The main functionality is implemented in the animateCircularMotion generator, which calculates the ball’s position on the circle using trigonometric functions (cos and sin) for each step of the revolution. This keeps the ball moving smoothly around the circle, while yield* all() synchronizes its motion with the explanatory text.

063_bezier_curves.tsx - Smooth curved motion paths
-Code Description:This code demonstrates Bezier curves by animating a green ball moving smoothly along a cubic Bezier path defined by four control points. While the ball travels the curve, explanatory text appears in sequence, describing how Bezier curves are constructed, the role of control points, and how they create smooth, flowing motion. The visualization includes the curve itself, the control points, and helper lines to illustrate the curve’s structure.
-Function Description: The key functionality is in the Bezier motion system, where calculateBezierPoint(t) computes the ball’s position on the curve using the cubic Bezier equation. The animateBezierMotion generator moves the ball step by step along the calculated points, while yield* all() synchronizes the curve animation with explanatory text.

064_easing_functions.tsx - Different timing curves
-Code Description: This code demonstrates different easing functions by animating colored balls moving across a horizontal track. Each ball uses a unique easing function — linear, ease-in, ease-out, ease-in-out, bounce, and back — to show how timing curves affect the speed and feel of motion. Explanatory text appears alongside the animations, describing each easing type as its corresponding ball moves, creating a clear connection between concept and visualization.
-Function Description:The core functionality uses easing functions like linear, easeInCubic, easeInOutCubic, easeOutBounce, and easeOutBack to animate the balls’ positions along the track. The sequence is orchestrated with yield* all() so that the ball’s movement and the matching text explanation appear together, synchronizing visual demonstration with descriptive guidance.

065_chain_animations.tsx - Sequential animation sequences
-Code Description:This code demonstrates chain animations by animating a sequence of five connected circles. Each circle appears one after another with connecting lines, showing how animations can be triggered sequentially to form smooth, flowing transitions. The explanation text introduces concepts such as sequential flow, chain() for controlling order, yield* for waiting, and all() for simultaneous actions. At the end, the circles perform a coordinated wave effect with scaling and color changes, reinforcing the idea of combining sequential and simultaneous animation control.
-Function Description:The main functionality uses chain() to queue multiple animations in sequence, while yield* ensures one completes before the next starts. Circles scale in with bounce easing, lines fade in to connect them, and later, all() allows several circles to animate together in synchronized pulses. This combination of chain, yield*, and all() demonstrates how to structure complex, natural-looking animation sequences step by

066_parallel_animations.tsx - Multiple simultaneous animations
-Code Description:This code demonstrates parallel animations by animating three circles and motion path lines simultaneously. The red circle bounces vertically, the blue circle rotates, and the green circle scales in and out, while lines appear to indicate motion paths. Explanatory text appears in sync with the animations to highlight parallel animation concepts.
-Function Description:
The main functionality uses yield* all() to run multiple animations at the same time. Each circle follows a distinct motion—bounce, rotation, or scaling—while lines fade in and out to emphasize their paths. Text elements appear in coordination with the visual actions, showing how parallel animations can be synchronized for smooth demonstrations.

067_loop_animations.tsx - Repeating motion patterns
-Code Description:This code demonstrates loop animations by animating multiple shapes with repeating motion patterns. Four types of loops are shown: a red circle spinning in place, an orange circle oscillating back and forth, a green circle pulsing in size, and a blue circle orbiting around a central point. Explanatory text fades in step by step to describe each loop type as the animations begin, reinforcing the concept of infinite motion.
-Function Description:The core functionality uses the loop(Infinity, ...) construct to create repeating animations. Each loop resets its state before the next cycle, allowing continuous motion. Circles perform rotation, oscillation, pulsing, and orbiting patterns while synchronized text explains the concept of infinite repetition. All loops run in parallel using yield* all(), demonstrating how Motion Canvas handles ongoing animations with smooth synchronization.

068_bounce_effects.tsx - Spring-like animations
-Code Description: This code demonstrates bounce effects using three colored balls animated with different easing functions. The red ball shows a classic diminishing bounce, the blue ball performs an elastic overshoot bounce, and the green ball exhibits smooth spring-like motion. Visual references like a ground line and trajectory guide are included, while explanatory text appears in sync with each bounce type to highlight their characteristics.
-Function Description: The animation sequence is divided into phases where text and visuals appear together using yield* all(). Each ball uses a specific easing function: easeOutBounce for classic rebounds, easeOutElastic for elastic oscillation, and easeInOutBounce for spring settling. Scale changes on impact simulate compression and release, enhancing realism. The sequence progresses from single drops to multiple bounce cycles, and finally to synchronized impacts, demonstrating how different easing functions can create natural, physics-like bounce behaviors.


069_elastic_animations.tsx - Overshoot and settle
-Code Description: This code creates an interactive animation that demonstrates elastic motion behaviors such as overshoot, spring-like settling, and bouncy oscillations. It visually explains different easing functions—like back easing and elastic easing—through animated shapes, synchronized with explanatory text, to show how objects can overshoot a target and then naturally settle into place, mimicking real-world spring and elastic dynamics.
-Function Description: The key functionality of this code is the demonstration of elastic and spring-like easing animations. Using easing functions such as easeOutBack, easeOutElastic, and their variations, the code animates shapes to illustrate overshoot, bounce, and gradual settling effects, highlighting how these motions create natural, lively, and physics-inspired animations.

Layout & Composition (76-90):

076_grid_layouts.tsx - Arranging objects in grids
-Code Description: This code demonstrates how to use the Grid component in Motion Canvas to arrange multiple elements in a structured grid layout. It visually shows how properties like spacing and direction affect the arrangement of items, while synchronized explanatory text highlights each property step-by-step.
-Function Description: The key functionality of this code is the visualization of the Grid layout system using the <Grid> component. It animates changes to key properties such as grid().spacing(), which controls the gaps between items, and grid().direction(), which sets whether items flow in rows or columns. By applying these properties to a collection of <Rect> elements inside the grid, the code demonstrates how grids resize and rearrange their content dynamically, making the alignment behavior clear and interactive.

077_flex_layouts.tsx - Flexible box layouts
Code Description: This code demonstrates how to use the Flex layout system in Motion Canvas to arrange elements dynamically inside a flexible container. It shows how items can be aligned and distributed along different axes, and how adjusting properties like direction, justifyContent, and alignItems changes the positioning of objects in real time, with synchronized explanatory text guiding the process.

Function Description: The key functionality of this code is the visualization of the Flex layout system using a <Rect layout> container. It animates key properties such as flexContainer().direction(), which controls horizontal or vertical flow of items, flexContainer().justifyContent(), which distributes space along the main axis, and flexContainer().alignItems(), which aligns elements along the cross axis. By applying these properties to child <Rect> elements, the code illustrates how flex layouts enable responsive and adaptable arrangements within a container.

078_stack_layouts.tsx - Vertical/horizontal stacking
-Code Description: This code demonstrates how to use the Stack layout system in Motion Canvas to arrange elements in either a vertical or horizontal sequence. It visually explains how properties such as direction, gap, and alignItems affect the arrangement of stacked items, while synchronized explanatory text provides step-by-step guidance.
-Function Description: The key functionality of this code is the visualization of the Stack layout system using a <Layout layout> container. It animates key properties such as stackContainer().direction() to switch between vertical and horizontal stacking, stackContainer().gap() to add spacing between items, and stackContainer().alignItems() to control alignment along the cross axis. By applying these properties to a sequence of child <Rect> elements, the code effectively illustrates how stack layouts provide simple, sequential arrangements of items.

079_circular_arrangements.tsx - Objects in circles
-Code Description: This code shows how to arrange objects in a circular pattern using trigonometry in Motion Canvas. By applying sine and cosine, elements are evenly distributed around a center point, with a guide circle and radius line illustrating the concept. The objects animate outward from the center, while synchronized text explains radius, angles, and common use cases like radial menus or orbits.
-Function Description: The main functionality is to visualize circular arrangements by calculating positions with Math.cos() and Math.sin() and animating them using position(). A guide circle and radius line introduce the idea of distance from the center, after which the objects move into place along the circumference. The scene concludes with a slow rotation, highlighting circular motion and reinforcing how radius and angles define evenly spaced placements.

080_dynamic_layouts.tsx - Responsive to content changes
-Code Description: This code demonstrates how Motion Canvas layouts can dynamically adapt when their content changes. It visually presents a flex-style container on the left side of the screen where items are added and removed, while explanatory text on the right narrates the process in sync. The scene shows how layouts automatically recalculate spacing and positioning when child elements are modified, and how these changes are animated smoothly for clarity.
-Function Description:The main functionality is to illustrate the behavior of dynamic layouts by animating updates as items are added or removed. The code introduces the concept with a styled container holding two rectangles. A third rectangle is then created and added using container().children()[0].add(newRect), which triggers the layout to reflow. This item’s appearance is animated with width() and opacity() to smoothly expand into place. Later, an existing item is removed after animating its shrink and fade-out with the same properties, again causing the layout to readjust. By combining <Layout> and <Rect> components with property animations, the code clearly demonstrates how layouts remain responsive and animated when their contents change.

081_alignment_systems.tsx - Center, edge alignment
-Code Description: This code demonstrates how alignment systems in Motion Canvas can be used to control the positioning of objects within a container. The visual side of the scene shows a parent container holding a single object that transitions smoothly between different alignment states, while the text side provides synchronized explanations of the alignment properties being applied. The sequence illustrates how justifyContent and alignItems work together to move the object from the center, to the top-left edge, then to the bottom-right edge, and finally back to the center.
-Function Description: The primary functionality is to animate the effect of alignment properties in a layout container. The container starts with its child object centered using justifyContent('center') and alignItems('center'). It then transitions to the top-left corner with justifyContent('start') and alignItems('start'), shifts to the bottom-right using justifyContent('end') and alignItems('end'), and returns to the center alignment. By combining <Layout> and <Rect> components with property animations, the code provides a clear and interactive demonstration of how alignment systems reposition elements within a parent container.

082_spacing_controls.tsx - Margins and padding
-Code Description: This code demonstrates how padding and gap in Motion Canvas control spacing within and between elements. On the left, a container first expands its inner padding, then introduces a second item with animated spacing between them, while synchronized text on the right explains the process.
-Function Description: The main functionality is to show spacing effects by animating container().padding() to add inner space and container().gap() to separate sibling items. A second rectangle is added with width() and opacity() animations, clearly illustrating how these properties create clean and organized layouts.

083_layout_animations.tsx - Transitioning between layouts
-Code Description: This code demonstrates how Motion Canvas can animate smooth transitions between different layout types. The left side shows a container that begins as a grid-like layout with wrapping enabled, then transitions into a single flex row as wrapping is disabled. On the right, synchronized text explains each step of the process, highlighting how Motion Canvas automatically animates the rearrangement of items.
-Function Description: The main functionality is to visualize layout transitions by animating container properties. The container starts with wrap('wrap') and a fixed width to form a 2×2 grid of items. It then animates to a flex row by switching to wrap('nowrap'), increasing its width with container().width(), and adjusting spacing using justifyContent(). The automatic repositioning of child elements is smoothly handled by Motion Canvas, clearly illustrating how complex layout changes can be animated with minimal code.

084_responsive_design.tsx - Adapting to different sizes
-Code Description: This code demonstrates responsive design in Motion Canvas by showing how a container adapts its structure as its size changes. On the left, the container starts in a wide horizontal layout, then smoothly transitions into a vertical stack when narrowed, and finally returns to its original row layout. On the right, synchronized text explains each stage, highlighting how responsive layouts adjust to different screen sizes.
-Function Description: The functionality is to visualize layout reflow based on available space by animating container properties. The container begins in a row layout with direction('row'), then transitions to a stacked layout by shrinking its width with container().width(), switching to direction('column'), and adjusting spacing with gap(). It then animates back to the row structure, illustrating how Motion Canvas enables smooth, fluid transitions for responsive design

085_component_composition.tsx - Reusable layout components
-Code Description: This code demonstrates component composition in Motion Canvas by building a simple UI using a reusable StyledButton component. On the left, three differently styled buttons are introduced one by one to show how the same component can be reused with different properties. On the right, synchronized explanatory text highlights the idea of constructing complex interfaces from smaller building blocks.
-Function Description: The functionality is to illustrate reusable component design by defining a StyledButton that wraps a <Rect> with consistent styles and a <Txt> label. Multiple instances are created with different text and color props and animated into view using scale(). The scene emphasizes how component composition leads to cleaner, modular, and more maintainable code while enabling consistency and reusability in UI design.

086_nested_layouts.tsx - Complex hierarchical layouts
-Code Description: This code demonstrates how nested layouts can be used in Motion Canvas to build structured, hierarchical UIs. On the left, a main vertical container gradually appears, and within it two horizontal rows animate into place, each holding differently sized rectangles. On the right, synchronized text explains the process, showing how layouts can be composed inside one another to create complex designs.
-Function Description: The functionality is to illustrate hierarchical composition by animating a vertical container created with direction('column'), then introducing two nested horizontal rows defined with direction('row'). These child layouts are animated into view using scale(), while the outer container fades in via opacity(). This example highlights how nesting <Layout> components enables grouping, organization, and the construction of flexible, multi-level user interfaces.

087_flow_layouts.tsx - Text flow around objects
-Code Description: This code demonstrates a flow layout in Motion Canvas, where text elements wrap naturally around a fixed object inside a container. On the left, a blue rectangle is placed inside a wrapping container, and a sentence is split into words that animate in one by one, flowing around the object. On the right, synchronized text explains how the wrapping behavior works and how responsive changes affect layout.
-Function Description: The functionality is to visualize wrapping behavior by defining a container with direction('row') and wrap('wrap'), placing a fixed rectangle inside, and adding <Txt> elements for each word. The words animate into view sequentially with opacity(), demonstrating how they automatically move to the next line when space is limited. Finally, resizing the container with width() and height() triggers reflow, clearly showing how flow layouts adapt responsively.

088_masonry_layouts.tsx - Pinterest-style arrangements
-Code Description: This code demonstrates how to build a Masonry layout, also known as a Pinterest-style grid, in Motion Canvas. On the left, blocks of varying heights animate upward from the bottom of the container and settle into a compact grid arrangement that minimizes vertical gaps. On the right, synchronized explanatory text introduces the concept, explains how items are placed into columns, and highlights how the shortest column is filled first to achieve a balanced layout.
-Function Description: The functionality is to illustrate custom item positioning for a Masonry grid by calculating positions manually. The container is divided into numColumns, and each block is assigned a column based on the current columnHeights. Using position() and opacity(), items animate from the bottom of the container to their computed positions, while columnHeights is updated to keep track of vertical stacking. This approach shows how Motion Canvas can simulate layouts not directly supported by built-in properties, while still maintaining smooth, animated behavior.

089_timeline_layouts.tsx - Horizontal time-based layouts
-Code Description: This code demonstrates how to create a horizontal timeline layout in Motion Canvas, where events appear in sequence along a central axis. On the left, a horizontal line is drawn to represent the flow of time, and colored circles with labels appear one after another at different positions, representing key years. On the right, synchronized explanatory text introduces the timeline concept, explains the axis, event markers, and the chronological order of placement.
-Function Description: The functionality is to illustrate sequential event visualization by animating a Line for the time axis and revealing event markers using Circle and Txt components. The timeline is drawn with end(), while events animate into place with scale() for circles and opacity() for labels. Events are revealed in order using chain(), showing how Motion Canvas can present chronological data with smooth, step-by-step animations.

090_dashboard_layouts.tsx - Multi-panel compositions
-Code Description: This code demonstrates how to construct a multi-panel dashboard layout in Motion Canvas using nested layouts. On the left, a dashboard container is introduced, and its panels gradually expand into place: a header at the top, a sidebar on the left, and a main content area on the right, all inside a parent container. On the right, synchronized explanatory text highlights the idea of structuring dashboards through composition, explaining how panels combine into a clean, hierarchical UI.
-Function Description: The functionality is to illustrate building a dashboard interface by animating a parent Rect container with direction('column'), containing a header panel and a body layout. The body uses direction('row') to hold a sidebar and a mainContent panel. These panels are animated into place by modifying their scale(), width(), and height() values in sequence, showing how Motion Canvas can demonstrate both vertical and horizontal nesting to achieve clear multi-section dashboard structures.

Mathematical Visualizations (91-105):
091_function_plotting.tsx - 2D function graphs
-Code Description: This file defines an animated scene that plots a sine wave across a defined range and synchronizes the graph’s animation with explanatory text. The sine curve is drawn progressively from left to right while corresponding text fades in, providing a clear demonstration of mathematical function plotting alongside descriptive narration.
-Function Description: The key code is the plotting and animation of the sine wave using Line with graphLine().end(1, 3, linear), which gradually reveals the curve over time. This is synchronized with heading().opacity(...) and description().opacity(...), ensuring that the explanatory text appears in sync with the graph animation.

092_parametric_curves.tsx - t-based curve generation
-Code Description: This file creates an animated visualization of a parametric curve defined by $x(t) = 200 \\cos(t)$ and $y(t) = 150 \\sin(2t)$. The curve is drawn progressively over the specified range of $t$, while explanatory text describing the equations and parameters appears in sync with the animation.
-Function Description: The key code is the parametric curve plotting and synchronized animation achieved by gradually rendering the curve with curveLine().end(1, 3, linear) while simultaneously fading in the explanatory text using textBlock().opacity(1, 3, linear). This ensures both the visual curve and its explanation appear together in a coordinated manner.

093_polar_coordinates.tsx - r,θ based plotting
-Code Description: This code visualizes a polar curve defined by the equation r(θ) = 200·sin(4θ). It converts polar coordinates into Cartesian points to plot the curve and synchronizes its animation with explanatory text. The animation gradually draws the curve while the corresponding mathematical details fade in, helping illustrate the relationship between the equation and its geometric shape.
-Function Description: The key function of this code is to generate and animate a *4-petal rose curve* by converting the polar equation r(θ) = 200·sin(4θ) into Cartesian coordinates and progressively rendering it with synchronized explanatory text.

095_vector_fields.tsx - Arrow field visualizations
-Code Description: This code demonstrates a *2D rotational vector field* defined by F(x, y) = (-y, x). It generates arrows across a grid, each representing the local vector’s direction and magnitude, and animates them radiating outward from the center. The accompanying text explains the circular flow pattern around the origin, synchronizing with the vector visualization.
-Function Description: The key function of this code is to *visualize and animate a rotational vector field, where arrows dynamically depict the circular flow created by *F(x, y) = (-y, x), helping illustrate how vectors rotate around the origin.

096_matrix_transformations.tsx - Linear algebra visualizations
-Code Description: This file demonstrates how a 2×2 matrix transforms a 2D vector, showing both the geometric effect on the vector in a coordinate plane and the step-by-step matrix multiplication on the algebraic side. It synchronizes the visualization of original and transformed vectors with the calculation steps, making the relationship between geometry and algebra explicit.
-Function Description: The key logic lies in applying the matrix transformation using applyMatrix, which computes the new coordinates of the vector after multiplication. This result drives both the visualization of the transformed vector and the algebraic breakdown of the calculation, keeping the math and geometry consistent.

097_fourier_series.tsx - Sine wave decomposition
-Code Description: This file demonstrates the Fourier series approximation of a square wave using sine wave harmonics. It progressively shows how adding more odd harmonic terms improves the approximation, starting with a single sine wave and gradually approaching the shape of a square wave. The animation reveals the step-by-step buildup of the waveform.
-Function Description: The core logic lies in the fourierSquareWave function, which calculates the Fourier series approximation by summing odd sine harmonics. This function provides the mathematical foundation for generating the plotted points, and the generatePoints utility applies it to sample data for visualization of partial sums with increasing harmonic counts.

098_fractal_generation.tsx - Mandelbrot, Julia sets
-Code Description: This code generates and animates a Julia set fractal using iterative complex dynamics. It computes each pixel’s value through repeated iteration of a quadratic function and assigns colors based on iteration counts, producing a vivid fractal visualization. The animation progressively reveals the fractal, zooms and rotates it, and finally fades it out.
-Function Description: The key function in this file is the *Julia set calculation (juliaSet)*, which determines whether a point in the complex plane belongs to the Julia set. By iteratively applying the recurrence relation $z_{{n+1}} = z_n^2 + c$, it calculates how quickly points diverge. This divergence rate directly controls the coloring of the fractal, making it the central logic behind generating the fractal image.

100_calculus_visualization.tsx - Derivatives, integrals
-Code Description: This file visualizes the function $y = x^2$, its derivative, and its integral through animations. It first plots the parabola, then shows a moving point with its tangent line and slope to illustrate the derivative. Finally, it highlights the integral as the shaded area under the curve between two bounds, helping convey the relationship between the function, its slope, and the accumulated area.
-Function Description:
The key code lies in the *mathematical definitions of the function and its derivative/integral*. Specifically, F(x) = x * x defines the parabola, F_PRIME(x) = 2 * x computes the slope for tangent visualization, and the integral is shown by constructing a polygon that fills the area under the curve. These expressions drive the entire animation, as they generate the curve, determine tangent behavior, and calculate the shaded integral region.

101_statistics_charts.tsx - Bar charts, histograms, scatter plots
-Code Description: This file demonstrates animated visualizations of three different chart types: a bar chart, a histogram, and a scatter plot. Each chart is introduced sequentially with smooth transitions—bars growing into place, labels appearing, and scatter points expanding—before fading out to transition to the next visualization. It serves as a comparative showcase of how different datasets can be represented visually.
-Function Description: The key code is the *animated construction of data visualizations*. For the bar chart, bar heights and labels are animated based on given values; the histogram uses frequency counts to generate proportional bars; and the scatter plot maps data points to coordinates within a frame. Together, these sequences highlight how different chart types visually represent quantitative data.

102_probability_distributions.tsx - Bell curves, distributions
-Code Description: This file creates an animated visualization of the normal distribution (bell curve). It generates the probability density function values for a specified mean and standard deviation, then plots the curve point by point. A marker moves smoothly along the curve while displaying its current coordinates, providing an interactive way to observe the shape and properties of the distribution.
-Function Description: The key code is the *normalDistribution function and curve generation*, which compute probability density values across a range of x-values and map them into drawable points. These points form the bell curve, which is then animated with a marker that traverses the curve, dynamically showing the relationship between input values and their corresponding probability densities.

103_complex_numbers.tsx - Complex plane visualizations
-Code Description: This code creates a 2D animated visualization to represent a complex number on the complex plane. It defines the real and imaginary axes, labels them, plots a complex number as a point, attaches its textual representation, and then animates a vector from the origin to that point, making the concept of complex numbers more intuitive.
-Function Description: The key function of this code is to *graphically demonstrate a complex number on the complex plane*, showing both its position as a point and its connection to the origin through a vector.


104_trigonometric_functions.tsx - Sin, cos, tan visualizations
-Code Description: This code generates an animated scene that sequentially visualizes the three main trigonometric functions—sine, cosine, and tangent—on a coordinate plane. It dynamically plots each function, labels it, and transitions between them to highlight their individual behavior over a defined range.
-Function Description: The key functionality lies in the progressive drawing of the trigonometric curves (yield* line().end(...)), where each function is animated onto the graph one at a time with its corresponding label, while the previous function is removed. This emphasizes the unique nature of sine, cosine, and tangent through focused step-by-step visualization.

105_number_theory.tsx - Prime spirals, number patterns
-Code Description: This code generates an animated visualization of the prime number spiral, where integers are arranged in a spiral pattern and prime numbers are highlighted. It calculates prime numbers, places them at their respective spiral coordinates, and animates their appearance alongside a connecting line to reveal the prime number distribution.
-Function Description: The key function of this code is to *visualize prime numbers within a spiral pattern*, animating their positions as points and connecting them to display the overall structure of prime distribution.



OUTPUT FORMAT (JSON only):
{{
  "selected_examples": ["001_basic_scene_setup.tsx", "015_reference_creation.tsx", "002_simple_rectangle.tsx", "004_basic_text.tsx", "005_color_basics.tsx", "006_opacity_control.tsx"]
}}

Remember: Select generously! Include all relevant examples that could help implement any aspect of the scene. Maximum 15 examples.
```

</details>

### 3. CodeGeneratorAgent: The Engineer

-   **Script:** `scripts/code_generator.py`
-   **Role:** To act as the "Engineer" of the pipeline. This is the workhorse agent responsible for writing the actual TypeScript (`.tsx`) code for the Motion Canvas animation. It takes the JSON blueprint from the `SceneDescriptorAgent` and the code examples from the `ContextAgent` and synthesizes them into a compilable and renderable animation scene.

#### Prompt Analysis

The `CodeGeneratorAgent` uses two distinct, highly detailed prompts depending on its task: initial generation or debugging.

##### `CODE_GENERATION_PROMPT` (Initial Generation)

This prompt is used to generate the code for a scene from scratch.

*   **Persona:** "Expert Motion Canvas Layout Engineer, Visual Choreographer, and Code Generator."
*   **Mandatory Rules:** The prompt is filled with strict, mandatory instructions, using keywords like "CRITICAL," "MUST," and "MANDATORY" to emphasize their importance.
*   **Visualization Framework Library:** This is a key feature. The prompt contains a hard-coded "library" of layout rules for specific visual metaphors (e.g., "a container being filled," "an indexed list," "connected nodes"). This forces the AI to use pre-defined, consistent calculations for coordinates and layouts instead of "magic numbers," which is crucial for maintaining visual consistency.
*   **Animation Blueprint:** The prompt dictates the exact, step-by-step structure of the generated code, from staging the scene and declaring references to choreographing the animation and handling the conclusion. This ensures all generated files have a similar, predictable structure.
*   **Content Injection Rules:** It provides strict instructions on how to extract text and values from the input JSON, preventing the AI from hallucinating placeholder content.

<details>
<summary>Click to view the full `CODE_GENERATION_PROMPT`</summary>

```
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

### **TEXT LAYOUT AND WRAPPING RULES (MANDATORY)**
1.  **Zone Enforcement**: All text elements **MUST** be placed in the Writing Zone (`x > -192`). A standard starting position is `x: 300`.
2.  **Content Generation (CRITICAL)**: Beyond the scene title and description, you **MUST** generate additional textual content for the Writing Zone. This content should be derived from the `actions` and `explanations` (if present) in the `json_data`, providing detailed explanations that synchronize with the visual animations. Aim for comprehensive, educational text.
3.  **Vertical Layout**: To prevent text blocks from overlapping, you **MUST** wrap them in a `<Layout layout direction={{"column"}} gap={{30}} />` component. This automatically handles vertical spacing.
4.  **Text Wrapping**: Long strings of text **MUST** be manually wrapped by inserting `\n` characters. A line should not exceed 60-70 characters to ensure it fits within the Writing Zone.

---

### **THE ANIMATION BLUEPRINT (MANDATORY)**
You **MUST** construct the `makeScene2D` generator function by following this exact, step-by-step blueprint.

#### **STEP 1: STAGING THE SCENE**
1.  **Background**: Add the white background.
2.  **Reference Declaration**: Create `createRef` variables for every `id` in the JSON's `elements`, `actions` and `explanations`. **Additionally, create `createRef` variables for the scene title and scene description.**
3.  **Calculate Positions**: **Before writing any JSX**, perform all necessary coordinate calculations based on the specified `visual_metaphor` from the library above. Store these calculated positions in variables.
    *   **Scene Title Position**: `x: 300`, `y: -450` (top of Writing Zone)
    *   **Scene Description Position**: `x: 300`, `y: -380` (below title, with a gap)
4.  **Initial Composition**: Add all elements to the scene using `view.add()`. Every element **MUST** be created with `opacity={{0}}` and positioned using your calculated coordinates. **Ensure the scene title and description are added here.** **Crucially, ensure all visual elements (Rect, Circle, Line, etc.) derived from `scene_data.elements` are created and placed within the Visualization Zone (left 40%).**

#### **STEP 2: CHOREOGRAPHING THE ANIMATION**
1.  **Initial Scene Introduction**: At the very beginning of the scene, animate the `scene_title` and `scene_description` fading in.
    *   `scene_title` styling: `fontSize: 60`, `fontWeight: 700`, `fill: '#333'`
    *   `scene_description` styling: `fontSize: 36`, `fill: '#555'`
    *   Ensure no text overlap.
2.  **Follow the Actions & Explanations (CRITICAL)**: Iterate through the `actions` array from the JSON. Each action corresponds to an animation block. **Crucially, for each action, you MUST also identify and animate its corresponding explanation text from the `explanations` array (if present in the JSON).**
3.  **Synchronize Visuals and Text**: For each action (e.g., `CREATE_NODE`), create a `yield* all(...)` block. Inside this block, animate the visual element (e.g., the node appearing) AND its corresponding explanation text (from the `explanations` array) fading in. **Ensure the text appears in the Writing Zone (right 60%) and is synchronized with the visual animation.**
4.  **Pace for Clarity**: After each `yield* all(...)` block, you **MUST** add a `yield* waitFor(1);` to create a deliberate pause.

#### **STEP 3: SCENE CONCLUSION**
1.  **Final Wait**: The last line **MUST** be `yield* waitFor(duration);` using the scene `duration` from the JSON.

### OUTPUT INSTRUCTIONS
- Generate ONLY the raw TypeScript code.
- You **MUST** strictly follow the blueprint and use the Visualization Framework Library for all layout calculations.
- The resulting code must produce a precisely calculated, well-paced, and narratively coherent animation.
```

</details>

##### `ERROR_ANALYSIS_PROMPT` (Debugging)

This prompt is used when a previously generated scene has failed compilation or validation.

*   **Persona:** "Expert Motion Canvas v3.17.29 debugger."
*   **Contextual Inputs:** The prompt is provided with a rich set of inputs for debugging: the original scene description, the faulty code, the specific error messages, and the validation feedback.
*   **Critical Debugging Checklist:** It provides a detailed checklist for the AI to follow, forcing it to address all reported issues, check for common logical errors (like using `null` references), and adhere to the specific Motion Canvas API version.
*   **Self-Correction:** The prompt explicitly tells the AI to review its previous attempt and identify the root cause of the failure, instructing it not to repeat the same mistakes. This is a key part of the pipeline's self-correction capability.

<details>
<summary>Click to view the full `ERROR_ANALYSIS_PROMPT`</summary>

```
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
   - **MANDATORY**: Every element created with `createRef()` **MUST** be added to the scene via `view.add()` *before* any of its animation `yield` calls. Animating a ref that isn't in the scene graph is a critical error.
   - **REFERENCES**: Ensure no animations are attempted on `null` or `undefined` references.

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
```

</details>

### 4. ValidationAgent: The Quality Inspector

-   **Script:** `scripts/validation_agent.py`
-   **Role:** To act as the "Quality Inspector" for the pipeline. This agent is responsible for the final and most critical step: validating that the rendered video meets a high standard of quality. It analyzes the final `.mp4` video file and compares it against the original scene blueprint and a strict quality rubric.

#### Prompt Analysis

The `ValidationAgent`'s prompt is designed to make the AI a meticulous and uncompromising quality assurance expert.

*   **Persona:** "COMPREHENSIVE Educational Video Quality Inspector with STRICT standards."
*   **Multi-Modal Input:** This agent uses a multi-modal prompt, providing the AI with not just the scene data and generated code, but also the rendered **video file** itself for analysis.
*   **Mandatory Validation Criteria:** The prompt contains an exhaustive checklist of criteria that the video *must* pass to be considered valid. This includes the strict 40/60 layout, text readability, visual content standards, animation timing, and technical quality.
*   **Structured Feedback Output:** The prompt requires the AI to output its feedback in a detailed JSON format. This structured data includes a boolean `valid` flag, a breakdown of scores for different quality categories, a list of specific issues with severity levels (`critical`, `major`, `minor`), and concrete suggestions for how to fix the code. This structured feedback is essential for the pipeline's self-correction loop.

<details>
<summary>Click to view the full `VALIDATION_PROMPT`</summary>

```
You are a COMPREHENSIVE Educational Video Quality Inspector with STRICT standards for visual layout, readability, and educational effectiveness.

SCENE SPECIFICATION:
```json
{json.dumps(scene_data, indent=2)}
```

CODE GENERATION RULES & STANDARDS:
```
{formatted_code_gen_prompt[:2500]}
```

REFERENCE EXAMPLES:
```typescript
{code_examples[:2000]}
```

IMPLEMENTATION CODE:
```typescript
{generated_code[:3500]}
```

REPORTED ERRORS: {error_text}

MANDATORY VALIDATION CRITERIA (ALL must pass for VALID rating):

1. **STRICT LAYOUT REQUIREMENTS:**
- LEFT 40%: Visual content ONLY (diagrams, charts, graphs, shapes, mathematical figures)
- RIGHT 60%: Text content ONLY (explanations, equations, bullet points)
- NO cross-boundary violations - visuals must stay left, text must stay right
- Clear visual separation between left and right sections
- Proper aspect ratio utilization (1920x1080 canvas)

2. **TEXT READABILITY & FORMATTING (CRITICAL):**
- ALL text MUST fit strictly within the right 60% boundary. Any overflow, cutoff, or text extending into the visual (left) area is a CRITICAL FAILURE.
- Text MUST wrap appropriately within its designated area. Lack of wrapping leading to unreadability is a CRITICAL FAILURE.
- NO text overlapping with ANY other text elements. This is a CRITICAL FAILURE.
- NO text overlapping with ANY visual elements. This is a CRITICAL FAILURE.
- Proper line spacing and paragraph breaks are MANDATORY for readability.
- Font sizes MUST be appropriate for readability (minimum 24px for body text).
- Consistent text hierarchy (titles, subtitles, body text) is required.

3. **VISUAL CONTENT STANDARDS (CRITICAL):**
- ALL visual elements MUST be positioned strictly within the left 40% boundary. Any visual element extending into the text (right) area is a CRITICAL FAILURE.
- NO visual elements overlapping text areas. This is a CRITICAL FAILURE.
- Mathematical figures, curves, graphs MUST be properly oriented (not inverted/flipped). Incorrect orientation is a CRITICAL FAILURE.
- Clear visual hierarchy and organization are MANDATORY.
- Proper scaling and proportions are required.
- No visual elements cut off or extending beyond canvas boundaries.

3.5. **LABELING & ANNOTATION (CRITICAL):**
- All significant visual elements MUST have clear, readable labels or annotations.
- Labels must be correctly positioned relative to their elements, not overlap other elements, and be visible throughout the relevant animation segment.
- Labels MUST be distinct from the main explanation text and clearly associated with their visual element.

3.6. **ANIMATION DETAIL & PRECISION (CRITICAL):**
- Animations must be descriptive and precise, clearly illustrating the concept.
- This includes using appropriate easing, showing intermediate states, and employing visual cues (e.g., highlights, temporary lines) to enhance understanding.
- Animations should not be overly simplistic if the concept allows for more detail and clarity.

4. **CONTENT COMPLETENESS:**
- ALL elements from scene description must be present and visible
- Proper text-visual synchronization as specified in code generation rules
- Educational narrative flows logically from visual to text
- No missing critical components (equations, diagrams, explanations)

5. **ANIMATION & TIMING:**
- Animation sequences follow logical educational progression
- Reasonable timing (not too fast to comprehend, not too slow to engage)
- Smooth transitions between elements
- Proper reveal sequences for educational content

6. **TECHNICAL QUALITY:**
- No rendering artifacts or visual glitches
- Proper color contrast for readability
- Clean, professional appearance
- No element positioning errors

DETAILED VALIDATION CHECKLIST:

**LAYOUT COMPLIANCE:**
- [ ] Visual content strictly within left 40% (x < 384px for 1920px width)
- [ ] Text content strictly within right 60% (x > 384px for 1920px width)
- [ ] No boundary violations or cross-contamination
- [ ] Proper utilization of allocated space

**TEXT QUALITY:**
- [ ] All text readable without overlapping
- [ ] Proper text wrapping within right boundary
- [ ] Adequate spacing between text elements
- [ ] Consistent font sizing and hierarchy
- [ ] No text cutoff or overflow issues

**VISUAL QUALITY:**
- [ ] All diagrams/charts properly positioned left
- [ ] Mathematical figures correctly oriented
- [ ] Clear visual-text separation
- [ ] Proper scaling and proportions
- [ ] No visual elements overlapping text

**LABELING & ANNOTATION QUALITY:**
- [ ] All significant visual elements have clear, readable labels/annotations
- [ ] Labels are correctly positioned and do not overlap
- [ ] Labels are distinct and clearly associated with their elements

**ANIMATION DETAIL & PRECISION:**
- [ ] Animations are descriptive and precise
- [ ] Appropriate easing and intermediate states are used
- [ ] Visual cues enhance understanding
- [ ] Animations are not overly simplistic

**CONTENT VERIFICATION:**
- [ ] All scene description elements present
- [ ] Proper educational flow and narrative
- [ ] Text-visual synchronization working
- [ ] Complete message conveyance

**ANIMATION ASSESSMENT:**
- [ ] Logical sequence and timing
- [ ] Educational effectiveness maintained
- [ ] Smooth, professional transitions

SEVERITY CLASSIFICATION:
- **CRITICAL**: Prevents message understanding (missing content, severe overlaps, boundary violations)
- **MAJOR**: Impacts readability/usability (text overlaps, poor spacing, misaligned elements)
- **MINOR**: Aesthetic issues that don't impact function (minor positioning variations)

REQUIRED OUTPUT FORMAT:

**VALIDATION RESULT:** [PASS/FAIL]

**LAYOUT COMPLIANCE ASSESSMENT:**
[Detailed check of 40/60 division adherence - mark FAIL if any violations]

**TEXT READABILITY ANALYSIS:**
[Check for overlapping, wrapping, spacing issues - mark FAIL if any found]

**VISUAL POSITIONING VERIFICATION:**
[Verify all visuals in left 40%, properly oriented - mark FAIL if violations]

**CONTENT COMPLETENESS CHECK:**
[All scene description elements present and properly positioned - mark FAIL if missing elements]

**ANIMATION & FLOW EVALUATION:**
[Educational effectiveness and timing assessment]

**OVERALL EDUCATIONAL EFFECTIVENESS:** [Score 1-10]

**DETAILED JSON SUMMARY:**
```json
{{
"valid": true,
"layout_compliance": {{
    "left_visual_boundary": true,
    "right_text_boundary": true,
    "proper_separation": true,
    "space_utilization": true
}},
"text_quality": {{
    "no_overlapping": true,
    "proper_wrapping": true,
    "adequate_spacing": true,
    "readability": true
}},
"visual_quality": {{
    "proper_positioning": true,
    "correct_orientation": true,
    "no_text_overlap": true,
    "appropriate_scaling": true
}},
"labeling_quality": {{
    "clear_labels": true,
    "correct_positioning": true,
    "no_overlap": true
}},
"animation_detail": {{
    "descriptive_animations": true,
    "appropriate_easing": true,
    "visual_cues_used": true,
    "not_overly_simplistic": true
}},
"issues": [
    {{
    "type": "layout_violation|text_overlap|visual_misplacement|labeling_issue|animation_detail_issue|content_missing|animation_issue|technical_problem",
    "description": "Specific detailed issue description",
    "fix_suggestion": "Concrete fix recommendation",
    "severity": "critical|major|minor",
    "location": "specific element or area affected"
    }}
],
"corrected_scene_description": "Enhanced scene description addressing all issues",
"code_improvement_hints": [
    "Specific technical fixes needed",
    "Layout corrections required",
    "Text positioning improvements",
    "Visual element adjustments"
],
"educational_effectiveness_score": 1-10
}}
```

VALIDATION STANDARDS:
- FAIL if ANY layout boundary violations (40/60 division not respected) are observed.
- FAIL if ANY text overlapping, text wrapping issues, or text readability issues are observed.
- FAIL if ANY visual-text overlaps or visual misplacements (visuals in text area, or vice-versa) are observed.
- FAIL if ANY essential content missing from scene description.
- FAIL if animation timing severely impacts comprehension.
- PASS only when ALL criteria meet professional educational video standards.

Be THOROUGH and PRECISE in identifying issues. The goal is to ensure every video meets high educational and visual standards.

</details>

## The Agent Feedback Loop

A key feature of this pipeline is its ability to self-correct. When the `ValidationAgent` identifies an issue with a generated video, it doesn't just fail; it provides structured feedback that is used to automatically trigger a new attempt. This creates a powerful feedback loop that allows the system to learn from its mistakes and improve the quality of its output.

Here’s how the loop works:

1.  **Feedback Generation**: The `ValidationAgent` fails a scene and produces a detailed JSON feedback report containing specific issues and suggestions.
2.  **Orchestration**: The `run_pipeline.py` script catches the failure and routes the feedback report back to the appropriate agents.
3.  **Scene Plan Refinement**: The `SceneDescriptorAgent` receives the feedback and re-runs its generation process, using the feedback to create a new, improved JSON blueprint that addresses the identified issues.
4.  **Code Correction**: The `CodeGeneratorAgent` enters its debugging mode. It receives the faulty code, the compilation errors, and the validation feedback, and uses its `ERROR_ANALYSIS_PROMPT` to generate a corrected version of the TypeScript code.
5.  **Retry**: The pipeline then re-attempts the compilation and rendering process with the corrected code, effectively learning from its prior mistakes.

## Core Architectural Concepts

Beyond the agent-based workflow, the pipeline is built on two core design principles that ensure the output is both high-quality and consistent.

### The Visualization Framework

To avoid "magic numbers" and ensure that animations are visually consistent and mathematically precise, the `CodeGeneratorAgent` uses a **Visualization Framework**. This is not a formal library, but rather a set of hard-coded layout rules and coordinate systems defined directly within the agent's prompt.

-   **Domain-Specific Templates:** The framework provides templates for different educational domains (e.g., Data Structures, Chemistry, Physics). When a user provides a topic, the pipeline maps it to a specific domain and uses the corresponding template.
-   **Pre-defined Calculations:** For each domain, the framework provides specific calculations for positioning and layout. For example, the `DataStructures` template has rules for how to draw a stack or an array, including the size of the cells and the spacing between them.
-   **Enforced Consistency:** By instructing the `CodeGeneratorAgent` to *always* use the framework for calculations, the pipeline ensures that all animations of a certain type (e.g., all array animations) have the same look and feel, regardless of the specific content.

### The Consistency System

To ensure that a series of independently rendered scenes feel like a single, cohesive video, the pipeline uses a **Consistency System**. This system works by passing a stateful `scene_consistency_data` object from one agent to the next.

-   **Stateful Memory:** This object acts as the pipeline's short-term memory. After each scene is generated, the `CodeGeneratorAgent` automatically extracts key visual information (e.g., colors used, element positions, text styles) and stores it in this object.
-   **Consistency Injection:** Before generating the *next* scene, the `CodeGeneratorAgent`'s prompt is dynamically updated with the information from the `scene_consistency_data` object. This "injects" the context of the previous scene into the prompt for the new scene.
-   **Enforced Cohesion:** This process ensures that the AI is always aware of the visual decisions made in the previous scene. It is instructed to maintain the established color palette, reference the positions of previous elements, and create smooth transitions, resulting in a professional and visually coherent final video.

## How to Run

1.  **Set up the Environment:**
    *   Ensure you have Python 3.12+ and Node.js installed.
    *   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
    *   Install the required Node.js packages:
        ```bash
        npm install
        ```
2.  **Set up your API Key:**
    *   Create a file named `.env` in the `my-animation` directory.
    *   Add your Google AI Studio API key to the file like this:
        ```
        GOOGLE_API_KEY='your-api-key-here'
        ```
3.  **Run the Pipeline:**
    *   Navigate to the `scripts` directory:
        ```bash
        cd motion-canvas/MotionCanvas_Agent/my-animation/scripts
        ```
    *   Execute the `run_pipeline.py` script:
        ```bash
        python run_pipeline.py
        ```
    *   The script will then prompt you to enter an educational topic.

## Project Structure

-   `scripts/`: Contains all the Python agent scripts that form the core of the pipeline.
    -   `run_pipeline.py`: The main orchestrator script.
    -   `scene_descriptor.py`: The "Architect" agent.
    -   `context_agent.py`: The "Librarian" agent.
    -   `code_generator.py`: The "Engineer" agent.
    -   `validation_agent.py`: The "QA Inspector" agent.
-   `src/`: Contains the Motion Canvas source code.
    -   `scenes/`: The directory where the generated TypeScript scene files (`.tsx`) are saved.
    -   `project.ts`: The main Motion Canvas project file, which is automatically updated by the pipeline to include new scenes.
-   `examples/`: A large library of over 100 Motion Canvas code examples that are used by the `ContextAgent` to provide reference patterns to the `CodeGeneratorAgent`.
-   `output/`: The directory where the final rendered `.mp4` video files are saved.
-   `my-animation/reports/`: The directory where the JSON scene plans generated by the `SceneDescriptorAgent` are saved for debugging and review.



## Pipeline Workflow Diagram

<img width="535" height="1078" alt="mermaid-8292025 124932 AM" src="https://github.com/user-attachments/assets/1efce86e-79f1-4bf7-9798-3f8719055838" />
<img width="1703" height="904" alt="mermaid-8282025 33516 PM" src="https://github.com/user-attachments/assets/118c467d-7771-4d17-8cf6-43e2fcec6805" />
<img width="502" height="1078" alt="mermaid-8282025 33348 PM" src="https://github.com/user-attachments/assets/1443db76-68d5-4b30-a1ae-f81697f191be" />
# Audio Feature Branch Documentation

## Overview
The **audio feature** was developed in a dedicated branch as part of an experimental effort.  
The primary objective was to integrate text-to-speech capabilities into the existing pipeline.  

## Implementation Details
- The initial implementation was tested using **Google Cloud Text-to-Speech**, which confirmed that the pipeline works successfully end-to-end.  
- An attempt was made to integrate the **Gemini preview model**, but issues were encountered with **SSML-to-audio conversion**.  
- To validate the pipeline functionality, the team temporarily reverted to **Google Cloud’s text-to-speech service**, which worked as expected.  

## Next Steps Before Integration
- Replace the temporary **Google Cloud integration** with the intended model (Gemini or another provider).  
- No additional pipeline modifications are required — only a model swap.  

## Current Status
The audio pipeline is fully functional.  
The only pending action is replacing the test model with the desired production model before merging into the main branch.  


