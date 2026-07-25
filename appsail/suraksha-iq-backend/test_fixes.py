import os
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

import asyncio
from unittest.mock import patch
from app.core.mock_data import get_mock_app

async def main():
    app = get_mock_app()
    mock_zcql = app.zcql()

    print("=== Testing Repeat Offenders Fix ===")
    from app.repositories.fir_repo import FIRRepository
    from app.repositories.repeat_offender_repo import RepeatOffenderRepository
    from app.repositories.crime_repo import CrimeRepository
    from app.repositories.crime_criminal_link_repo import CrimeCriminalLinkRepository
    from app.services.repeat_offender_service import RepeatOffenderService
    from fastapi import Request

    with patch('app.repositories.fir_repo.FIRRepository.zcql', new_callable=lambda mock_zcql=app.zcql(): mock_zcql), \
         patch('app.repositories.repeat_offender_repo.RepeatOffenderRepository.zcql', new_callable=lambda mock_zcql=app.zcql(): mock_zcql), \
         patch('app.repositories.crime_repo.CrimeRepository.zcql', new_callable=lambda mock_zcql=app.zcql(): mock_zcql), \
         patch('app.repositories.crime_criminal_link_repo.CrimeCriminalLinkRepository.zcql', new_callable=lambda mock_zcql=app.zcql(): mock_zcql):
        
        fir_repo = FIRRepository(None)
        
        result = await fir_repo.count_by_district("bangalore-urban")
        print(f"count_by_district('bangalore-urban'): {result}")

        result = await fir_repo.count_by_station("bangalore-urban")
        print(f"count_by_station('bangalore-urban'): {result}")

        service = RepeatOffenderService(None)
        service.fir_repo = fir_repo
        service.repo = RepeatOffenderRepository(None)
        service.crime_repo = CrimeRepository(None)
        service.link_repo = CrimeCriminalLinkRepository(None)

        try:
            offenders = await service.get_repeat_offenders({}, limit=10)
            print(f"get_repeat_offenders: {len(offenders)} offenders")
            for o in offenders[:3]:
                print(f"  - {o.offender_name}: {o.total_offences} offences, score={o.repeat_offender_score}")
        except Exception as e:
            print(f"get_repeat_offenders ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        try:
            stats = await service.get_statistics({})
            print(f"get_statistics: total={stats.total_repeat_offenders}, avg={stats.average_offences}")
        except Exception as e:
            print(f"get_statistics ERROR: {type(e).__name__}: {e}")

        try:
            top = await service.get_top_repeat_offenders({}, limit=5)
            print(f"get_top_repeat_offenders: {len(top)} offenders")
        except Exception as e:
            print(f"get_top_repeat_offenders ERROR: {type(e).__name__}: {e}")

    print("\n=== Testing Network APIs Fix ===")
    from app.repositories.network_repo import NetworkRepository
    from app.services.network_service import NetworkService

    with patch('app.repositories.network_repo.NetworkRepository.zcql', new_callable=lambda mock_zcql=app.zcql(): mock_zcql):
        net_repo = NetworkRepository(None)
        net_service = NetworkService(None)
        net_service.repo = net_repo

        try:
            result = await net_service.get_advanced_graph({}, filters={})
            print(f"get_advanced_graph: {len(result.nodes)} nodes, {len(result.edges)} edges")
            print(f"  communities: {len(result.communities)}")
            print(f"  centrality keys: {len(result.centrality or {})}")
        except Exception as e:
            print(f"get_advanced_graph ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        try:
            result = await net_service.get_analytics({})
            print(f"get_analytics: bridge_nodes={len(result.bridge_nodes)}")
            print(f"  community_stats: {result.community_stats}")
        except Exception as e:
            print(f"get_analytics ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        try:
            result = await net_service.get_timeline({})
            print(f"get_timeline: {len(result.timeline)} events")
            if result.timeline:
                print(f"  first: {result.timeline[0]}")
        except Exception as e:
            print(f"get_timeline ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(main())
