#!/usr/bin/env python3
"""
PROFESSIONAL Motion Canvas Pipeline with Advanced Agent Communication

This pipeline implements a sophisticated multi-agent system for creating
high-quality educational animations with:

1. SCENE DESCRIPTOR AGENT: Creates mathematically precise scene specifications
   with calculated coordinates and professional layout engineering

2. CONTEXT AGENT: Intelligently selects relevant code examples based on
   educational patterns and visual consistency requirements

3. CODE GENERATOR AGENT: Transforms scene specifications into flawless
   TypeScript code with syntax validation and debugging capabilities

4. VALIDATION AGENT: Conducts rigorous quality assurance with detailed
   feedback and corrective recommendations

5. FEEDBACK LOOP: Enables continuous improvement through structured
   communication between all agents

Key improvements:
- Deep thinking prompts for all agents
- Mathematical coordinate precision (60/40 layout)
- Advanced error handling and debugging
- Visual consistency management across scenes
- Professional educational animation standards
"""

import os
import time
import json
from dotenv import load_dotenv

# Import enhanced agent logic
from scene_descriptor import generate_scene_description
from context_agent import get_relevant_examples
from code_generator import CodeGeneratorAgent
from validation_agent import ValidationAgent
from token_tracker import TokenTracker
# from ssml_to_audio import convert_ssml_to_audio

from video_combiner import VideoCombiner


# Load environment variables
load_dotenv()

# --- Enhanced Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# Define all necessary paths
SCENES_DIR = os.path.join(PROJECT_ROOT, "src", "scenes")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
EXAMPLES_DIR = os.path.join(PROJECT_ROOT, "examples")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "my-animation", "reports")

def print_pipeline_header():
    """Print professional pipeline header"""
    print("=" * 80)
    print("🎬 PROFESSIONAL MOTION CANVAS EDUCATIONAL ANIMATION PIPELINE")
    print("=" * 80)
    print("🧠 Deep Thinking Agents  •  📐 Mathematical Precision  •  🎨 Professional Quality")
    print("📊 Scene Analysis  •  🔧 Smart Debugging  •  ✅ Rigorous Validation")
    print("=" * 80)

def validate_environment():
    """Validate that all required dependencies and directories exist"""
    print("\n🔍 VALIDATING PIPELINE ENVIRONMENT...")

    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("   Please set your API key: export GOOGLE_API_KEY='your-key-here'")
        return False

    # Check directories
    required_dirs = [SCENES_DIR, OUTPUT_DIR, EXAMPLES_DIR, REPORTS_DIR]
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✅ Directory ready: {os.path.basename(dir_path)}")

    # Check examples availability
    try:
        example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.tsx')]
        print(f"  ✅ Found {len(example_files)} code examples for reference")
    except Exception as e:
        print(f"  ⚠️ Examples directory issue: {e}")

    print("✅ Environment validation complete")
    return True

# --- Enhanced Main Pipeline Logic ---
if __name__ == "__main__":
    print_pipeline_header()

    # 1. Environment Validation
    if not validate_environment():
        print("\n❌ Environment validation failed. Please fix issues and retry.")
        exit(1)

    # Initialize Token Tracker
    token_tracker = TokenTracker()

    # 2. Initialize Enhanced Agents
    print("\n🤖 INITIALIZING INTELLIGENT AGENTS...")
    code_generator = CodeGeneratorAgent()
    validation_agent = ValidationAgent()
    print("  ✅ Code Generator Agent initialized with advanced debugging")
    print("  ✅ Validation Agent initialized with rigorous QA protocols")

    # 3. Get Educational Topic from User
    print("\n📚 EDUCATIONAL CONTENT SPECIFICATION")
    print("-" * 50)
    user_topic = input("Enter the educational topic for the explainer video: ")
    if not user_topic.strip():
        print("❌ No topic entered. Pipeline terminated.")
        exit(1)

    print(f"🎯 Topic confirmed: '{user_topic}'")
    print("🧠 Engaging deep educational analysis...")

    # 4. SCENE DESCRIPTOR AGENT: Generate Multi-Scene Plan
    print(f"\n{'='*20} SCENE DESCRIPTOR AGENT {'='*20}")
    print("🎯 Mission: Create high-level semantic scene specifications")

    # Initial semantic plan generation
    all_scenes_data = generate_scene_description(user_topic, token_tracker=token_tracker)

    if not all_scenes_data or "error" in all_scenes_data:
        print(f"\n❌ SCENE GENERATION FAILED")
        print(f"Error: {all_scenes_data.get('error', 'Unknown error')}")
        print("Pipeline terminated. Please check your API key and try again.")
        exit(1)

    print(f"✅ SEMANTIC SCENE PLAN GENERATED: {len(all_scenes_data)} scenes")

    # Print token usage after scene descriptor
    print(f"\n🔢 TOKEN USAGE AFTER SCENE DESCRIPTOR:")
    usage = token_tracker.get_agent_total("SceneDescriptor")
    print(f"   Input tokens: {usage['input']} | Output tokens: {usage['output']} | Total: {usage['input'] + usage['output']}")

    # Save the generated plan with enhanced metadata
    try:
        plan_filename = f"{user_topic.replace(' ', '_').lower()}_semantic_plan.json"
        plan_filepath = os.path.join(REPORTS_DIR, plan_filename)

        # Enhanced plan data with metadata
        enhanced_plan = {
            "topic": user_topic,
            "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_scenes": len(all_scenes_data),
            "total_estimated_duration": sum(scene.get('duration', 4.0) for scene in all_scenes_data),
            "pipeline_version": "Professional v3.0", # Updated version
            "scenes": all_scenes_data
        }

        with open(plan_filepath, "w") as f:
            json.dump(enhanced_plan, f, indent=2)
        print(f"📁 Semantic plan saved: {plan_filepath}")
    except Exception as e:
        print(f"⚠️ Plan save warning: {e}")

    # 5. MULTI-AGENT SCENE PROCESSING with Enhanced Communication & User Enhancement Loop
    total_scenes = len(all_scenes_data)
    successful_scenes = 0
    failed_scenes = []

    for i, scene_data in enumerate(all_scenes_data):
        scene_number = i + 1
        scene_name = f"Scene{scene_number}"
        scene_title = scene_data.get('scene_title', 'Untitled Scene')
        
        print(f"\n{'='*60}")
        print(f"🎬 PROCESSING SCENE {scene_number}/{total_scenes}")
        print(f"📋 Title: '{scene_title}'")
        print(f"⏱️ Duration: {scene_data.get('duration', 4.0)}s")
        print(f"🎯 Visual Metaphor: {scene_data.get('visual_metaphor', 'N/A')}")
        print(f"Actions: {len(scene_data.get('actions', []))}")
        print(f"Explanations: {len(scene_data.get('explanations', []))}")
        print(f"{'='*60}")
        
        # CONTEXT AGENT: Enhanced Example Selection
        print(f"\n🔍 CONTEXT AGENT: Intelligent Example Selection")
        selected_examples = get_relevant_examples(scene_data, token_tracker=token_tracker)
        
        if selected_examples and selected_examples.get('selected_files'):
            print(f"   ✅ Selected {len(selected_examples['selected_files'])} optimal examples")
        else:
            print("   ⚠️ No examples selected, using base generation")
        
        # Print token usage after context agent
        print(f"\n🔢 TOKEN USAGE AFTER CONTEXT AGENT (Scene {scene_number}):")
        usage = token_tracker.get_agent_scene("ContextAgent", scene_data.get("scene_title", "UnknownScene"))
        print(f"   Input tokens: {usage['input']} | Output tokens: {usage['output']} | Total: {usage['input'] + usage['output']}")
        
        # ═══════════════════════════════════════════════════════════════════
        # ENHANCED VALIDATION LOOP WITH USER INTERACTION
        # ═══════════════════════════════════════════════════════════════════
        
        max_retries = 3
        current_scene_data = scene_data.copy()  # Working copy for modifications
        user_wants_quit = False
        scene_success = False
        final_video_path = None
        
        while not scene_success and not user_wants_quit:
            print(f"\n🛠️ CODE GENERATOR + VALIDATION: Advanced Processing")
            
            # CODE GENERATION + VALIDATION RETRY LOOP
            for attempt in range(max_retries):
                print(f"   Attempt {attempt + 1}/{max_retries} for Code Generation and Validation...")
                
                success, video_path, errors, validation_feedback = code_generator.process_scene_with_retry(
                    scene_data=current_scene_data,
                    scene_name=scene_name,
                    validation_agent=validation_agent,
                    selected_examples=selected_examples,
                    token_tracker=token_tracker
                )
                
                if success:
                    print(f"\n✅ SCENE {scene_number} VALIDATED SUCCESSFULLY!")
                    print(f"📁 Video: {video_path}")
                    print(f"⭐ Quality: Professional standard achieved")
                    
                    scene_success = True
                    final_video_path = video_path
                    
                    # Print token usage
                    print(f"\n🔢 TOKEN USAGE AFTER CODE GENERATOR + VALIDATION (Scene {scene_number}):")
                    usage = token_tracker.get_agent_scene("CodeGenerator", scene_data.get("scene_title", "UnknownScene"))
                    print(f"   Input tokens: {usage['input']} | Output tokens: {usage['output']} | Total: {usage['input'] + usage['output']}")
                    usage = token_tracker.get_agent_scene("ValidationAgent", scene_data.get("scene_title", "UnknownScene"))
                    print(f"   Validation Input tokens: {usage['input']} | Output tokens: {usage['output']} | Total: {usage['input'] + usage['output']}")
                    
                    break  # Exit retry loop
                
                # Handle validation failure
                if validation_feedback and not validation_feedback.get('valid', True):
                    print("🔁 Validation failed. Refining scene based on feedback.")
                    # The process_scene_with_retry already handles internal retries
                    # If we reach here, all retries exhausted
                else:
                    print("❌ No actionable feedback or unrecoverable error.")
                    break
            
            # ═══════════════════════════════════════════════════════════════════
            # USER ENHANCEMENT INTERFACE (Only after successful validation)
            # ═══════════════════════════════════════════════════════════════════
            
            if scene_success:
                try:
                    from scene_enhancer import SceneEnhancer
                    enhancer = SceneEnhancer()
                    
                    # Show user the successful scene and get enhancement requests
                    enhanced_scene_data, should_quit = enhancer.interactive_scene_enhancement(
                        scene_data=current_scene_data,  # Pass current working data
                        scene_name=scene_name,
                        video_path=final_video_path
                    )
                    
                    # Check if user wants to quit entire pipeline
                    if should_quit:
                        print(f"\n🛑 User requested to stop processing. Completed scenes: {successful_scenes}")
                        user_wants_quit = True
                        break
                    
                    # Check if user requested enhancements
                    if enhanced_scene_data != current_scene_data:
                        print(f"\n🔄 USER REQUESTED ENHANCEMENTS - RESTARTING VALIDATION")
                        print(f"🎨 Applying user modifications to scene specification")
                        
                        # Update current scene data with enhancements
                        current_scene_data = enhanced_scene_data
                        scene_success = False  # Reset to trigger new validation loop
                        
                        print(f"\n{'='*60}")
                        print(f"🔄 RE-GENERATING SCENE {scene_number} WITH ENHANCEMENTS")
                        print(f"{'='*60}")
                        # Loop will continue with new current_scene_data
                    else:
                        print(f"\n✅ User approved scene - No enhancements requested")
                        # scene_success remains True, will exit loop
                        
                except ImportError:
                    print("⚠️ Scene enhancer not available, skipping enhancement")
                    break  # Exit enhancement loop
                except Exception as e:
                    print(f"⚠️ Enhancement error: {e}, using validated scene")
                    break  # Exit enhancement loop
            else:
                # Scene failed after all retries
                print(f"❌ Scene {scene_number} failed after {max_retries} attempts")
                break  # Exit enhancement loop
        
        # ═══════════════════════════════════════════════════════════════════
        # FINAL SCENE STATUS
        # ═══════════════════════════════════════════════════════════════════
        
        if user_wants_quit:
            break  # Exit main scene loop
        
        if scene_success:
            successful_scenes += 1
            print(f"\n🎉 SCENE {scene_number} COMPLETED SUCCESSFULLY!")
            print(f"📁 Final Video: {final_video_path}")
            print(f"🚀 Quality: {'Enhanced by user' if current_scene_data != scene_data else 'Original quality'}")
        else:
            failed_scenes.append({
                "scene_number": scene_number,
                "scene_title": scene_title,
                "errors": errors or ["Unknown processing error"]
            })
            print(f"❌ SCENE {scene_number} FAILED")
            if errors:
                print("   Errors:")
                for error in errors[:3]:
                    print(f"     - {error}")
        
        # Brief pause for system stability
        time.sleep(1)


    # 6. PIPELINE COMPLETION REPORT
    print(f"\n{'='*80}")
    print("🎉 MOTION CANVAS PIPELINE COMPLETION REPORT")
    print(f"{'='*80}")
    print(f"📚 Topic: '{user_topic}'")
    print(f"🎬 Total Scenes Processed: {total_scenes}")
    print(f"✅ Successful Scenes: {successful_scenes}")
    print(f"❌ Failed Scenes: {len(failed_scenes)}")

    if successful_scenes > 0:
        success_rate = (successful_scenes / total_scenes) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"🎥 Videos Available in: {OUTPUT_DIR}")

    if failed_scenes:
        print(f"\n⚠️ FAILED SCENES SUMMARY:")
        for failed in failed_scenes:
            print(f"   Scene {failed['scene_number']}: {failed['scene_title']}")
            print(f"     Primary error: {failed['errors'][0] if failed['errors'] else 'Unknown'}")

    if successful_scenes == total_scenes:
        print(f"\n🏆 PERFECT PIPELINE EXECUTION!")
        print(f"   All scenes generated with professional quality")
        print(f"   Ready for educational deployment")
    elif successful_scenes > 0:
        print(f"\n🎯 PARTIAL SUCCESS ACHIEVED")
        print(f"   {successful_scenes} scenes ready for use")
        print(f"   Consider re-running failed scenes with topic refinement")
    else:
        print(f"\n❌ PIPELINE REQUIRES ATTENTION")
        print(f"   No scenes completed successfully")
        print(f"   Check API connectivity and example availability")

    print(f"{'='*80}")
    print("🎬 Motion Canvas Educational Animation Pipeline Complete")
    print(f"{'='*80}")

    # Print Token Usage Report
    print("\n📊 FINAL TOKEN USAGE REPORT")
    token_tracker.print_report()
    token_tracker.save(os.path.join(REPORTS_DIR, "token_usage.json"))

    # 7. AUTOMATIC SMOOTH VIDEO COMBINATION
    if successful_scenes > 0:
        print(f"\n{'='*60}")
        print("🎬 CREATING FINAL SMOOTH VIDEO")
        print(f"{'='*60}")
        
        try:
            import subprocess
            import datetime
            
            # Find FFmpeg (already configured in your environment)
            ffmpeg_cmd = 'ffmpeg'
            try:
                result = subprocess.run([ffmpeg_cmd, '-version'], capture_output=True, timeout=5)
                if result.returncode != 0:
                    ffmpeg_cmd = r'C:\ffmpeg\bin\ffmpeg.exe'
            except:
                ffmpeg_cmd = r'C:\ffmpeg\bin\ffmpeg.exe'
            
            # Find all scene videos in correct order
            video_files = []
            for i in range(1, successful_scenes + 10):  # Check extra scenes
                video_path = os.path.join(OUTPUT_DIR, f"scene{i}.mp4")
                if os.path.exists(video_path):
                    video_files.append(video_path)
            
            if video_files:
                print(f"🎬 Found {len(video_files)} scene videos to combine")
                
                # Create final output name
                safe_topic = "".join(c for c in user_topic if c.isalnum() or c in (' ', '-', '_')).strip()
                final_output = os.path.join(OUTPUT_DIR, f"{safe_topic}_FINAL.mp4")
                
                # Build FFmpeg command for smooth combination
                if len(video_files) == 1:
                    # Single video - just copy with better encoding
                    cmd = [ffmpeg_cmd, '-y', '-i', video_files[0], '-c:v', 'libx264', '-crf', '18', final_output]
                elif len(video_files) == 2:
                    # Two videos - smooth crossfade
                    cmd = [
                        ffmpeg_cmd, '-y', '-i', video_files[0], '-i', video_files[1],
                        '-filter_complex', '[0:v][1:v]xfade=transition=smoothleft:duration=0.5:offset=7.5[v];[0:a][1:a]acrossfade=duration=0.3[a]',
                        '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', final_output
                    ]
                else:
                    # Multiple videos - create concat file for smooth joining
                    concat_content = ""
                    for video_file in video_files:
                        concat_content += f"file '{video_file.replace(chr(92), '/')}'\n"
                    
                    concat_file_path = os.path.join(OUTPUT_DIR, "temp_concat.txt")
                    with open(concat_file_path, 'w') as f:
                        f.write(concat_content)
                    
                    cmd = [
                        ffmpeg_cmd, '-y', '-f', 'concat', '-safe', '0', '-i', concat_file_path,
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                        '-c:a', 'aac', '-b:a', '192k', final_output
                    ]
                
                print("🔄 Processing final video with smooth transitions...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                # Clean up temp file if it exists
                concat_file_path = os.path.join(OUTPUT_DIR, "temp_concat.txt")
                if os.path.exists(concat_file_path):
                    os.remove(concat_file_path)
                
                if result.returncode == 0 and os.path.exists(final_output):
                    file_size_mb = os.path.getsize(final_output) / (1024 * 1024)
                    print(f"\n🎉 FINAL SMOOTH VIDEO CREATED!")
                    print(f"📁 Location: {os.path.basename(final_output)}")
                    print(f"📊 Size: {file_size_mb:.1f} MB | Scenes: {len(video_files)} | Quality: High (CRF 18)")
                    print(f"🌟 Ready for: YouTube, presentations, teaching!")
                else:
                    print(f"⚠️ Video combination failed: {result.stderr}")
                    print(f"✅ {successful_scenes} individual scene videos available")
            else:
                print("❌ No scene videos found for combination")
                
        except Exception as e:
            print(f"⚠️ Auto-combination error: {e}")
            print(f"✅ {successful_scenes} individual scene videos available in output folder")
    else:
        print("\n⚠️ No successful scenes to combine")
