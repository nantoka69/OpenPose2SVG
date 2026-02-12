import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.svg_renderer import SVGRenderer

def test_hand_rendering():
    print("Testing hand rendering...")
    # 21 keypoints for a hand (0-20)
    # Each keypoint is [x, y, score]
    hand_kpts = []
    for i in range(21):
        hand_kpts.extend([0.1 + i*0.01, 0.1 + i*0.01, 1.0])
        
    pose_data = [{
        'canvas_width': 500,
        'canvas_height': 500,
        'people': [{
            'hand_left_keypoints_2d': hand_kpts
        }]
    }]
    renderer = SVGRenderer(pose_data)
    svg_content = renderer.render()
    
    # Check for hand_left group
    assert '<g id="hand_left">' in svg_content
    print("Found hand_left group element.")
    
    # Check for lines with markers at both ends
    assert 'marker-start="url(#marker_hand)"' in svg_content
    assert 'marker-end="url(#marker_hand)"' in svg_content
    print("Found markers at start and end of hand lines.")
    
    # Check for some colors (first index i=0, h=0 -> Red #ff0000)
    # Note: colorsys matches the formula i / num_indices
    assert 'stroke="#ff0000"' in svg_content
    print("Found correctly calculated HSV-to-Hex color (Red for first bone).")
    
    print("Hand rendering tests passed successfully!")

if __name__ == "__main__":
    try:
        test_hand_rendering()
    except Exception as e:
        print(f"\nTests failed: {e}")
        sys.exit(1)
