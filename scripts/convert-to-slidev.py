#!/usr/bin/env python3
"""
Convert generated sessions to Slidev format
"""

import json
import re
from pathlib import Path

def convert_to_slidev(session_name, content):
    """Convert session markdown to Slidev format"""
    lines = content.split('\n')
    slides = []
    current_slide = []
    
    # Track sections to split into slides
    for line in lines:
        # New major section becomes a new slide
        if line.startswith('## '):
            if current_slide:
                slides.append(current_slide)
            current_slide = [line.replace('## ', '# ')]
        elif line.startswith('### '):
            # Sub-section - add as bullet point
            current_slide.append(f"## {line.replace('### ', '')}")
        elif line.strip():
            current_slide.append(line)
    
    # Add final slide
    if current_slide:
        slides.append(current_slide)
    
    # Build Slidev markdown
    slidev_content = f"""---
title: {session_name.replace('_', ' ').title()}
---

"""
    
    for i, slide in enumerate(slides[:15]):  # Max 15 slides per session
        slidev_content += '\n'.join(slide) + '\n\n---\n\n'
    
    return slidev_content

def main():
    print("Converting sessions to Slidev format...")
    
    sessions_file = Path("data/generated-sessions.json")
    if not sessions_file.exists():
        print("✗ No sessions found")
        return 1
    
    sessions = json.loads(sessions_file.read_text())
    
    slides_dir = Path("slides")
    slides_dir.mkdir(exist_ok=True)
    
    for session in sessions:
        if not session.get("content"):
            continue
        
        slidev_md = convert_to_slidev(session["name"], session["content"])
        
        slide_file = slides_dir / f"{session['name']}.md"
        with open(slide_file, 'w') as f:
            f.write(slidev_md)
        
        print(f"  ✓ {slide_file.name}")
    
    print(f"\n✓ Created {len(sessions)} Slidev presentations in slides/")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())