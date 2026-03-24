import {makeScene2D} from '@motion-canvas/2d/lib/scenes';
import {Rect, Circle, Txt, Layout, Line, Latex} from '@motion-canvas/2d/lib/components';
import {all, waitFor, chain} from '@motion-canvas/core/lib/flow';
import {createRef} from '@motion-canvas/core/lib/utils';
import {Vector2, Color} from '@motion-canvas/core/lib/types';
import * as easing from '@motion-canvas/core/lib/tweening';

// UTILITY FUNCTION FOR TEXT FORMATTING
function formatText(text: string): string {
    // Simple sentence splitting for Motion Canvas
    return text.replace(/\. /g, '.\n').replace(/\n+/g, '\n').trim();
}

function cleanDescription(description: string): string {
    // Remove enhancement markers and other metadata
    let cleanText = description;
    cleanText = cleanText.replace(/\[Enhanced:.*?\]/g, '');
    cleanText = cleanText.replace(/--- USER REQUESTED ENHANCEMENTS ---[\s\S]*?--- END ENHANCEMENTS ---/g, '');
    cleanText = cleanText.replace(/\[SYSTEM INSTRUCTION.*?END SYSTEM INSTRUCTION\]/gs, '');
    cleanText = cleanText.replace(/\[INTERNAL NOTE.*?END INTERNAL NOTE\]/gs, '');
    return cleanText.trim();
}


export default makeScene2D(function* (view) {
    // JSON Data Ingestion
    const scene_data = {
      "scene_number": 2,
      "scene_title": "Newton's Law of Universal Gravitation",
      "duration": 12,
      "actions": {
        "visualization": [
          {"command": "create", "type": "circle", "target_id": "object1"},
          {"command": "create", "type": "circle", "target_id": "object2"},
          {"command": "create", "type": "line", "target_id": "distance_line"}
        ],
        "writing": [
          {"command": "create", "type": "text", "target_id": "newton_law", "properties": {"text": "Newton's Law: F = G * (m1 * m2) / r^2"}},
          {"command": "create", "type": "text", "target_id": "law_explanation", "properties": {"text": "F is the force, G is the gravitational constant, m1 and m2 are the masses, and r is the distance."}}
        ]
      },
      "scene_description": "\n\n[Enhanced: add more text]\n"
    };

    // STEP 0: PRE-PROCESS SCENE DATA
    const cleaned_description = cleanDescription(scene_data.scene_description);

    // STEP 1: STAGING THE SCENE
    // Background
    view.add(<Rect fill={'#ffffff'} size={'100%'} />);

    // Reference Declaration
    const titleRef = createRef<Txt>();
    const descRef = createRef<Txt>();
    const formulaRef = createRef<Latex>();
    
    const object1Ref = createRef<Circle>();
    const object2Ref = createRef<Circle>();
    const distanceLineRef = createRef<Line>();

    // Coordinate Calculations
    // Visualization Zone (Left 40%, x < -192)
    const object1Pos = new Vector2(-700, 0);
    const object2Pos = new Vector2(-400, 0);

    // Writing Zone (Right 60%, x > -192)
    const textX = 300;
    const titleY = -300;
    const descY = -150;
    const formulaY = 50;

    // Initial Composition
    view.add(
        <>
            {/* Writing Zone Elements */}
            <Txt
                ref={titleRef}
                text={formatText(scene_data.scene_title)}
                x={textX}
                y={titleY}
                fontSize={48}
                fontWeight={700}
                fill={'#333'}
                opacity={0}
            />
            <Txt
                ref={descRef}
                text={formatText(scene_data.actions.writing[1].properties.text)}
                x={textX}
                y={descY}
                fontSize={32}
                fill={'#555'}
                opacity={0}
                lineHeight={48}
            />
            <Latex
                ref={formulaRef}
                tex="{\\text{Newton's Law: } F = G \\frac{m_1 m_2}{r^2}}"
                x={textX}
                y={formulaY}
                height={60}
                fill={'#333'}
                opacity={0}
            />
            
            {/* Visualization Zone Elements */}
            <Circle
                ref={object1Ref}
                position={object1Pos}
                size={120}
                fill={'#4A90E2'}
                stroke={'#1E3A8A'}
                lineWidth={6}
                opacity={0}
                scale={0}
            />
            <Circle
                ref={object2Ref}
                position={object2Pos}
                size={80}
                fill={'#F5A623'}
                stroke={'#B8860B'}
                lineWidth={6}
                opacity={0}
                scale={0}
            />
            <Line
                ref={distanceLineRef}
                points={[object1Pos, object2Pos]}
                stroke={'#1E293B'}
                lineWidth={8}
                end={0}
            />
        </>
    );

    // STEP 2: CHOREOGRAPHING THE ANIMATION
    yield* waitFor(0.5);

    // Scene Introduction: Fade in the title
    yield* titleRef().opacity(1, 1);
    yield* waitFor(1);

    // Action 1: Create the two objects representing masses
    yield* all(
        object1Ref().opacity(1, 0.5),
        object1Ref().scale(1, 1, easing.easeOutBack),
        object2Ref().opacity(1, 0.5),
        object2Ref().scale(1, 1, easing.easeOutBack)
    );
    yield* waitFor(0.5);

    // Action 2: Draw the line representing the distance 'r'
    yield* distanceLineRef().end(1, 1.5, easing.easeInOutCubic);
    yield* waitFor(1);

    // Action 3: Reveal the formula and its explanation
    yield* all(
        formulaRef().opacity(1, 1.5),
        descRef().opacity(1, 1.5)
    );

    // STEP 3: SCENE CONCLUSION
    yield* waitFor(3);
});