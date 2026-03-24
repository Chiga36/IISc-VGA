#!/usr/bin/env python3

"""
Interactive Scene Enhancement System
Allows users to add custom enhancements after successful scene generation.
"""

import os
import json
from typing import Dict, List, Optional, Tuple


class SceneEnhancer:
    """Interactive scene enhancement system with improved UX."""
    
    def __init__(self):
        self.enhancement_history = []
    
    def display_enhancement_menu(self, scene_name: str, video_path: str, scene_data: Dict) -> Tuple[List[str], List[str]]:
        """Display interactive enhancement menu and get user choices."""
        print(f"\n{'='*70}")
        print(f"🎨 SCENE ENHANCEMENT INTERFACE - {scene_name}")
        print(f"{'='*70}")
        print(f"✅ Scene validated successfully!")
        print(f"📁 Video: {os.path.basename(video_path)}")
        print(f"📋 Title: {scene_data.get('scene_title', 'N/A')}")
        print(f"📝 Description: {scene_data.get('scene_description', 'N/A')[:60]}...")
        print()
        print("┌─────────────────────────────────────────────────────────────────┐")
        print("│ ENHANCEMENT OPTIONS:                                           │")
        print("│ • Enter enhancement request (e.g., 'add glowing effect')       │")
        print("│ • Type 'skip' - Accept scene as-is and continue               │")
        print("│ • Type 'quit' - Stop processing remaining scenes              │")
        print("└─────────────────────────────────────────────────────────────────┘")
        print()
        
        while True:
            user_choice = input("🎯 Your choice: ").strip()
            
            if user_choice.lower() == 'skip':
                print("✅ Scene approved - continuing to next scene")
                return [], []
            
            elif user_choice.lower() == 'quit':
                confirm = input("⚠️ Stop entire pipeline? (yes/no): ").strip().lower()
                if confirm in ['yes', 'y']:
                    print("🛑 Pipeline stop requested")
                    return [], ['quit']
                else:
                    print("↩️ Returning to enhancement menu")
                    continue
            
            elif user_choice:
                print(f"\n📝 Enhancement request: '{user_choice}'")
                print(f"⚠️ This will regenerate the scene with your enhancement.")
                confirm = input(f"Apply this enhancement? (y/n): ").strip().lower()
                
                if confirm in ['y', 'yes']:
                    print(f"✅ Enhancement queued for regeneration")
                    return [user_choice], []
                else:
                    print("❌ Enhancement cancelled")
                    continue
            else:
                print("❌ Please enter a valid command")
                continue
    
    def apply_enhancements(self, scene_data: Dict, selected_enhancements: List[str]) -> Dict:
        """
        Apply user enhancement requests using clean, parseable format.
        """
        enhanced_scene = scene_data.copy()
        
        if selected_enhancements:
            original_description = enhanced_scene.get('scene_description', '')
            
            # Use clean, bracketed format that prompt explicitly handles
            enhancement_instructions = "\n\n"
            for idx, enhancement in enumerate(selected_enhancements, 1):
                enhancement_instructions += f"[Enhanced: {enhancement}]\n"
            
            # Append to scene description
            enhanced_scene['scene_description'] = f"{original_description}{enhancement_instructions}"
            
            # Track history
            self.enhancement_history.append({
                'scene_title': scene_data.get('scene_title', 'Unknown'),
                'enhancements': selected_enhancements
            })
            
            print(f"✅ Added {len(selected_enhancements)} enhancement instruction(s)")
            print(f"   Format: [Enhanced: {selected_enhancements[0]}]")
        
        return enhanced_scene

    
    def interactive_scene_enhancement(
        self, 
        scene_data: Dict, 
        scene_name: str, 
        video_path: str
    ) -> Tuple[Dict, bool]:
        """
        Main interactive enhancement workflow.
        
        Returns:
            Tuple[Dict, bool]: (enhanced_scene_data, should_quit_pipeline)
        """
        # Get user input for enhancements
        selected_enhancements, control_flags = self.display_enhancement_menu(
            scene_name, video_path, scene_data
        )
        
        # Check for quit flag
        if 'quit' in control_flags:
            return scene_data, True  # Return original data, quit=True
        
        # Apply enhancements if any selected
        if selected_enhancements:
            print(f"\n🔧 Applying enhancements...")
            enhanced_scene = self.apply_enhancements(scene_data, selected_enhancements)
            
            print("✅ Enhancement request added to scene specification!")
            print(f"🔄 Scene will be regenerated with requested changes")
            print(f"⚡ Validation will restart from scratch")
            
            return enhanced_scene, False  # Return enhanced data, quit=False
        else:
            print(f"\n✅ Scene approved without modifications")
            return scene_data, False  # Return original data, quit=False


if __name__ == "__main__":
    # Test the enhancer
    enhancer = SceneEnhancer()
    test_scene = {
        "scene_title": "Test Scene",
        "scene_description": "Original scene content"
    }
    
    enhanced, quit_flag = enhancer.interactive_scene_enhancement(
        test_scene, "Scene1", "test.mp4"
    )
    
    print(f"\nResult:")
    print(f"Quit: {quit_flag}")
    print(f"Enhanced: {enhanced != test_scene}")
    if enhanced != test_scene:
        print(f"New description: {enhanced['scene_description']}")
