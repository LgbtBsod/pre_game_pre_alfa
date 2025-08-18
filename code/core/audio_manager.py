import pygame
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from enum import Enum
from .resource_manager import ResourceManager, ResourceType

class AudioType(Enum):
    """Audio type constants"""
    MUSIC = "music"
    SOUND = "sound"
    AMBIENT = "ambient"

class AudioManager:
    """Enhanced audio management system"""
    
    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._music_tracks: Dict[str, str] = {}
        self._current_music: Optional[str] = None
        self._music_volume = 0.7
        self._sound_volume = 0.8
        self._master_volume = 1.0
        self._is_muted = False
        self._is_paused = False
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"Warning: Could not initialize audio mixer: {e}")
    
    def load_sound(self, name: str, file_path: str) -> bool:
        """Load a sound effect"""
        try:
            sound = self.resource_manager.load_sound(file_path)
            if sound:
                self._sounds[name] = sound
                return True
            return False
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return False
    
    def load_music(self, name: str, file_path: str) -> bool:
        """Load a music track"""
        try:
            # For music, we just store the path since pygame.mixer.music handles it
            if self.resource_manager._normalize_path(file_path).exists():
                self._music_tracks[name] = file_path
                return True
            return False
        except Exception as e:
            print(f"Error loading music {name}: {e}")
            return False
    
    def load_audio_folder(self, folder_path: str, audio_type: AudioType = AudioType.SOUND) -> int:
        """Load all audio files from a folder"""
        loaded_count = 0
        
        try:
            full_path = self.resource_manager._normalize_path(folder_path)
            if not full_path.exists() or not full_path.is_dir():
                return 0
            
            for file_path in full_path.iterdir():
                if file_path.is_file():
                    file_name = file_path.stem
                    relative_path = str(file_path.relative_to(self.resource_manager.base_path))
                    
                    if audio_type == AudioType.MUSIC:
                        if self.load_music(file_name, relative_path):
                            loaded_count += 1
                    else:
                        if self.load_sound(file_name, relative_path):
                            loaded_count += 1
            
            return loaded_count
        except Exception as e:
            print(f"Error loading audio folder {folder_path}: {e}")
            return 0
    
    def play_sound(self, name: str, volume: Optional[float] = None) -> bool:
        """Play a sound effect"""
        try:
            if name in self._sounds:
                sound = self._sounds[name]
                if volume is not None:
                    sound.set_volume(volume * self._master_volume * self._sound_volume)
                else:
                    sound.set_volume(self._master_volume * self._sound_volume)
                
                if not self._is_muted:
                    sound.play()
                return True
            return False
        except Exception as e:
            print(f"Error playing sound {name}: {e}")
            return False
    
    def play_music(self, name: str, loops: int = -1, fade_ms: int = 0) -> bool:
        """Play background music"""
        try:
            if name in self._music_tracks:
                file_path = self._music_tracks[name]
                full_path = self.resource_manager._normalize_path(file_path)
                
                if full_path.exists():
                    pygame.mixer.music.load(str(full_path))
                    pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
                    
                    if fade_ms > 0:
                        pygame.mixer.music.play(loops, fade_ms=fade_ms)
                    else:
                        pygame.mixer.music.play(loops)
                    
                    self._current_music = name
                    self._is_paused = False
                    return True
            return False
        except Exception as e:
            print(f"Error playing music {name}: {e}")
            return False
    
    def stop_music(self, fade_ms: int = 0) -> None:
        """Stop background music"""
        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            self._current_music = None
            self._is_paused = False
        except Exception as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self) -> None:
        """Pause background music"""
        try:
            if self._current_music and not self._is_paused:
                pygame.mixer.music.pause()
                self._is_paused = True
        except Exception as e:
            print(f"Error pausing music: {e}")
    
    def unpause_music(self) -> None:
        """Unpause background music"""
        try:
            if self._current_music and self._is_paused:
                pygame.mixer.music.unpause()
                self._is_paused = False
        except Exception as e:
            print(f"Error unpausing music: {e}")
    
    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        self._master_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)"""
        self._music_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
    
    def set_sound_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)"""
        self._sound_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
    
    def _update_volumes(self) -> None:
        """Update all audio volumes"""
        try:
            # Update music volume
            if self._current_music:
                pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
            
            # Update sound volumes
            for sound in self._sounds.values():
                sound.set_volume(self._master_volume * self._sound_volume)
        except Exception as e:
            print(f"Error updating volumes: {e}")
    
    def mute(self) -> None:
        """Mute all audio"""
        self._is_muted = True
        try:
            pygame.mixer.music.set_volume(0)
            for sound in self._sounds.values():
                sound.set_volume(0)
        except Exception as e:
            print(f"Error muting audio: {e}")
    
    def unmute(self) -> None:
        """Unmute all audio"""
        self._is_muted = False
        self._update_volumes()
    
    def is_muted(self) -> bool:
        """Check if audio is muted"""
        return self._is_muted
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy() and not self._is_paused
    
    def get_current_music(self) -> Optional[str]:
        """Get the name of currently playing music"""
        return self._current_music
    
    def get_volume_info(self) -> Dict[str, float]:
        """Get current volume levels"""
        return {
            'master': self._master_volume,
            'music': self._music_volume,
            'sound': self._sound_volume
        }
    
    def preload_game_audio(self) -> int:
        """Preload common game audio files"""
        audio_resources = [
            (ResourceType.SOUND, 'audio/attack/claw.wav'),
            (ResourceType.SOUND, 'audio/attack/fireball.wav'),
            (ResourceType.SOUND, 'audio/attack/slash.wav'),
            (ResourceType.SOUND, 'audio/death.wav'),
            (ResourceType.SOUND, 'audio/Fire.wav'),
            (ResourceType.SOUND, 'audio/heal.wav'),
            (ResourceType.SOUND, 'audio/hit.wav'),
            (ResourceType.MUSIC, 'audio/main.ogg'),
            (ResourceType.SOUND, 'audio/sword.wav')
        ]
        
        return self.resource_manager.preload_resources(audio_resources)
    
    def cleanup(self) -> None:
        """Cleanup audio resources"""
        try:
            self.stop_music()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error cleaning up audio: {e}")

# Global audio manager instance
_audio_manager: Optional[AudioManager] = None

def init_audio_manager(resource_manager: ResourceManager) -> AudioManager:
    """Initialize the global audio manager"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager(resource_manager)
    return _audio_manager

def get_audio_manager() -> AudioManager:
    """Get the global audio manager instance"""
    global _audio_manager
    if _audio_manager is None:
        raise RuntimeError("Audio manager not initialized. Call init_audio_manager() first.")
    return _audio_manager
