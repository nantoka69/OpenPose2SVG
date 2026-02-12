import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_background_rendering():
    print("Testing black background rendering...")
    pose_data = [{
        'canvas_width': 500,
        'canvas_height': 500,
        'people': []
    }]
    renderer = SVGRenderer(pose_data)
    svg_content = renderer.render()
    
    # Check for background group
    assert '<g id="background">' in svg_content
    print("Found background group element")
    
    # Check for black rectangle with correct dimensions
    assert '<rect width="500" height="500" fill="black" />' in svg_content
    print("Found black rectangle with correct dimensions")
    
    # Check that background is generated after header but before footer
    header_index = svg_content.find('<svg')
    background_index = svg_content.find('<g id="background">')
    footer_index = svg_content.find('</svg>')
    
    assert header_index < background_index < footer_index
    print("Background position is correct (between header and footer)")
    
    print("\nBackground rendering tests passed successfully!")

if __name__ == "__main__":
    try:
        test_background_rendering()
    except Exception as e:
        print(f"\nTests failed: {e}")
        sys.exit(1)
