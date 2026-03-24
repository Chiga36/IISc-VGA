import {{{{makeScene2D}}}} from '@motion-canvas/2d/lib/scenes';
import {{{{Rect, Circle, Txt, Layout, Line, Latex}}}} from '@motion-canvas/2d/lib/components';
import {{{{all, waitFor, chain}}}} from '@motion-canvas/core/lib/flow';
import {{{{createRef}}}} from '@motion-canvas/core/lib/utils';
import {{{{Vector2, Color}}}} from '@motion-canvas/core/lib/types';
import * as easing from '@motion-canvas/core/lib/tweening';

// UTILITY FUNCTION FOR TEXT FORMATTING
// This function MUST be used for all Txt components to ensure proper line breaks.
function formatText(text: string): string {
    // Simple sentence splitting for Motion Canvas
    return text.replace(/\. /g, '.\n').replace(/\n+/g, '\n').trim();
}

export default makeScene2D(function* (view) {
    // Scene data extracted from the input JSON
    const scene_data = {
      "scene_number": 3,
      "scene_title": "Mass and Distance Relationship",
      "duration": 10,
      "actions": {
        "visualization": [
          {
            "command": "modify",
            "type": "circle",
            "target_id": "object1",
            "properties": {
              "placeholder": "string"
            }
          }
        ],
        "writing": [
          {
            "command": "modify",
            "type": "text",
            "target_id": "law_explanation",
            "properties": {
              "text": "Increasing mass increases the force; increasing distance decreases the force."
            }
          }
        ]
      }
    };
    
    // As scene_description is not provided in the JSON, a logical one is created.
    const scene_description = "This scene illustrates how mass and distance influence the gravitational force between two objects, as described by Newton's Law of Universal Gravitation.";

    // STEP 0: PRE-PROCESSING (No enhancement markers to parse in this JSON)
    const cleaned_description = scene_description; // No cleaning needed for this input.
    
    // STEP 1: STAGING THE SCENE
    
    // 1. Background
    view.add(<Rect width={'100%'} height={'100%'} fill={'#ffffff'} />);

    // 2. Reference Declaration
    const titleRef = createRef<Txt>();
    const descRef = createRef<Txt>();
    const lawExplanationRef = createRef<Txt>();
    const newtonLawRef = createRef<Latex>();
    const object1Ref = createRef<Circle>();
    const object2Ref = createRef<Circle>();
    const distanceLineRef = createRef<Line>();
    
    // 3. Calculate Positions
    const object1Pos = new Vector2(-700, 0);
    const object2Pos = new Vector2(-400, 0);
    
    // 4. Initial Composition
    // All elements are added with opacity 0, ready for animation.

    // Visualization Zone (Left 40%)
    view.add(
        <>
            <Circle
                ref={object1Ref}
                position={object1Pos}
                size={100}
                fill={'#369E96'}
                stroke={'#1E293B'}
                lineWidth={6}
                opacity={0}
            />
            <Circle
                ref={object2Ref}
                position={object2Pos}
                size={100}
                fill={'#369E96'}
                stroke={'#1E293B'}
                lineWidth={6}
                opacity={0}
            />
            <Line
                ref={distanceLineRef}
                points={[object1Pos, object2Pos]}
                stroke={'#64748B'}
                lineWidth={8}
                lineDash={[10, 10]}
                end={0} // Start invisible for animation
                opacity={0}
            />
        </>
    );

    // Writing Zone (Right 60%)
    view.add(
        <>
            <Txt
                ref={titleRef}
                text={formatText(scene_data.scene_title)}
                x={300}
                y={-300}
                fontSize={48}
                fontWeight={700}
                fill={'#333'}
                opacity={0}
            />
            <Txt
                ref={descRef}
                text={formatText(cleaned_description)}
                x={300}
                y={-150}
                fontSize={32}
                fill={'#555'}
                opacity={0}
            />
            <Txt
                ref={lawExplanationRef}
                text={formatText(scene_data.actions.writing[0].properties.text)}
                x={300}
                y={50}
                fontSize={24}
                fill={'#666'}
                opacity={0}
            />
            <Latex
                ref={newtonLawRef}
                tex="F = G \frac{m_1 m_2}{r^2}"
                x={300}
                y={200}
                height={60}
                fill={'#1E293B'}
                opacity={0}
            />
        </>
    );

    // STEP 2: CHOREOGRAPHING THE ANIMATION

    // Scene Introduction: Animate in the static context
    yield* all(
        titleRef().opacity(1, 1),
        descRef().opacity(1, 1),
    );
    yield* waitFor(0.5);

    // Bring in the visualization elements and the formula
    yield* all(
        object1Ref().opacity(1, 0.7),
        object2Ref().opacity(1, 0.7),
        distanceLineRef().opacity(1, 0.7),
        newtonLawRef().opacity(1, 1.2)
    );
    
    // Animate the distance line drawing itself
    yield* distanceLineRef().end(1, 1, easing.easeInOutCubic);
    yield* waitFor(1);

    // Main Animation Block from JSON 'actions'
    // Synchronize the visual change (mass increase) with the explanation text
    yield* all(
        object1Ref().size(180, 1.5, easing.easeOutBounce),
        object1Ref().fill('#E11D48', 1.5),
        lawExplanationRef().opacity(1, 1.5)
    );

    // STEP 3: SCENE CONCLUSION
    yield* waitFor(scene_data.duration);
});