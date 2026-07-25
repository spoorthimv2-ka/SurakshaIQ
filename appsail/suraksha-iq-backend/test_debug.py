import os
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

import asyncio
from app.core.mock_data import get_mock_app
from app.repositories.network_repo import NetworkRepository
from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.crime_criminal_link_repo import CrimeCriminalLinkRepository

async def main():
    app = get_mock_app()
    
    # Test repeat offender repo
    repo = RepeatOffenderRepository(None)
    repo.request = app
    repo.zcql = app.zcql()
    
    try:
        criminals = await repo.find_active(limit=1000, offset=0)
        print(f"Criminals found: {len(criminals)}")
    except Exception as e:
        print(f"find_active ERROR: {type(e).__name__}: {e}")
        return

    try:
        first_id = criminals[0].get('ROWID', '') if criminals else ''
        links = await repo.find_by_criminal(first_id, limit=1000)
        print(f"Links for {first_id}: {len(links)}")
    except Exception as e:
        print(f"find_by_criminal ERROR: {type(e).__name__}: {e}")
        return

    try:
        crime_repo = CrimeRepository(None)
        crime_repo.request = app
        crime_repo.zcql = app.zcql()
        crimes = await crime_repo.find_all_with_filters(limit=1000)
        print(f"Crimes found: {len(crimes)}")
    except Exception as e:
        print(f"find_all_with_filters ERROR: {type(e).__name__}: {e}")
        return

    # Test network repo
    net_repo = NetworkRepository(None)
    net_repo.request = app
    net_repo.zcql = app.zcql()
    
    try:
        data = await net_repo.get_network_data(limit=500)
        print(f"Network data keys: {list(data.keys())}")
        print(f"Criminals: {len(data.get('criminals', []))}")
        print(f"Links: {len(data.get('links', []))}")
    except Exception as e:
        print(f"get_network_data ERROR: {type(e).__name__}: {e}")
        return
    
    try:
        from app.services.network_service import NetworkService
        from fastapi import Request
        service = NetworkService(None)
        service.request = app
        service.repo = net_repo
        
        result = await service.get_advanced_graph({}, filters={})
        print(f"Advanced graph: {len(result.nodes)} nodes, {len(result.edges)} edges")
    except Exception as e:
        print(f"get_advanced_graph ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

    try:
        result = await service.get_analytics({})
        print(f"Analytics OK: {result}")
    except Exception as e:
        print(f"get_analytics ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

    try:
        result = await service.get_timeline({})
        print(f"Timeline OK: {len(result.timeline)} events")
    except Exception as e:
        print(f"get_timeline ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

asyncio.run(main())
