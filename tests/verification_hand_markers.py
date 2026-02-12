import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_markers_refinement():
    print("Testing side-specific and refined markers...")
    pose_data = [{
        'canvas_width': 500,
        'canvas_height': 500,
        'people': [{
            'hand_left_keypoints_2d': [0.1, 0.1, 1.0, 0.15, 0.15, 1.0],
            'hand_right_keypoints_2d': [0.2, 0.2, 1.0, 0.25, 0.25, 1.0]
        }]
    }]
    renderer = SVGRenderer(pose_data)
    svg_content = renderer.render()
    
    # Check for side-specific hand marker definitions
    assert '<marker id="marker_hand_left"' in svg_content
    # Hand markers: viewBox 5x5, radius 2
    assert 'viewBox="0 0 5 5"' in svg_content
    assert 'r="2"' in svg_content
    print("Found refined dimensions (viewBox 5, r=2) for hand markers.")
    
    # Check for pose bone marker definition (if any colors exist)
    # The first pose bone color is usually #c80000 etc.
    if 'viewBox="0 0 20 20"' in svg_content:
        assert 'r="9"' in svg_content
        print("Found restored dimensions (viewBox 20, r=9) for pose bone markers.")
    
    # Check hand bone lines use correct side-specific markers
    assert 'marker-start="url(#marker_hand_left)"' in svg_content
    assert 'marker-start="url(#marker_hand_right)"' in svg_content
    print("Hand bones use side-specific markers.")
    
    print("Marker differentiation and refinement tests passed successfully!")

if __name__ == "__main__":
    try:
        test_markers_refinement()
    except Exception as e:
        print(f"\nTests failed: {e}")
        sys.exit(1)
