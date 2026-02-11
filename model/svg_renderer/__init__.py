from .renderer import SVGRenderer

def render_pose(pose_json_data):
    """
    Creates a renderer object for the given pose JSON and returns the rendered SVG string.
    
    Args:
        pose_json_data: The parsed OpenPose JSON data.
        
    Returns:
        str: The rendered SVG as a string.
    """
    renderer = SVGRenderer(pose_json_data)
    return renderer.render()
