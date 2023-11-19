from pygame.mixer import Sound
from pathlib import Path
from settings import *
import logging


class SoundManager:
    """Manages importing , configuring and playing of all game sounds."""

    def __init__(self, audio_dir: Path) -> None:
        self.audio_dir = audio_dir
        self.sounds: dict[str, Sound] = self.import_sounds()
        self.set_volume()
        self.play_indefinite("music")

    def import_sounds(self) -> dict[str, Sound]:
        sounds: dict[str, Sound] = {}

        # search for audio files
        supported_formats = ("mp3", "wav")
        glob_patterns = [
            f"{self.audio_dir}/*.{extension}" for extension in supported_formats
        ]
        audio_files: list[Path] = []
        for glob_pattern in glob_patterns:
            audio_files += self.audio_dir.glob(glob_pattern)
        logging.info(f"Found {len(audio_files)} audio files in {self.audio_dir}")

        # load audio files as pygame Sounds
        for audio_file in audio_files:
            sounds[audio_file.stem] = Sound(audio_file)
            logging.info(f"Loaded {audio_file}into audio manager")

        return sounds

    def set_volume(self) -> None:
        for sound_key, sound in self.sounds.items():
            if sound_key in SOUND_VOLUMES.keys():
                logging.info(
                    f"Setting volume of {sound_key} to {SOUND_VOLUMES[sound_key]}"
                )
                sound.set_volume(SOUND_VOLUMES[sound_key])
            else:
                logging.warning(
                    f"The volume of {sound_key} is not set. Using default value 1.0"
                )
                sound.set_volume(1.0)

    def play_once(self, sound_name: str) -> None:
        self.sounds[sound_name].play()

    def play_indefinite(self, sound_name: str) -> None:
        self.sounds[sound_name].play(loops=-1)
