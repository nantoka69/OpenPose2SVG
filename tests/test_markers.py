import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_svg_markers():
    renderer = SVGRenderer()
    pose_data = {'canvas_width': 500, 'canvas_height': 500}
    header = renderer._generate_svg_header(pose_data)
    
    print("Generated Header:")
    print(header)
    
    assert '<defs>' in header
    assert '</defs>' in header
    assert 'id="marker_#00ff00"' in header
    assert 'id="marker_#ff0000"' in header
    assert 'id="marker_#0000ff"' in header
    assert 'style="fill:#00ff00;"' in header
    assert 'style="fill:#ff0000;"' in header
    assert 'style="fill:#0000ff;"' in header
    print("\nSVG Marker tests passed successfully!")

if __name__ == "__main__":
    try:
        test_svg_markers()
    except Exception as e:
        print(f"\nTests failed: {e}")
        sys.exit(1)
