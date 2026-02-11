import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_svg_renderer():
    # Test 1: OpenPose list format (one entry)
    print("Test 1: OpenPose list format (one entry)")
    pose_data_1 = [{'canvas_width': 500, 'canvas_height': 500}]
    svg_1 = SVGRenderer.render_pose(pose_data_1)
    assert '<svg width="500" height="500"' in svg_1
    print("Test 1 Passed")

    # Test 2: Multiple entries (should use first)
    print("\nTest 2: Multiple entries (should use first)")
    pose_data_2 = [
        {'canvas_width': 800, 'canvas_height': 600},
        {'canvas_width': 100, 'canvas_height': 100}
    ]
    svg_2 = SVGRenderer.render_pose(pose_data_2)
    assert '<svg width="800" height="600"' in svg_2
    print("Test 2 Passed")

    # Test 3: Empty list (should raise exception)
    print("\nTest 3: Empty list")
    pose_data_3 = []
    try:
        SVGRenderer.render_pose(pose_data_3)
        assert False, "Should have raised Exception: No pose data found"
    except Exception as e:
        assert str(e) == "No pose data found"
        print("Test 3 Passed (Caught expected exception)")

if __name__ == "__main__":
    try:
        test_svg_renderer()
        print("\nAll simplified list format tests passed successfully!")
    except Exception as e:
        print(f"\nTests failed: {e}")
        sys.exit(1)
