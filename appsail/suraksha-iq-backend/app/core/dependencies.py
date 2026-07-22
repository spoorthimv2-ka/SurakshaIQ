from fastapi import Depends, Request

# Repositories
from app.repositories.user_repo import UserRepository
from app.repositories.officer_repo import OfficerRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.criminal_repo import CriminalRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.report_repo import ReportRepository

# Services
from app.services.user_service import UserService
from app.services.officer_service import OfficerService
from app.services.district_service import DistrictService
from app.services.police_station_service import PoliceStationService
from app.services.crime_service import CrimeService
from app.services.fir_service import FIRService
from app.services.criminal_service import CriminalService
from app.services.alert_service import AlertService
from app.services.report_service import ReportService

# Dependency Providers for Repositories
def get_user_repo(request: Request) -> UserRepository:
    return UserRepository(request)

def get_officer_repo(request: Request) -> OfficerRepository:
    return OfficerRepository(request)

def get_district_repo(request: Request) -> DistrictRepository:
    return DistrictRepository(request)

def get_police_station_repo(request: Request) -> PoliceStationRepository:
    return PoliceStationRepository(request)

def get_crime_repo(request: Request) -> CrimeRepository:
    return CrimeRepository(request)

def get_fir_repo(request: Request) -> FIRRepository:
    return FIRRepository(request)

def get_criminal_repo(request: Request) -> CriminalRepository:
    return CriminalRepository(request)

def get_alert_repo(request: Request) -> AlertRepository:
    return AlertRepository(request)

def get_report_repo(request: Request) -> ReportRepository:
    return ReportRepository(request)

# Dependency Providers for Services
def get_user_service(request: Request, repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(request, repo)

def get_officer_service(request: Request, repo: OfficerRepository = Depends(get_officer_repo)) -> OfficerService:
    return OfficerService(request, repo)

def get_district_service(request: Request, repo: DistrictRepository = Depends(get_district_repo)) -> DistrictService:
    return DistrictService(request, repo)

def get_police_station_service(request: Request, repo: PoliceStationRepository = Depends(get_police_station_repo)) -> PoliceStationService:
    return PoliceStationService(request, repo)

def get_crime_service(request: Request, repo: CrimeRepository = Depends(get_crime_repo)) -> CrimeService:
    return CrimeService(request, repo)

def get_fir_service(request: Request, repo: FIRRepository = Depends(get_fir_repo)) -> FIRService:
    return FIRService(request, repo)

def get_criminal_service(request: Request, repo: CriminalRepository = Depends(get_criminal_repo)) -> CriminalService:
    return CriminalService(request, repo)

def get_alert_service(request: Request, repo: AlertRepository = Depends(get_alert_repo)) -> AlertService:
    return AlertService(request, repo)

def get_report_service(request: Request, repo: ReportRepository = Depends(get_report_repo)) -> ReportService:
    return ReportService(request, repo)
