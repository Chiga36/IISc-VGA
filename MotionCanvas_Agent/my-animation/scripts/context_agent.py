import os
import json
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Assumes the 'examples' folder is in the parent directory ('my-animation/')
EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples'))

# --- Gemini API Configuration ---
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    print(f"Fatal Error configuring Gemini API in Context Agent: {e}")
    exit()

CONTEXT_SELECTION_PROMPT = """
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
"""

# --- JSON Schema for the AI Model's Output ---
JSON_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "selected_examples": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["selected_examples"]
}


def get_relevant_examples(scene_data: Dict, token_tracker = None) -> Optional[Dict]:
    """
    Intelligently select relevant code examples and return their content.

    Args:
        scene_data: A dictionary containing the description for a single scene.
        _previous_scene_info: Optional dictionary with previous scene data (ignored in current implementation).

    Returns:
        A dictionary with selected examples and their content, or None if an error occurs.
    """
    print("  -> Context Agent: Analyzing scene requirements for example selection...")



    # Try with main prompt first, then fallback if needed
    selected_files = _try_gemini_selection(scene_data, use_fallback=False, token_tracker=token_tracker)
    if selected_files is None or len(selected_files) < 3:
        print("  -> Context Agent: Retrying with enhanced fallback...")
        selected_files = _try_gemini_selection(scene_data, use_fallback=True, token_tracker=token_tracker)

    if selected_files is None:
        print("  -> Context Agent: Both attempts failed, using smart fallback...")
        selected_files = _smart_fallback_selection(scene_data)

    # Read the actual content of selected files
    return _read_example_contents(selected_files)


def _try_gemini_selection(scene_data: Dict, use_fallback: bool = False, token_tracker = None) -> Optional[List[str]]:
    """
    Attempt to get example selection from Gemini API with priority-based selection.
    """
    if use_fallback:
        # Simplified fallback prompt focusing on complexity
        prompt = f"""
Select the most COMPLEX and RELEVANT Motion Canvas examples for this scene. Focus on ADVANCED TECHNIQUES.

SCENE TO IMPLEMENT:
Scene Title: {scene_data.get('scene_title', 'Untitled')}
Description: {scene_data.get('scene_description', 'No description')}
Visual Elements: {scene_data.get('visual_elements', [])}
Animations: {scene_data.get('animations', [])}
Colors: {scene_data.get('colors', [])}
Text Content: {scene_data.get('text_content', [])}

PRIORITY SELECTION RULES:
1. **HIGHEST PRIORITY**: Advanced domain-specific examples (Mathematical: 091-105, Typography: 051-060, Complex Animations: 061-90)
2. **MEDIUM PRIORITY**: Sophisticated geometry and styling (016-050)
3. **LOWEST PRIORITY**: Basic examples (001-015) - only if absolutely essential

For mathematical/scientific content → Focus on 091-105
For complex animations → Focus on 061-90
For advanced text effects → Focus on 051-060
For sophisticated visuals → Focus on 016-050

Select 10-15 examples. Prioritize complexity and specialization over basics.

Return JSON format: {{"selected_examples": ["091_function_plotting.tsx", "064_easing_functions.tsx", "066_parallel_animations.tsx"]}}
"""
    else:
        # Use the enhanced priority-based prompt
        prompt = CONTEXT_SELECTION_PROMPT.format(
            scene_data=json.dumps(scene_data, indent=2)
        )

    try:
        # Configure generation for complexity-focused output
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,  # Slightly higher for more creative selection
            top_p=0.9,
            top_k=40,
            max_output_tokens=1500,  # More room for complex selections
            response_mime_type="application/json",
            response_schema=JSON_OUTPUT_SCHEMA
        )

        # Override safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        if not use_fallback:
            print(f"  -> Context Agent: Analyzing for COMPLEX & SPECIALIZED examples...")

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # Track token usage if token_tracker is provided
        if token_tracker:
            try:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                scene_title = scene_data.get("scene_title", "UnknownScene")
                token_tracker.add("ContextAgent", scene_title, input_tokens, output_tokens)
            except AttributeError:
                # Fallback if usage_metadata is not available
                pass

        # Check if the response was blocked or has no valid parts
        if not response.parts or not response.text:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    if not use_fallback:
                        print(f"  -> ERROR: Gemini response blocked with finish_reason: {finish_reason}")
            return None

        # Parse the JSON response
        try:
            response_data = json.loads(response.text)
            selected_examples = response_data.get("selected_examples", [])

            if not selected_examples:
                if not use_fallback:
                    print("  -> WARNING: No examples selected by AI")
                return None

            print(f"  -> Context Agent: Selected {len(selected_examples)} examples (complexity-focused):")
            for example in selected_examples:
                print(f"     • {example}")

            return selected_examples

        except json.JSONDecodeError as e:
            if not use_fallback:
                print(f"  -> ERROR: Failed to parse JSON response: {e}")
                print(f"  -> Raw response: {response.text[:200]}...")
            return None

    except Exception as e:
        error_msg = str(e)
        if not use_fallback:
            print(f"  -> ERROR: Gemini API call failed: {error_msg}")
        return None


def _smart_fallback_selection(scene_data: Dict) -> List[str]:
    """
    Priority-based fallback selection emphasizing complexity and specialization.
    """
    print("  -> Context Agent: Using priority-based smart fallback selection...")

    selected_examples = []
    scene_text = json.dumps(scene_data, default=str).lower()

    # PRIORITY 1: Domain-specific advanced examples
    math_keywords = ['graph', 'plot', 'chart', 'function', 'equation', 'formula', 'mathematical', 'calculus', 'trigonometric', 'statistical', 'data', 'visualization', 'curve', 'distribution', 'matrix', 'vector']
    typography_keywords = ['text', 'font', 'typewriter', 'typing', 'character', 'word', 'paragraph', 'latex', 'mathematical notation', 'rich text', 'formatting']
    animation_keywords = ['complex', 'advanced', 'smooth', 'physics', 'spring', 'elastic', 'bounce', 'particle', 'wave', 'morph', 'transition', 'sequence', 'parallel', 'bezier', 'easing']

    # Mathematical visualization (91-105) - HIGHEST PRIORITY for math content
    math_score = sum(1 for keyword in math_keywords if keyword in scene_text)
    if math_score > 0:
        math_examples = ['091_function_plotting.tsx', '092_parametric_curves.tsx', '101_statistics_charts.tsx',
                        '104_trigonometric_functions.tsx', '096_matrix_transformations.tsx', '095_vector_fields.tsx',
                        '102_probability_distributions.tsx', '103_complex_numbers.tsx']
        # Select based on math intensity
        math_count = min(math_score * 2 + 3, 8)  # 3-8 examples based on math content
        selected_examples.extend(math_examples[:math_count])

    # Advanced typography (51-60) - HIGHEST PRIORITY for text content
    typography_score = sum(1 for keyword in typography_keywords if keyword in scene_text)
    if typography_score > 0:
        typography_examples = ['054_typewriter_effect.tsx', '053_text_animation.tsx', '056_mathematical_notation.tsx',
                              '052_text_styling.tsx', '055_text_along_path.tsx', '057_rich_text_formatting.tsx']
        typography_count = min(typography_score + 2, 6)
        for example in typography_examples[:typography_count]:
            if example not in selected_examples:
                selected_examples.append(example)

    # Advanced animations (61-90) - HIGH PRIORITY for complex animations
    animation_score = sum(1 for keyword in animation_keywords if keyword in scene_text)
    if animation_score > 0:
        animation_examples = ['064_easing_functions.tsx', '066_parallel_animations.tsx', '065_chain_animations.tsx',
                             '068_bounce_effects.tsx', '069_elastic_animations.tsx', '063_bezier_curves.tsx',
                             '071_particle_systems.tsx', '073_morphing_transitions.tsx']
        animation_count = min(animation_score + 3, 8)
        for example in animation_examples[:animation_count]:
            if example not in selected_examples:
                selected_examples.append(example)

    # PRIORITY 2: Advanced geometry and styling (16-50) - if sophisticated visuals needed
    geometry_keywords = ['gradient', 'shadow', 'path', 'polygon', 'morphing', 'complex shapes']
    geometry_score = sum(1 for keyword in geometry_keywords if keyword in scene_text)
    if geometry_score > 0 and len(selected_examples) < 12:
        geometry_examples = ['021_gradient_fills.tsx', '020_path_creation.tsx', '025_shape_morphing.tsx',
                           '023_shadow_effects.tsx', '018_polygon_creation.tsx']
        for example in geometry_examples[:3]:
            if example not in selected_examples:
                selected_examples.append(example)

    # PRIORITY 3: Only add basic examples if we're short and they're essential
    if len(selected_examples) < 8:
        essential_basic = []
        if any(word in scene_text for word in ['scene', 'setup', 'basic']) and '001_basic_scene_setup.tsx' not in selected_examples:
            essential_basic.append('001_basic_scene_setup.tsx')
        if any(word in scene_text for word in ['reference', 'ref', 'animate']) and '015_reference_creation.tsx' not in selected_examples:
            essential_basic.append('015_reference_creation.tsx')

        selected_examples.extend(essential_basic)

    # Ensure we have 10-15 examples, but prioritize advanced ones
    target_count = max(10, min(15, len(selected_examples) + 3))
    if len(selected_examples) < target_count:
        # Fill with most relevant advanced examples
        additional_advanced = ['076_grid_layouts.tsx', '077_flex_layouts.tsx', '081_alignment_systems.tsx']
        for example in additional_advanced:
            if example not in selected_examples and len(selected_examples) < target_count:
                selected_examples.append(example)

    # Limit to 15 max
    selected_examples = selected_examples[:15]

    print(f"  -> Priority-based selection: {len(selected_examples)} examples")
    print(f"     Math focus: {math_score}, Typography focus: {typography_score}, Animation focus: {animation_score}")
    for example in selected_examples:
        print(f"     • {example}")

    return selected_examples


def _read_example_contents(selected_files: List[str]) -> Dict:
    """
    Read the actual content of selected example files.

    Args:
        selected_files: List of selected example filenames

    Returns:
        Dictionary containing filenames, their content, and metadata
    """
    print(f"  -> Context Agent: Reading content from {len(selected_files)} example files...")
    print(selected_files)

    examples_with_content = {
        "selected_files": selected_files,
        "examples": {}
    }

    for filename in selected_files:
        file_path = os.path.join(EXAMPLES_DIR, filename)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                examples_with_content["examples"][filename] = {
                    "content": content,
                    "description": _get_file_description(filename),
                    "path": file_path
                }
                print(f"     • Read {filename} ({len(content)} chars)")
            else:
                print(f"     • WARNING: {filename} not found at {file_path}")
                examples_with_content["examples"][filename] = {
                    "content": "",
                    "description": _get_file_description(filename),
                    "path": file_path,
                    "error": "File not found"
                }

        except Exception as e:
            print(f"     • ERROR reading {filename}: {e}")
            examples_with_content["examples"][filename] = {
                "content": "",
                "description": _get_file_description(filename),
                "path": file_path,
                "error": str(e)
            }

    return examples_with_content


def _get_file_description(filename: str) -> str:
    """
    Get a description for a given example file based on its name.
    """
    descriptions = {
        "001_basic_scene_setup.tsx": "makeScene2D foundation and basic scene structure",
        "002_simple_rectangle.tsx": "Rect component creation and basic properties",
        "003_multiple_shapes.tsx": "Multiple geometry primitives in one scene",
        "004_basic_text.tsx": "Txt component implementation and text properties",
        "005_color_basics.tsx": "Color property configuration and usage",
        "006_opacity_control.tsx": "Opacity animations and fade effects",
        "007_position_setting.tsx": "Coordinate positioning and placement",
        "008_scale_transformations.tsx": "Scale animations and transformations",
        "009_rotation_basics.tsx": "Rotation transforms and spinning effects",
        "010_anchor_points.tsx": "Transform origin points and anchoring",
        "011_parent_child_hierarchy.tsx": "Node hierarchy and nested components",
        "012_view_management.tsx": "Scene graph management and view operations",
        "013_basic_timing.tsx": "Animation timing and waitFor usage",
        "014_generator_functions.tsx": "Generator syntax and yield patterns",
        "015_reference_creation.tsx": "createRef patterns and node references",
        "016_rectangle_variants.tsx": "Rectangle variations and advanced properties",
        "017_circle_animations.tsx": "Circle component usage and animations",
        "018_polygon_creation.tsx": "Polygon geometry and custom shapes",
        "019_line_drawing.tsx": "Line component styling and properties",
        "020_path_creation.tsx": "SVG path creation and complex shapes",
        "021_gradient_fills.tsx": "Gradient configurations and fill patterns",
        "022_border_styling.tsx": "Stroke properties and border styling",
        "023_shadow_effects.tsx": "Shadow rendering and visual effects",
        "024_text_mapping.tsx": "Text texture mapping and advanced text",
        "025_shape_morphing.tsx": "Shape transitions and morphing effects",
        "051_font_loading.tsx": "Custom font usage and font styling",
        "052_text_styling.tsx": "Text styling variations and formatting",
        "053_text_animation.tsx": "Character-by-character text animations",
        "054_typewriter_effect.tsx": "Progressive text typing effects",
        "056_mathematical_notation.tsx": "LaTeX mathematical expressions",
        "061_linear_motion.tsx": "Linear motion and straight-line movement",
        "064_easing_functions.tsx": "Animation easing and timing curves",
        "065_chain_animations.tsx": "Sequential animation chaining",
        "066_parallel_animations.tsx": "Simultaneous parallel animations",
        "068_bounce_effects.tsx": "Spring-like bounce animations",
        "069_elastic_animations.tsx": "Elastic overshoot and settle effects",
        "076_grid_layouts.tsx": "Grid-based layout arrangements",
        "077_flex_layouts.tsx": "Flexible box layout system",
        "081_alignment_systems.tsx": "Element alignment and positioning",
        "091_function_plotting.tsx": "2D function graph visualization",
        "101_statistics_charts.tsx": "Charts, graphs, and data visualization",
    }

    return descriptions.get(filename, f"Motion Canvas example: {filename}")


def format_examples_for_prompt(examples_data: Dict) -> str:
    """
    Format the examples with content for inclusion in AI prompts.

    Args:
        examples_data: Dictionary containing examples with content

    Returns:
        Formatted string ready for inclusion in prompts
    """
    if not examples_data or not examples_data.get("examples"):
        return "No reference examples available."

    formatted_examples = ["REFERENCE CODE EXAMPLES:"]
    formatted_examples.append("Use these as patterns for implementing similar features:\n")

    for filename, data in examples_data["examples"].items():
        if data.get("error"):
            continue

        formatted_examples.append(f"=== {filename} ===")
        formatted_examples.append(f"Purpose: {data['description']}")
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
                content_preview = data["content"][:100].replace('\n', ' ')
                print(f"  - {filename} ({len(data['content'])} chars): {content_preview}...")
    else:
        print("FAILED: No examples retrieved")
