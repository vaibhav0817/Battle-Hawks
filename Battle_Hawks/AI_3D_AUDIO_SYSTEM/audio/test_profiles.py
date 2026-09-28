from audio.sound_profiles import get_sound_profile


tests = [
    "Gunshot, gunfire",
    "Explosion",
    "Footsteps",
    "Speech",
    "Vehicle",
    "Wind",
    "Unknown sound"
]


print("\n==============================================")
print("           SOUND PROFILE TEST")
print("==============================================\n")


for label in tests:

    profile = get_sound_profile(label)

    print(
        f"{label:<25} | "
        f"{profile['category']:<15} | "
        f"{profile['action']:<15} | "
        f"{profile['gain_db']:+.1f} dB"
    )