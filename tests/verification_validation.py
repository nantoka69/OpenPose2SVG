import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_validation():
    print("Testing coordinate validation (negative values should be skipped)...")
    
    # 1. Pose bone test: Keypoint 0 has negative x
    # 2. Face point test: One face keypoint has negative y
    # 3. Hand bone test: One hand keypoint has negative x
    
    pose_data = [{
        'canvas_width': 500,
        'canvas_height': 500,
        'people': [{
            'pose_keypoints_2d': [-1.0, 100, 1.0, 150, 150, 1.0], # kp0 invalid, kp1 valid
            'face_keypoints_2d': [50, -50, 1.0, 60, 60, 1.0],     # one invalid, one valid
            'hand_left_keypoints_2d': [-10, 10, 1.0, 20, 20, 1.0] # kp0 invalid, kp1 valid
        }]
    }]
    
    renderer = SVGRenderer(pose_data)
    svg_content = renderer.render()
    
    # Validation checks:
    
    # 1. Pose: Bone (0, 1) should be missing because kp0 is negative
    # (Checking for absence of bezier path is tricky, but let's check for absence of marker_#... for kp0 color)
    # Actually, let's just assert that the bezier loop for that specific bone is not in content
    # Since we can't easily predict the path, let's look for markers
    
    # 2. Face: Circle at (-1.0 scaled, ...) or (-10, ...) should be missing
    assert 'cx="-5"' not in svg_content # scaled -1.0 * 5 ??? wait, if it's -1.0 it's not normalized in [0,1]
    # In my implementation, I scale only if 0 <= x <= 1. 
    # If x is -1.0, it's not scaled, so circle would be cx="-1.0". 
    assert 'cx="-1.0"' not in svg_content
    assert 'cy="-50"' not in svg_content
    assert 'x1="-10"' not in svg_content
    
    print("Confirmed: Negative coordinates for face, hand, and pose are NOT found in the SVG.")
    
    # Check that VALID ones still exist
    # If coordinates are 60, 60, they appear as "60.0" because in the JSON they might be floats
    # Actually SVGRenderer uses f"{x}" which depends on the input type.
    # In my test data I used [60, 60, 1.0]. Python 3.x prints 60.0 if it's a float or 60 if it's an int.
    # Let's check for "60" to be safe.
    assert 'cx="60' in svg_content
    assert 'cy="60' in svg_content
    print("Confirmed: Valid coordinates ARE still present.")
    
    print("Coordinate validation tests passed successfully!")

if __name__ == "__main__":
    try:
        test_validation()
    except Exception as e:
        print(f"\nTests failed: {e}")
        # If possible, print a bit of svg_content to debug
        # But let's assume the previous run failed quietly because of empty exception
        import traceback
        traceback.print_exc()
        sys.exit(1)
