class KeyPoint:
    """
    Represents a single pose keypoint with coordinates and a probability score.
    """
    def __init__(self, x: float, y: float, score: float):
        self.x = x
        self.y = y
        self.score = score

    def __repr__(self):
        return f"KeyPoint(x={self.x}, y={self.y}, s={self.score})"
