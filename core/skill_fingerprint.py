import hashlib
import json
import os
import re
from typing import Dict, List, Optional, Tuple

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    util = None

class SkillFingerprintManager:
    def __init__(self, fingerprint_dir: Optional[str] = None, model_path: Optional[str] = None):
        """
        Initialize skill fingerprint manager
        
        Args:
            fingerprint_dir: Fingerprint storage directory, defaults to fingerprints subdirectory under skills directory
            model_path: Pre-downloaded model path, uses default model name if not specified
        """
        if fingerprint_dir is None:
            # Default to fingerprints subdirectory under skills directory
            from .skill_generator import SkillGenerator
            default_skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
            fingerprint_dir = os.path.join(default_skills_dir, "fingerprints")
        
        self.fingerprint_dir = fingerprint_dir
        os.makedirs(self.fingerprint_dir, exist_ok=True)
        
        self.fingerprint_file = os.path.join(self.fingerprint_dir, "skill_fingerprints.json")
        self.skill_fingerprints = self._load_fingerprints()
        
        # Initialize Sentence-Transformer model path (lazy loading)
        if model_path:
            self.model_name_or_path = model_path
        else:
            # Default to pre-downloaded model in model subdirectory under core directory
            models_dir = os.path.join(os.path.dirname(__file__), "model")
            self.model_name_or_path = os.path.join(models_dir, "all-MiniLM-L6-v2")
            # If local model doesn't exist, use default model name
            if not os.path.exists(self.model_name_or_path):
                self.model_name_or_path = 'all-MiniLM-L6-v2'
        
        self.model = None  # Lazy loading, only load when needed
        
        # Store skill description embeddings
        self.skill_embeddings = {}
        
        # Store skill descriptions for preprocessing
        self.skill_descriptions = {}
        
        # Don't preprocess at initialization, use lazy loading instead
        # self._preprocess_skill_descriptions()
    
    def _load_fingerprints(self) -> Dict[str, Dict[str, any]]:
        """
        Load skill fingerprints from file
        """
        if os.path.exists(self.fingerprint_file):
            try:
                with open(self.fingerprint_file, "r", encoding="utf-8") as f:
                    fingerprints = json.load(f)
                
                # Only keep fingerprints for currently existing skills
                from .skill_generator import SkillGenerator
                default_skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
                existing_skills = []
                for item in os.listdir(default_skills_dir):
                    item_path = os.path.join(default_skills_dir, item)
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "manifest.yaml")):
                        existing_skills.append(item)
                
                # Filter out existing skill fingerprints
                existing_fingerprints = {}
                for skill_name, fingerprint in fingerprints.items():
                    if skill_name in existing_skills:
                        existing_fingerprints[skill_name] = fingerprint
                
                return existing_fingerprints
            except Exception as e:
                print(f"Failed to load fingerprint file: {e}")
        return {}
    
    def _save_fingerprints(self):
        """
        Save skill fingerprints to file
        """
        try:
            with open(self.fingerprint_file, "w", encoding="utf-8") as f:
                json.dump(self.skill_fingerprints, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save fingerprint file: {e}")
    
    def _ensure_model_loaded(self):
        """
        Ensure model is loaded (lazy loading)
        """
        if self.model is None:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers library not installed. Please install the skill-fingerprint dependency:\n"
                    "pip install autoskill-ai[skill-fingerprint]"
                )
            self.model = SentenceTransformer(self.model_name_or_path)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for fingerprint calculation
        """
        # Remove punctuation
        text = re.sub(r'[\W_]+', ' ', text.lower())
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _preprocess_skill_descriptions(self):
        """
        Preprocess all skill descriptions and compute embeddings for similarity calculation
        """
        self._ensure_model_loaded()
        self.skill_descriptions = {}
        self.skill_embeddings = {}
        for skill_name, fingerprint in self.skill_fingerprints.items():
            description = fingerprint.get("description", "")
            if description:
                processed_desc = self._preprocess_text(description)
                self.skill_descriptions[skill_name] = processed_desc
                # Compute and store embedding
                self.skill_embeddings[skill_name] = self.model.encode(processed_desc, convert_to_tensor=True)
    
    def compute_fingerprint(self, skill_name: str, description: str, code: Optional[str] = None) -> Dict[str, any]:
        """
        Compute skill fingerprint
        
        Args:
            skill_name: Skill name
            description: Skill description
            code: Skill code (optional)
        
        Returns:
            Skill fingerprint dictionary
        """
        # Compute hash of description
        desc_hash = hashlib.md5(self._preprocess_text(description).encode()).hexdigest()
        
        # Compute hash of code (if provided)
        code_hash = None
        if code:
            # Remove whitespace and comments, keep only core code structure
            clean_code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            clean_code = re.sub(r'\s+', '', clean_code)
            code_hash = hashlib.md5(clean_code.encode()).hexdigest()
        
        fingerprint = {
            "description": description,
            "desc_hash": desc_hash,
            "code_hash": code_hash,
            "created_at": os.path.getmtime(__file__)  # Use current time as creation time
        }
        
        return fingerprint
    
    def register_skill(self, skill_name: str, description: str, code: Optional[str] = None):
        """
        Register skill, compute and store its fingerprint and embedding
        
        Args:
            skill_name: Skill name
            description: Skill description
            code: Skill code (optional)
        """
        self._ensure_model_loaded()
        fingerprint = self.compute_fingerprint(skill_name, description, code)
        self.skill_fingerprints[skill_name] = fingerprint
        processed_desc = self._preprocess_text(description)
        self.skill_descriptions[skill_name] = processed_desc
        # Compute and store embedding
        self.skill_embeddings[skill_name] = self.model.encode(processed_desc, convert_to_tensor=True)
        self._save_fingerprints()
    
    def check_duplicate(self, description: str, threshold: float = 0.7) -> Tuple[bool, Optional[str], float]:
        """
        Check for duplicate skills
        
        Args:
            description: Skill description to check
            threshold: Similarity threshold, default 0.7
        
        Returns:
            (Whether duplicate exists, Duplicate skill name, Similarity)
        """
        self._ensure_model_loaded()
        if not self.skill_embeddings:
            return False, None, 0.0
        
        # Preprocess input description and compute embedding
        processed_desc = self._preprocess_text(description)
        input_embedding = self.model.encode(processed_desc, convert_to_tensor=True)
        
        # Compute similarity with all skill descriptions
        max_similarity = 0.0
        max_skill = None
        
        for skill_name, embedding in self.skill_embeddings.items():
            similarity = util.cos_sim(input_embedding, embedding).item()
            if similarity > max_similarity:
                max_similarity = similarity
                max_skill = skill_name
        
        if max_similarity >= threshold:
            return True, max_skill, max_similarity
        else:
            return False, None, max_similarity
    
    def get_skill_fingerprint(self, skill_name: str) -> Optional[Dict[str, any]]:
        """
        Get skill fingerprint
        
        Args:
            skill_name: Skill name
        
        Returns:
            Skill fingerprint dictionary, None if not exists
        """
        return self.skill_fingerprints.get(skill_name)
    
    def remove_skill(self, skill_name: str):
        """
        Remove skill fingerprint and embedding
        
        Args:
            skill_name: Skill name
        """
        if skill_name in self.skill_fingerprints:
            del self.skill_fingerprints[skill_name]
        if skill_name in self.skill_descriptions:
            del self.skill_descriptions[skill_name]
        if skill_name in self.skill_embeddings:
            del self.skill_embeddings[skill_name]
        self._save_fingerprints()
    
    def list_skills(self) -> List[str]:
        """
        List all registered skills
        
        Returns:
            List of skill names
        """
        return list(self.skill_fingerprints.keys())
