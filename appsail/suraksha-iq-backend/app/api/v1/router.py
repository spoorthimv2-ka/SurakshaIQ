from fastapi import APIRouter

from .alerts.routes import router as alerts_router
from .anomaly.routes import router as anomaly_router
from .auth.routes import router as auth_router
from .dashboard.routes import router as dashboard_router
from .districts.routes import router as districts_router
from .hotspots.routes import router as hotspots_router
from .network.routes import router as network_router
from .repeat_offenders.routes import router as repeat_offenders_router
from .reports.routes import router as reports_router
from .risk.routes import router as risk_router
from .search.routes import router as search_router
from .users.routes import router as users_router

api_router = APIRouter()

api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(anomaly_router, prefix="/anomaly", tags=["Anomaly"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(districts_router, prefix="/districts", tags=["Districts"])
api_router.include_router(hotspots_router, prefix="/hotspots", tags=["Hotspots"])
api_router.include_router(network_router, prefix="/network", tags=["Network"])
api_router.include_router(repeat_offenders_router, prefix="/repeat-offenders", tags=["Repeat Offenders"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(risk_router, prefix="/risk", tags=["Risk"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
