import sys
import os
import math

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_bezier_loop():
    renderer = SVGRenderer()
    
    # Test horizontal line: (0,0) to (100,0)
    # dx=100, dy=0, length=100
    # nx = -0/100 = 0, ny = 100/100 = 1
    # ox = 0, oy = 10
    # Forward handles: (0, 10), (100, 10)
    # Return handles: (100, -10), (0, -10)
    x1, y1, x2, y2 = 0, 0, 100, 0
    color = "red"
    svg_path = renderer._SVGRenderer__draw_bezier_loop(x1, y1, x2, y2, color)
    
    print(f"Generated SVG Path: {svg_path}")
    
    assert 'M 0,0' in svg_path
    assert 'style="fill:red;stroke:none"' in svg_path
    assert 'marker-start="url(#marker_red)"' in svg_path
    assert 'marker-mid="url(#marker_red)"' in svg_path
    assert 'marker-end="url(#marker_red)"' in svg_path
    assert 'C 0.0,10.0 100.0,10.0 100,0' in svg_path
    assert 'C 100.0,-10.0 0.0,-10.0 0,0' in svg_path
    print("Horizontal Bezier loop test passed")

    # Test vertical line: (0,0) to (0,100)
    # dx=0, dy=100, length=100
    # nx = -100/100 = -1, ny = 0/100 = 0
    # ox = -10, oy = 0
    # Forward handles: (-10, 0), (-10, 100)
    # Return handles: (10, 100), (10, 0)
    x1, y1, x2, y2 = 0, 0, 0, 100
    color_v = "blue"
    svg_path_v = renderer._SVGRenderer__draw_bezier_loop(x1, y1, x2, y2, color_v)
    print(f"Generated SVG Path (Vertical): {svg_path_v}")
    
    assert 'M 0,0' in svg_path_v
    assert 'style="fill:blue;stroke:none"' in svg_path_v
    assert 'marker-start="url(#marker_blue)"' in svg_path_v
    assert 'marker-mid="url(#marker_blue)"' in svg_path_v
    assert 'marker-end="url(#marker_blue)"' in svg_path_v
    assert 'C -10.0,0.0 -10.0,100.0 0,100' in svg_path_v
    assert 'C 10.0,100.0 10.0,0.0 0,0' in svg_path_v
    print("Vertical Bezier loop test passed")

if __name__ == "__main__":
    try:
        test_bezier_loop()
        print("\nBezier loop rendering tests passed successfully!")
    except Exception as e:
        print(f"\nTests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
