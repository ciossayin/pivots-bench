"""PIVOTSBench evaluation toolkit."""

__version__ = "0.1.0"

DIMENSIONS = ("P", "I", "V", "O", "T", "S")
DIMENSION_NAMES = {
    "P": "Power",
    "I": "Involvement",
    "V": "Valence",
    "O": "Objective",
    "T": "Permanence",
    "S": "Stance",
}
SCALE = (-2, -1, 0, 1, 2)
CUES = {
    "A": "Facial expression",
    "B": "Body posture",
    "C": "Proximity",
    "D": "Body height",
    "E": "Hand gesture",
    "F": "Social norms",
    "G": "Gaze",
    "H": "Context",
    "I": "Attire",
    "J": "Contact",
}
