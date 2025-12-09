#!/usr/bin/env python3
"""
TALKING ROBOT - Makes your computer SPEAK! 🗣️
You control when it talks!
"""

import os
import sys
import subprocess

def speak(text):
    """Make the computer say something out loud!"""
    # This works on Mac!
    subprocess.run(['say', text])

def main():
    print("=" * 50)
    print("🤖 TALKING ROBOT 🤖")
    print("=" * 50)
    print()
    print("Commands:")
    print("  Type anything - Robot will say it!")
    print("  Type 'stop' or 'quit' - Stop the robot")
    print("  Type 'loud' - Robot talks LOUD!")
    print("  Type 'fast' - Robot talks FAST!")
    print("  Type 'normal' - Back to normal")
    print()
    print("=" * 50)
    print()
    
    mode = "normal"
    
    while True:
        # Get what you want to say
        user_input = input("YOU: ").strip()
        
        # Check for stop command
        if user_input.lower() in ['stop', 'quit', 'exit', 'bye']:
            speak("Goodbye! See you later!")
            print("🤖: Goodbye!")
            break
        
        # Check for mode changes
        if user_input.lower() == 'loud':
            mode = "loud"
            speak("Now I am VERY LOUD!")
            print("🤖: LOUD MODE ON!")
            continue
            
        if user_input.lower() == 'fast':
            mode = "fast"
            speak("Now I talk super fast!")
            print("🤖: FAST MODE ON!")
            continue
            
        if user_input.lower() == 'normal':
            mode = "normal"
            speak("Back to normal!")
            print("🤖: NORMAL MODE!")
            continue
        
        # Make robot talk!
        if user_input:
            print(f"🤖: {user_input}")
            
            if mode == "loud":
                # Louder voice (using a different voice that sounds more commanding)
                subprocess.run(['say', '-v', 'Fred', user_input])
            elif mode == "fast":
                # Faster voice
                subprocess.run(['say', '-r', '300', user_input])
            else:
                # Normal voice
                speak(user_input)
        else:
            print("🤖: (You didn't say anything!)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🤖: Stopped by Control+C!")
        speak("Stopped!")
