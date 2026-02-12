import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_face_rendering():
    print("Testing face rendering...")
    pose_data = [{
        'canvas_width': 500,
        'canvas_height': 500,
        'people': [{
            'face_keypoints_2d': [0.1, 0.1, 1.0, 0.2, 0.2, 1.0] # Two keypoints
        }]
    }]
    renderer = SVGRenderer(pose_data)
    svg_content = renderer.render()
    
    # Check for head group
    assert '<g id="head">' in svg_content
    print("Found head group element.")
    
    # Check for white circles
    # Keypoint 1: (0.1, 0.1) -> (50, 50)
    # Keypoint 2: (0.2, 0.2) -> (100, 100)
    assert '<circle cx="50.0" cy="50.0" r="2" style="fill:#ffffff;stroke:none" />' in svg_content
    assert '<circle cx="100.0" cy="100.0" r="2" style="fill:#ffffff;stroke:none" />' in svg_content
    
    print("Found white circles for face keypoints within the head group.")
    print("Face rendering tests passed successfully!")

if __name__ == "__main__":
    try:
        test_face_rendering()
    except Exception as e:
        print(f"\nTests failed: {e}")
        # Print svg content for debugging if it fails
        # print(svg_content) 
        sys.exit(1)
