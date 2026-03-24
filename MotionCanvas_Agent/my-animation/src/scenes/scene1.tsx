import {makeScene2D} from '@motion-canvas/2d/lib/scenes';
import {Rect, Circle, Txt, Layout, Line, Latex} from '@motion-canvas/2d/lib/components';
import {all, waitFor, chain} from '@motion-canvas/core/lib/flow';
import {createRef} from '@motion-canvas/core/lib/utils';
import {Vector2, Color} from '@motion-canvas/core/lib/types';
import * as easing from '@motion-canvas/core/lib/tweening';

// UTILITY FUNCTION: MANDATORY for text formatting.
function formatText(text: string): string {
    // Splits sentences at periods for better readability in Motion Canvas.
    return text.replace(/\. /g, '.\n').replace(/\n+/g, '\n').trim();
}

export default makeScene2D(function* (view) {
    // STEP 0: PRE-PROCESS SCENE DATA
    // Extract text content directly from the JSON data.
    const scene_title = "Introduction to Gravity";
    const scene_description = "Gravity is a fundamental force that attracts any two objects with mass.";
    const duration = 8;
    
    // The `scene_description` from the JSON is parsed for enhancement requests.
    // [Enhanced: add a ball] -> A Circle component will be created.
    // [Enhanced: make the ball bounce from top] -> The circle will animate with a bounce.
    // The bracketed text itself is not rendered.

    // STEP 1: STAGING THE SCENE
    // 1. Background
    view.add(<Rect width={1920} height={1080} fill={'#ffffff'} />);

    // 2. Reference Declaration
    const titleRef = createRef<Txt>();
    const descRef = createRef<Txt>();
    const ballRef = createRef<Circle>(); // For the [Enhanced: add a ball] request

    // 3. Calculate Positions (based on mandatory layout rules)
    const titlePosition = { x: 300, y: -300 };
    const descriptionPosition = { x: 300, y: -150 };
    
    // Positions for the visualization element (the ball)
    const ballStartPosition = { x: -550, y: -600 }; // Start above the screen
    const ballEndPosition = { x: -550, y: 250 }; // Final resting position

    // 4. Initial Composition (add all elements with opacity 0)
    view.add(
        <>
            {/* Writing Zone Elements */}
            <Txt
                ref={titleRef}
                text={formatText(scene_title)}
                x={titlePosition.x}
                y={titlePosition.y}
                fontSize={48}
                fontWeight={700}
                fill={'#333'}
                opacity={0}
            />
            <Txt
                ref={descRef}
                text={formatText(scene_description)}
                x={descriptionPosition.x}
                y={descriptionPosition.y}
                fontSize={32}
                fill={'#555'}
                opacity={0}
            />

            {/* Visualization Zone Element (from enhancement request) */}
            <Circle
                ref={ballRef}
                x={ballStartPosition.x}
                y={ballStartPosition.y}
                size={120}
                fill={'#2563EB'}
                stroke={'#1E40AF'}
                lineWidth={6}
                opacity={0}
            />
        </>
    );

    // STEP 2: CHOREOGRAPHING THE ANIMATION
    // Synchronize the visual (bouncing ball) with the text appearance.
    yield* all(
        // Animate the ball dropping from the top with a bounce effect.
        ballRef().opacity(1, 0.5),
        ballRef().position(ballEndPosition, 2, easing.easeOutBounce),

        // Fade in the title and description text.
        titleRef().opacity(1, 1.5),
        descRef().opacity(1, 1.5)
    );

    // Add a deliberate pause for the viewer to absorb the information.
    yield* waitFor(1);

    // STEP 3: SCENE CONCLUSION
    // Wait for the remainder of the specified scene duration.
    const animationTime = 2; // Duration of the bounce animation
    const pauseTime = 1;
    const remainingTime = duration - animationTime - pauseTime;
    yield* waitFor(remainingTime > 0 ? remainingTime : 0);
});