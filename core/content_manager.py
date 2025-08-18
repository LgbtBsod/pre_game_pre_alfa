"""
Content Manager for handling game content and data
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from .logger import GameLogger
from .game_data import GameDataManager

class ContentManager:
    """Manages game content and data according to Single Responsibility Principle"""
    
    def __init__(self, game_data_manager: GameDataManager):
        self.game_data_manager = game_data_manager
        self.logger = GameLogger("ContentManager")
        
        # Content storage
        self.content: Dict[str, Any] = {
            'levels': {},
            'items': {},
            'quests': {},
            'dialogue': {},
            'achievements': {},
            'tutorials': {}
        }
        
        # Content paths
        self.content_paths = {
            'levels': 'content/levels',
            'items': 'content/items',
            'quests': 'content/quests',
            'dialogue': 'content/dialogue',
            'achievements': 'content/achievements',
            'tutorials': 'content/tutorials'
        }
        
        # Content validation rules
        self.validation_rules = {
            'levels': ['name', 'map_file', 'entities'],
            'items': ['name', 'type', 'stats'],
            'quests': ['name', 'description', 'objectives'],
            'dialogue': ['id', 'text', 'speaker'],
            'achievements': ['name', 'description', 'condition'],
            'tutorials': ['id', 'title', 'steps']
        }
        
        self.logger.info("Content manager initialized")
    
    def load_all_content(self) -> bool:
        """Load all game content"""
        try:
            success = True
            for content_type in self.content.keys():
                if not self._load_content_type(content_type):
                    success = False
                    self.logger.error(f"Failed to load {content_type} content")
            
            if success:
                self.logger.info("All content loaded successfully")
            else:
                self.logger.warning("Some content failed to load")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error loading content: {e}")
            return False
    
    def _load_content_type(self, content_type: str) -> bool:
        """Load content of a specific type"""
        try:
            content_path = self.content_paths.get(content_type)
            if not content_path or not os.path.exists(content_path):
                self.logger.warning(f"Content path not found: {content_path}")
                return False
            
            content_files = []
            for file in os.listdir(content_path):
                if file.endswith('.json'):
                    content_files.append(os.path.join(content_path, file))
            
            if not content_files:
                self.logger.warning(f"No content files found for {content_type}")
                return False
            
            loaded_content = {}
            for file_path in content_files:
                content_data = self._load_json_file(file_path)
                if content_data and self._validate_content(content_type, content_data):
                    content_id = content_data.get('id', Path(file_path).stem)
                    loaded_content[content_id] = content_data
                    self.logger.debug(f"Loaded {content_type}: {content_id}")
                else:
                    self.logger.warning(f"Invalid content file: {file_path}")
            
            self.content[content_type] = loaded_content
            self.logger.info(f"Loaded {len(loaded_content)} {content_type} items")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading {content_type} content: {e}")
            return False
    
    def _load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {e}")
            return None
    
    def _validate_content(self, content_type: str, content_data: Dict[str, Any]) -> bool:
        """Validate content data"""
        required_fields = self.validation_rules.get(content_type, [])
        
        for field in required_fields:
            if field not in content_data:
                self.logger.warning(f"Missing required field '{field}' in {content_type}")
                return False
        
        return True
    
    def get_content(self, content_type: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get specific content by type and ID"""
        return self.content.get(content_type, {}).get(content_id)
    
    def get_all_content(self, content_type: str) -> Dict[str, Any]:
        """Get all content of a specific type"""
        return self.content.get(content_type, {})
    
    def get_level_data(self, level_id: str) -> Optional[Dict[str, Any]]:
        """Get level data"""
        return self.get_content('levels', level_id)
    
    def get_item_data(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item data"""
        return self.get_content('items', item_id)
    
    def get_quest_data(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get quest data"""
        return self.get_content('quests', quest_id)
    
    def get_dialogue_data(self, dialogue_id: str) -> Optional[Dict[str, Any]]:
        """Get dialogue data"""
        return self.get_content('dialogue', dialogue_id)
    
    def get_achievement_data(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Get achievement data"""
        return self.get_content('achievements', achievement_id)
    
    def get_tutorial_data(self, tutorial_id: str) -> Optional[Dict[str, Any]]:
        """Get tutorial data"""
        return self.get_content('tutorials', tutorial_id)
    
    def create_level_content(self, level_data: Dict[str, Any]) -> bool:
        """Create new level content"""
        try:
            if self._validate_content('levels', level_data):
                level_id = level_data.get('id', level_data.get('name', 'unknown'))
                self.content['levels'][level_id] = level_data
                self.logger.info(f"Created level content: {level_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error creating level content: {e}")
            return False
    
    def create_item_content(self, item_data: Dict[str, Any]) -> bool:
        """Create new item content"""
        try:
            if self._validate_content('items', item_data):
                item_id = item_data.get('id', item_data.get('name', 'unknown'))
                self.content['items'][item_id] = item_data
                self.logger.info(f"Created item content: {item_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error creating item content: {e}")
            return False
    
    def update_content(self, content_type: str, content_id: str, new_data: Dict[str, Any]) -> bool:
        """Update existing content"""
        try:
            if content_type not in self.content:
                self.logger.error(f"Invalid content type: {content_type}")
                return False
            
            if self._validate_content(content_type, new_data):
                self.content[content_type][content_id] = new_data
                self.logger.info(f"Updated {content_type} content: {content_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating content: {e}")
            return False
    
    def remove_content(self, content_type: str, content_id: str) -> bool:
        """Remove content"""
        try:
            if content_type in self.content and content_id in self.content[content_type]:
                del self.content[content_type][content_id]
                self.logger.info(f"Removed {content_type} content: {content_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing content: {e}")
            return False
    
    def search_content(self, content_type: str, search_term: str) -> List[Dict[str, Any]]:
        """Search content by term"""
        try:
            results = []
            content_items = self.get_all_content(content_type)
            
            for content_id, content_data in content_items.items():
                if self._content_matches_search(content_data, search_term):
                    results.append(content_data)
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching content: {e}")
            return []
    
    def _content_matches_search(self, content_data: Dict[str, Any], search_term: str) -> bool:
        """Check if content matches search term"""
        search_term = search_term.lower()
        
        for key, value in content_data.items():
            if isinstance(value, str) and search_term in value.lower():
                return True
            elif isinstance(value, dict):
                if self._content_matches_search(value, search_term):
                    return True
        
        return False
    
    def export_content(self, content_type: str, file_path: str) -> bool:
        """Export content to file"""
        try:
            content_data = self.get_all_content(content_type)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Exported {content_type} content to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting content: {e}")
            return False
    
    def import_content(self, content_type: str, file_path: str) -> bool:
        """Import content from file"""
        try:
            content_data = self._load_json_file(file_path)
            if content_data:
                self.content[content_type] = content_data
                self.logger.info(f"Imported {content_type} content from {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error importing content: {e}")
            return False
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Get content statistics"""
        stats = {}
        for content_type, content_items in self.content.items():
            stats[content_type] = {
                'count': len(content_items),
                'ids': list(content_items.keys())
            }
        return stats
    
    def validate_all_content(self) -> Dict[str, bool]:
        """Validate all content"""
        validation_results = {}
        
        for content_type, content_items in self.content.items():
            valid_count = 0
            total_count = len(content_items)
            
            for content_id, content_data in content_items.items():
                if self._validate_content(content_type, content_data):
                    valid_count += 1
                else:
                    self.logger.warning(f"Invalid {content_type} content: {content_id}")
            
            validation_results[content_type] = valid_count == total_count
        
        return validation_results
    
    def cleanup(self) -> None:
        """Cleanup content manager resources"""
        try:
            self.content.clear()
            self.logger.info("Content manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during content manager cleanup: {e}")
