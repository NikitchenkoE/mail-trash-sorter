"""Checkpoint model for tracking email processing state."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CheckpointModel(BaseModel):
    """Model representing an email processing checkpoint.
    
    Used to track the last processed email UID for each mailbox to enable
    incremental email processing and avoid reprocessing already handled emails.
    
    Attributes:
        email: Email address/account identifier
        mailbox: Name of the mailbox (e.g., 'INBOX', 'Sent')
        uidvalidity: IMAP UIDVALIDITY value for mailbox consistency
        last_uid: Last processed email UID
        updated_at: Timestamp of last checkpoint update
    """
    
    email: str = Field(..., description="Email address/account identifier")
    mailbox: str = Field(..., description="Mailbox name")
    uidvalidity: int = Field(..., description="IMAP UIDVALIDITY value", ge=1)
    last_uid: Optional[int] = Field(
        None, description="Last processed email UID", ge=1
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )
    
    class Config:
        """Pydantic model configuration."""
        
        # Enable ORM mode for database integration
        from_attributes = True
        # Use enum values instead of enum objects
        use_enum_values = True
        # Validate assignment to prevent data corruption
        validate_assignment = True
        # Allow population by field name or alias
        populate_by_name = True
