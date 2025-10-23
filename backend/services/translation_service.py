"""
Translation Service
Phase 4: Multi-language Support

Handles translation management, language detection, and i18n operations.
"""
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models.language_models import (
    Language, TranslationKey, Translation,
    ISOClauseTranslation, UserLanguagePreference
)


class TranslationService:
    """Service for managing translations and i18n"""
    
    # Default supported languages
    DEFAULT_LANGUAGES = [
        {
            "code": "en",
            "name": "English",
            "native_name": "English",
            "flag_emoji": "🇺🇸",
            "is_rtl": False
        },
        {
            "code": "es",
            "name": "Spanish",
            "native_name": "Español",
            "flag_emoji": "🇪🇸",
            "is_rtl": False
        },
        {
            "code": "fr",
            "name": "French",
            "native_name": "Français",
            "flag_emoji": "🇫🇷",
            "is_rtl": False
        },
        {
            "code": "de",
            "name": "German",
            "native_name": "Deutsch",
            "flag_emoji": "🇩🇪",
            "is_rtl": False
        },
        {
            "code": "zh",
            "name": "Chinese (Simplified)",
            "native_name": "简体中文",
            "flag_emoji": "🇨🇳",
            "is_rtl": False
        }
    ]
    
    @staticmethod
    def initialize_languages(db: Session) -> None:
        """Initialize default languages in database"""
        for lang_data in TranslationService.DEFAULT_LANGUAGES:
            existing = db.query(Language).filter(Language.code == lang_data["code"]).first()
            if not existing:
                language = Language(**lang_data, is_active=True)
                db.add(language)
        db.commit()
    
    @staticmethod
    def get_active_languages(db: Session) -> List[Language]:
        """Get all active languages"""
        return db.query(Language).filter(Language.is_active == True).all()
    
    @staticmethod
    def get_translation(
        db: Session,
        key: str,
        language_code: str = "en",
        default: Optional[str] = None
    ) -> str:
        """
        Get translation for a key in specified language.
        Falls back to default language if translation not found.
        """
        # Try to get translation
        translation = db.query(Translation).join(TranslationKey).filter(
            and_(
                TranslationKey.key == key,
                Translation.language_code == language_code
            )
        ).first()
        
        if translation:
            return translation.translated_text
        
        # Fallback to English
        if language_code != "en":
            translation = db.query(Translation).join(TranslationKey).filter(
                and_(
                    TranslationKey.key == key,
                    Translation.language_code == "en"
                )
            ).first()
            if translation:
                return translation.translated_text
        
        # Fallback to default text in key
        key_obj = db.query(TranslationKey).filter(TranslationKey.key == key).first()
        if key_obj:
            return key_obj.default_text
        
        return default or key
    
    @staticmethod
    def get_translations_batch(
        db: Session,
        keys: List[str],
        language_code: str = "en"
    ) -> Dict[str, str]:
        """Get multiple translations at once"""
        translations = {}
        
        results = db.query(TranslationKey, Translation).outerjoin(
            Translation,
            and_(
                Translation.key_id == TranslationKey.id,
                Translation.language_code == language_code
            )
        ).filter(TranslationKey.key.in_(keys)).all()
        
        for key_obj, trans in results:
            translations[key_obj.key] = (
                trans.translated_text if trans else key_obj.default_text
            )
        
        return translations
    
    @staticmethod
    def set_translation(
        db: Session,
        key: str,
        language_code: str,
        text: str,
        category: str = "ui",
        default_text: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Translation:
        """Add or update a translation"""
        # Get or create translation key
        key_obj = db.query(TranslationKey).filter(TranslationKey.key == key).first()
        if not key_obj:
            key_obj = TranslationKey(
                key=key,
                category=category,
                default_text=default_text or text
            )
            db.add(key_obj)
            db.flush()
        
        # Get or create translation
        translation = db.query(Translation).filter(
            and_(
                Translation.key_id == key_obj.id,
                Translation.language_code == language_code
            )
        ).first()
        
        if translation:
            translation.translated_text = text
            translation.translated_by = user_id
        else:
            translation = Translation(
                key_id=key_obj.id,
                language_code=language_code,
                translated_text=text,
                translated_by=user_id
            )
            db.add(translation)
        
        db.commit()
        return translation
    
    @staticmethod
    def get_clause_translation(
        db: Session,
        clause_id: str,
        language_code: str = "en"
    ) -> Optional[ISOClauseTranslation]:
        """Get translated ISO clause content"""
        return db.query(ISOClauseTranslation).filter(
            and_(
                ISOClauseTranslation.clause_id == clause_id,
                ISOClauseTranslation.language_code == language_code
            )
        ).first()
    
    @staticmethod
    def set_user_language(
        db: Session,
        user_id: str,
        language_code: str,
        date_format: Optional[str] = None,
        time_format: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> UserLanguagePreference:
        """Set or update user's language preference"""
        pref = db.query(UserLanguagePreference).filter(
            UserLanguagePreference.user_id == user_id
        ).first()
        
        if pref:
            pref.language_code = language_code
            if date_format:
                pref.date_format = date_format
            if time_format:
                pref.time_format = time_format
            if timezone:
                pref.timezone = timezone
        else:
            pref = UserLanguagePreference(
                user_id=user_id,
                language_code=language_code,
                date_format=date_format or "MM/DD/YYYY",
                time_format=time_format or "12h",
                timezone=timezone or "UTC"
            )
            db.add(pref)
        
        db.commit()
        return pref
    
    @staticmethod
    def get_user_language(
        db: Session,
        user_id: str
    ) -> Optional[UserLanguagePreference]:
        """Get user's language preference"""
        return db.query(UserLanguagePreference).filter(
            UserLanguagePreference.user_id == user_id
        ).first()
    
    @staticmethod
    def detect_language_from_header(accept_language: Optional[str]) -> str:
        """Detect preferred language from Accept-Language header"""
        if not accept_language:
            return "en"
        
        # Parse Accept-Language header (simplified)
        # Format: "en-US,en;q=0.9,es;q=0.8"
        languages = []
        for lang in accept_language.split(","):
            parts = lang.strip().split(";")
            code = parts[0].split("-")[0].lower()  # Get base language code
            quality = 1.0
            if len(parts) > 1 and parts[1].startswith("q="):
                try:
                    quality = float(parts[1][2:])
                except:
                    pass
            languages.append((code, quality))
        
        # Sort by quality
        languages.sort(key=lambda x: x[1], reverse=True)
        
        # Return first supported language
        supported = [l["code"] for l in TranslationService.DEFAULT_LANGUAGES]
        for code, _ in languages:
            if code in supported:
                return code
        
        return "en"
