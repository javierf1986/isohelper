"""
Language & Translation API Routes
Phase 4: Multi-language Support
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.database import get_db
from backend.services.translation_service import TranslationService
from backend.api.dependencies import get_current_user
from backend.models.user_models import User

router = APIRouter(prefix="/languages", tags=["Languages & i18n"])


# ===== Request/Response Models =====

class LanguageResponse(BaseModel):
    """Language response model"""
    code: str
    name: str
    native_name: str
    flag_emoji: Optional[str]
    is_rtl: bool
    is_active: bool

class TranslationRequest(BaseModel):
    """Translation request"""
    key: str
    text: str
    language_code: str
    category: str = "ui"

class UserLanguagePreferenceRequest(BaseModel):
    """User language preference request"""
    language_code: str
    date_format: Optional[str] = "MM/DD/YYYY"
    time_format: Optional[str] = "12h"
    timezone: Optional[str] = "UTC"

class UserLanguagePreferenceResponse(BaseModel):
    """User language preference response"""
    language_code: str
    date_format: str
    time_format: str
    timezone: str


# ===== Routes =====

@router.get("/", response_model=List[LanguageResponse])
async def get_languages(db: Session = Depends(get_db)):
    """
    Get all active languages.
    
    Returns list of supported languages with their details.
    """
    languages = TranslationService.get_active_languages(db)
    return [
        LanguageResponse(
            code=lang.code,
            name=lang.name,
            native_name=lang.native_name,
            flag_emoji=lang.flag_emoji,
            is_rtl=lang.is_rtl,
            is_active=lang.is_active
        )
        for lang in languages
    ]


@router.get("/detect")
async def detect_language(
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    """
    Detect preferred language from Accept-Language header.
    
    Returns the best matching supported language code.
    """
    language_code = TranslationService.detect_language_from_header(accept_language)
    return {"language_code": language_code}


@router.get("/translate/{key}")
async def get_translation(
    key: str,
    language_code: str = "en",
    db: Session = Depends(get_db)
):
    """
    Get translation for a specific key.
    
    - **key**: Translation key (e.g., 'dashboard.welcome')
    - **language_code**: Target language code (default: 'en')
    """
    text = TranslationService.get_translation(db, key, language_code)
    return {
        "key": key,
        "language_code": language_code,
        "text": text
    }


@router.post("/translate")
async def get_translations_batch(
    keys: List[str],
    language_code: str = "en",
    db: Session = Depends(get_db)
):
    """
    Get multiple translations at once.
    
    - **keys**: List of translation keys
    - **language_code**: Target language code (default: 'en')
    """
    translations = TranslationService.get_translations_batch(db, keys, language_code)
    return {
        "language_code": language_code,
        "translations": translations
    }


@router.get("/preferences", response_model=UserLanguagePreferenceResponse)
async def get_user_language_preference(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's language preference.
    """
    pref = TranslationService.get_user_language(db, str(current_user.id))
    if not pref:
        # Return default
        return UserLanguagePreferenceResponse(
            language_code="en",
            date_format="MM/DD/YYYY",
            time_format="12h",
            timezone="UTC"
        )
    
    return UserLanguagePreferenceResponse(
        language_code=pref.language_code,
        date_format=pref.date_format,
        time_format=pref.time_format,
        timezone=pref.timezone
    )


@router.put("/preferences", response_model=UserLanguagePreferenceResponse)
async def set_user_language_preference(
    request: UserLanguagePreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set current user's language preference.
    
    - **language_code**: Language code (e.g., 'en', 'es', 'fr')
    - **date_format**: Date format preference
    - **time_format**: Time format preference ('12h' or '24h')
    - **timezone**: User's timezone
    """
    # Verify language exists
    language = db.query(TranslationService.Language).filter(
        TranslationService.Language.code == request.language_code
    ).first()
    
    if not language:
        raise HTTPException(status_code=400, detail="Invalid language code")
    
    pref = TranslationService.set_user_language(
        db=db,
        user_id=str(current_user.id),
        language_code=request.language_code,
        date_format=request.date_format,
        time_format=request.time_format,
        timezone=request.timezone
    )
    
    return UserLanguagePreferenceResponse(
        language_code=pref.language_code,
        date_format=pref.date_format,
        time_format=pref.time_format,
        timezone=pref.timezone
    )


# Admin routes for managing translations

@router.post("/admin/translations", dependencies=[Depends(get_current_user)])
async def create_translation(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update a translation (Admin only).
    
    - **key**: Translation key
    - **text**: Translated text
    - **language_code**: Target language
    - **category**: Category (ui, email, clause, etc.)
    """
    # TODO: Add admin role check
    translation = TranslationService.set_translation(
        db=db,
        key=request.key,
        language_code=request.language_code,
        text=request.text,
        category=request.category,
        user_id=str(current_user.id)
    )
    
    return {
        "key": request.key,
        "language_code": request.language_code,
        "text": request.text,
        "created_by": str(current_user.id)
    }


@router.post("/admin/initialize")
async def initialize_languages(
    db: Session = Depends(get_db)
):
    """
    Initialize default languages in database (Admin only).
    Should be called once during setup.
    """
    TranslationService.initialize_languages(db)
    return {"message": "Languages initialized successfully"}
