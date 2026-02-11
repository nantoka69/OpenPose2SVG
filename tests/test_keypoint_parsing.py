import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer
from model.keypoints import KeyPoint

def test_keypoint_parsing():
    renderer = SVGRenderer()
    
    # Sample OpenPose JSON data with one person
    pose_json_data = [{
        'canvas_width': 500,
        'canvas_height': 500,
        'people': [{
            'pose_keypoints_2d': [10.0, 20.0, 0.9, 30.0, 40.0, 0.8],
            'face_keypoints_2d': [1.0, 2.0, 0.7],
            'hand_left_keypoints_2d': [],
            'hand_right_keypoints_2d': [5.0, 6.0, 1.0]
        }]
    }]
    
    # We need to access private methods for testing parsing logic
    # or just check if render runs without error and produces valid SVG
    svg = renderer.render(pose_json_data)
    assert '<svg width="500" height="500"' in svg
    assert svg.endswith('</svg>')
    print("SVG rendering test passed (no errors during parsing)")

    # Test private __parse_keypoints directly using name mangling
    person = pose_json_data[0]['people'][0]
    parsed_pose = renderer._SVGRenderer__parse_keypoints(person['pose_keypoints_2d'])
    
    assert len(parsed_pose) == 2
    assert parsed_pose[0].x == 10.0
    assert parsed_pose[0].y == 20.0
    assert parsed_pose[0].score == 0.9
    assert parsed_pose[1].x == 30.0
    assert parsed_pose[1].y == 40.0
    assert parsed_pose[1].score == 0.8
    print("Private __parse_keypoints test passed")

if __name__ == "__main__":
    try:
        test_keypoint_parsing()
        print("\nPose keypoint parsing tests passed successfully!")
    except Exception as e:
        print(f"\nTests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
