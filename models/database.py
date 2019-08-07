import arrow
from sqlalchemy import Column, Integer, Float, Boolean, BigInteger, DateTime, ForeignKey, MetaData, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.util.compat import contextmanager

database_metadata = MetaData()
Base = declarative_base(metadata=database_metadata)


class System(Base):
    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    permit_required = Column(Boolean, nullable=False)
    name = Column(Text, nullable=False)
    allegiance = Column(Text, nullable=True)
    government = Column(Text, nullable=True)
    security = Column(Text, nullable=True)
    primary_economy = Column(Text, nullable=True)
    updated_at = Column(Integer, nullable=False)
    population = Column(BigInteger, nullable=True)
    power = Column(Text, nullable=True)
    power_state = Column(Text, nullable=True)

    stations = relationship("Station", backref="systems")


class Station(Base):
    __tablename__ = 'stations'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    last_shipyard_update = Column(DateTime, nullable=True)
    distance_to_star = Column(Integer, nullable=True)
    max_landing_pad = Column(Text, nullable=True)
    is_planetary = Column(Boolean, nullable=False)
    type = Column(Text, nullable=True)

    system_id = Column(Integer, ForeignKey('systems.id'))
    system = relationship('System', lazy='joined', back_populates="stations")

    ships_sold = relationship('StationShipLink', lazy='joined')


class StationShipLink(Base):
    __tablename__ = 'station_ship_link'

    station_id = Column(Integer, ForeignKey('stations.id'), primary_key=True)
    ship_id = Column(Integer, ForeignKey('ships.id'), primary_key=True)
    station = relationship('Station', lazy='joined')
    ship = relationship('Ship', lazy='joined')


class Ship(Base):
    __tablename__ = 'ships'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    internal_name = Column(Text, nullable=False)


class CommodityCategory(Base):
    __tablename__ = 'commodities_categories'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Commodity(Base):
    __tablename__ = 'commodities'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    internal_name = Column(Text, nullable=False)
    average_price = Column(Integer, nullable=True)
    is_rare = Column(Boolean, nullable=False)

    category_id = Column(Integer, ForeignKey('commodities_categories.id'))
    category = relationship('CommodityCategory', lazy='joined')


class CommodityPrice(Base):
    __tablename__ = 'commodities_prices'

    id = Column(Integer, primary_key=True)
    supply = Column(BigInteger)
    buy_price = Column(Integer)
    sell_price = Column(Integer)
    demand = Column(BigInteger)
    collected_at = Column(Integer, index=True)

    commodity_id = Column(Integer, index=True)
    commodity = relationship('Commodity',
                             primaryjoin='foreign(CommodityPrice.commodity_id) == remote(Commodity.id)',
                             lazy='select')

    station_id = Column(Integer, index=True)
    station = relationship('Station',
                           primaryjoin='foreign(CommodityPrice.station_id) == remote(Station.id)',
                           lazy='select')

    def from_eddn_dict(self, timestamp, data):
        msg_time = arrow.get(timestamp).to('utc').timestamp

        if msg_time > self.collected_at:
            self.demand = data.get("demand")
            self.buy_price = data.get("buyPrice")
            self.sell_price = data.get("sellPrice")
            self.supply = data.get("stock")
            self.collected_at = msg_time


class Engineer(Base):
    __tablename__ = 'engineers'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class BlueprintIngredient(Base):
    __tablename__ = 'blueprint_ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class EngineerBlueprint(Base):
    __tablename__ = 'engineer_blueprints'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    grade = Column(Integer, nullable=True)
    engineers = relationship('BlueprintEngineerLink', lazy='joined')
    ingredients = relationship('BlueprintIngredientLink', lazy='joined')


class BlueprintEngineerLink(Base):
    __tablename__ = 'blueprint_engineer_link'

    blueprint_id = Column(Integer, ForeignKey('engineer_blueprints.id'), primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'), primary_key=True)
    blueprint = relationship('EngineerBlueprint', lazy='joined')
    engineer = relationship('Engineer', lazy='joined')


class BlueprintIngredientLink(Base):
    __tablename__ = 'blueprint_ingredient_link'

    id = Column(Integer, primary_key=True)
    blueprint_id = Column(Integer, ForeignKey('engineer_blueprints.id'))
    ingredient_id = Column(Integer, ForeignKey('blueprint_ingredients.id'))
    quantity = Column(Integer)
    blueprint = relationship('EngineerBlueprint', lazy='joined')
    ingredient = relationship('BlueprintIngredient', lazy='joined')


class CommunityGoalStatus(Base):
    __tablename__ = 'community_goals_status'

    id = Column(Integer, primary_key=True)
    last_update = Column(DateTime, nullable=False)
    is_finished = Column(Boolean, nullable=False)
    current_tier = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)


@contextmanager
def get_session(engine):
    """Provide a transactional scope around a series of operations."""
    sess = sessionmaker(bind=engine)()
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
        raise
    finally:
        sess.close()
