from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.officer_repo import OfficerRepository
from app.schemas.officer import OfficerCreate
from app.models.officer import Officer

class OfficerService:
    """
    Service layer orchestrating the synchronization of Catalyst Identities to Local Officers.
    """
    
    @staticmethod
    async def sync_catalyst_identity(session: AsyncSession, catalyst_identity: Dict[str, Any]) -> Officer:
        """
        Looks up an officer by their Catalyst ID. If they don't exist, provisions a new record.
        """
        catalyst_id = str(catalyst_identity.get("user_id"))
        email = str(catalyst_identity.get("email_id"))
        
        first_name = catalyst_identity.get("first_name", "")
        last_name = catalyst_identity.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or "Unknown Officer"
        
        # Extract role from Catalyst (fallback to default)
        role_details = catalyst_identity.get("role_details", {})
        catalyst_role = role_details.get("role_name", "STATION_OFFICER")
        
        # Map Catalyst role to backend role enum/string if needed (Task 2 integration point)
        role = catalyst_role

        # 1. Lookup existing
        officer = await OfficerRepository.get_by_catalyst_id(session, catalyst_id)
        if officer:
            # (Optional) Update fields if they changed in Catalyst
            return officer
            
        # 2. First-login provisioning
        new_officer_data = OfficerCreate(
            catalyst_user_id=catalyst_id,
            name=full_name,
            email=email,
            role=role,
        )
        
        new_officer = await OfficerRepository.create(session, new_officer_data)
        return new_officer
