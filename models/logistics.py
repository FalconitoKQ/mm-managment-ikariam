from models import db
from datetime import datetime
from sqlalchemy import func
import enum


class LogisticsStatus(enum.Enum):
    active = 'active', 'aktywna'
    disabled = 'disabled', 'nieaktywny'
    completed = 'completed', 'zakończona'
    deleted = 'deleted', 'usunięta'

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def __str__(self):
        return self.label

class LogisticsTypeOffer(enum.Enum):
    Needs = 'Needs', 'Potrzebuje'
    Offers = 'Offers', 'Oferuje'
    Requests = 'Requests', 'Prośby'

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def __str__(self):
        return self.label

class LogisticsType(enum.Enum):
    LandUnits = 'LandUnits', 'Jednostki Lądowe'
    NavalUnits = 'NavalUnits', 'Jednostki Morskie'
    RawMaterials = 'RawMaterials', 'Surowce'
    
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def __str__(self):
        return self.label

class TypeLandUnits(enum.Enum):
    Hoplite = 'Hoplite', 'Hoplita'
    SteamGiant = 'SteamGiant', 'Gigant Parowy'
    Swordsman = 'Swordsman', 'Wojownik'
    Spearman = 'Spearman', 'Oszczepnik'
    Sulphur = 'Sulphur', 'Strzelec Siarkowy'
    Archer = 'Archer', 'Łucznik'
    Slinger = 'Slinger', 'Procarz'
    Mortar = 'Mortar', 'Moździerz'
    Catapult = 'Catapult', 'Katapulta'
    Ram = 'Ram', 'Taran'
    BalloonBombardier = 'BalloonBombardier', 'Balonowy Bombardier'
    Gyrocopter = 'Gyrocopter', 'Żyrokopter'
    Cook = 'Cook', 'Kucharz'
    Doctor = 'Doctor', 'Doktor'

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def __str__(self):
        return self.label

class TypeNavalUnits(enum.Enum):
    SteamRam = 'SteamRam', 'Taran Parowy'
    FireShip = 'FireShip', 'Grecki Ogień (miotła)'
    RamShip = 'RamShip', 'Statek z Taranem'
    BallistaShip = 'BallistaShip', 'Balista'
    CatapultShip = 'CatapultShip', 'Okręt z Katapultą'
    MortarShip = 'MortarShip', 'Okręt z Moździerzem'
    DivingBoat = 'DivingBoat', 'Łódź Podwodna'
    RocketShip = 'RocketShip', 'Krążownik Rakietowy'
    BalloonCarrier = 'BalloonCarrier', 'Balonowiec'
    PaddleSpeedboat = 'PaddleSpeedboat', 'Statek Parowy'
    Tender = 'Tender', 'Statek Pomocniczy'
    CargoShip = 'CargoShip', 'Statek Transportowy'
    PhoenicianMerchantShip = 'PhoenicianMerchantShip', 'Fenicki Statek Handlowy'
    Freighter = 'Freighter', 'Statek transportowy'
    PhoenicianFreighterer = 'PhoenicianFreighterer', 'Fenicki Statek Transportowy'

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def __str__(self):
        return self.label
    
class TypeRawMaterials(enum.Enum):
    Money = 'Money', 'Pieniądze'
    Wood = 'Wood', 'Drewno'
    Wine = 'Wine', 'Wino'
    Stone = 'Stone', 'Kamień'
    Crystal = 'Crystal', 'Kryształ'
    Sulphur = 'Sulphur', 'Siarka'

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def __str__(self):
        return self.label

class Logistics(db.Model):
    __tablename__ = 'logistics'
    id_order = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_order = db.Column(db.Enum(LogisticsType), nullable=False)
    subtype_order = db.Column(db.String, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(LogisticsStatus), default=LogisticsStatus.active, nullable=False)
    time_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=func.current_timestamp())
    contractor = db.Column(db.ForeignKey('users.username'), nullable=False)
    principal = db.Column(db.ForeignKey('users.username'), nullable=True)

    contractor_user = db.relationship('User', foreign_keys=[contractor], backref='orders_as_contractor', lazy='select')
    principal_user = db.relationship('User', foreign_keys=[principal], backref='orders_as_principal', lazy='select')

    preferred_time = db.Column(db.DateTime, nullable=True)
    time_complete = db.Column(db.DateTime, nullable=True)
    offert = db.Column(db.Enum(LogisticsTypeOffer), nullable=True)

    # Metoda do pobrania etykiety dla podtypu zamówienia
    @property
    def subtype_order_label(self):
        if not self.subtype_order:
            return '-'
        try:
            # wybieramy odpowiednie podtypy dla danego typu
            enum_cls = LogisticsType_enum[self.type_order]
            return enum_cls(self.subtype_order).label
        except (KeyError, ValueError):
            return self.subtype_order

LogisticsType_enum = {
    LogisticsType.LandUnits: TypeLandUnits,
    LogisticsType.NavalUnits: TypeNavalUnits,
    LogisticsType.RawMaterials: TypeRawMaterials
}