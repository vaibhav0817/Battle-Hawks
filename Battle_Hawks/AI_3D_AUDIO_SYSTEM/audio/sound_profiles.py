# ==========================================================
# SOUND-SPECIFIC PROCESSING PROFILES
# ==========================================================

SOUND_PROFILES = {

    # ------------------------------------------------------
    # GUNSHOT / GUNFIRE
    # ------------------------------------------------------

    "gunshot": {
        "category": "WEAPON",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 120,
        "high_cut": 9000
    },

    "gunshot, gunfire": {
        "category": "WEAPON",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 120,
        "high_cut": 9000
    },

    "gunfire": {
        "category": "WEAPON",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 120,
        "high_cut": 9000
    },

    "machine gun": {
        "category": "WEAPON",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 120,
        "high_cut": 9000
    },

    # ------------------------------------------------------
    # EXPLOSION
    # ------------------------------------------------------

    "explosion": {
        "category": "BLAST",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 40,
        "high_cut": 10000
    },

    "blast": {
        "category": "BLAST",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 40,
        "high_cut": 10000
    },

    "bomb": {
        "category": "BLAST",
        "action": "PRESERVE_LIMIT",
        "gain_db": 0.0,
        "low_cut": 40,
        "high_cut": 10000
    },

    # ------------------------------------------------------
    # FOOTSTEPS
    # ------------------------------------------------------

    "footstep": {
        "category": "MOVEMENT",
        "action": "ENHANCE",
        "gain_db": 3.0,
        "low_cut": 100,
        "high_cut": 6000
    },

    "footsteps": {
        "category": "MOVEMENT",
        "action": "ENHANCE",
        "gain_db": 3.0,
        "low_cut": 100,
        "high_cut": 6000
    },

    # ------------------------------------------------------
    # SPEECH / COMMUNICATION
    # ------------------------------------------------------

    "speech": {
        "category": "COMMUNICATION",
        "action": "ENHANCE",
        "gain_db": 3.0,
        "low_cut": 150,
        "high_cut": 5000
    },

    "voice": {
        "category": "COMMUNICATION",
        "action": "ENHANCE",
        "gain_db": 3.0,
        "low_cut": 150,
        "high_cut": 5000
    },

    "conversation": {
        "category": "COMMUNICATION",
        "action": "ENHANCE",
        "gain_db": 3.0,
        "low_cut": 150,
        "high_cut": 5000
    },

    # ------------------------------------------------------
    # VEHICLE
    # ------------------------------------------------------

    "vehicle": {
        "category": "MOBILITY",
        "action": "PRESERVE",
        "gain_db": 0.0,
        "low_cut": 70,
        "high_cut": 7000
    },

    "engine": {
        "category": "MOBILITY",
        "action": "PRESERVE",
        "gain_db": 0.0,
        "low_cut": 70,
        "high_cut": 7000
    },

    "car": {
        "category": "MOBILITY",
        "action": "PRESERVE",
        "gain_db": 0.0,
        "low_cut": 70,
        "high_cut": 7000
    },

    "motorcycle": {
        "category": "MOBILITY",
        "action": "PRESERVE",
        "gain_db": 0.0,
        "low_cut": 70,
        "high_cut": 7000
    },

    # ------------------------------------------------------
    # BACKGROUND / NOISE
    # ------------------------------------------------------

    "wind": {
        "category": "BACKGROUND",
        "action": "SUPPRESS",
        "gain_db": -6.0,
        "low_cut": 80,
        "high_cut": 8000
    },

    "wind noise (microphone)": {
        "category": "BACKGROUND",
        "action": "SUPPRESS",
        "gain_db": -6.0,
        "low_cut": 80,
        "high_cut": 8000
    },

    "leaves": {
        "category": "BACKGROUND",
        "action": "SUPPRESS",
        "gain_db": -5.0,
        "low_cut": 100,
        "high_cut": 8000
    },

    "static": {
        "category": "BACKGROUND",
        "action": "SUPPRESS",
        "gain_db": -8.0,
        "low_cut": 100,
        "high_cut": 9000
    }
}


# ==========================================================
# DEFAULT PROFILE
# ==========================================================

DEFAULT_PROFILE = {
    "category": "UNKNOWN",
    "action": "PRESERVE",
    "gain_db": 0.0,
    "low_cut": 80,
    "high_cut": 10000
}


# ==========================================================
# GET PROFILE
# ==========================================================

def get_sound_profile(label):

    label = label.lower().strip()

    # Exact match
    if label in SOUND_PROFILES:

        return SOUND_PROFILES[label]

    # Partial match
    for sound_name, profile in SOUND_PROFILES.items():

        if sound_name in label:

            return profile

    return DEFAULT_PROFILE