import arrow
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.util.compat import contextmanager

database_metadata = MetaData()
Base = declarative_base(metadata=database_metadata)


class System(Base):
    __tablename__ = "systems"

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
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    last_shipyard_update = Column(DateTime, nullable=True)
    distance_to_star = Column(Integer, nullable=True)
    max_landing_pad = Column(Text, nullable=True)
    is_planetary = Column(Boolean, nullable=False)
    type = Column(Text, nullable=True)

    system_id = Column(Integer, ForeignKey("systems.id"))
    system = relationship("System", lazy="joined", back_populates="stations")


class StationShipLink(Base):
    __tablename__ = "station_ship_link"

    station_id = Column(Integer, ForeignKey("stations.id"), primary_key=True)
    ship_id = Column(Integer, ForeignKey("ships.id"), primary_key=True)
    station = relationship("Station", lazy="joined")
    ship = relationship("Ship", lazy="joined")


class StationModuleLink(Base):
    __tablename__ = "station_module_link"

    station_id = Column(Integer, ForeignKey("stations.id"), primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id"), primary_key=True)
    station = relationship("Station", lazy="joined")
    module = relationship("Module", lazy="joined")


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class CommodityCategory(Base):
    __tablename__ = "commodities_categories"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    def get_api_model(self):
        return {"id": self.id, "name": self.name}


class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    internal_name = Column(Text, nullable=False)
    average_price = Column(Integer, nullable=True)
    is_rare = Column(Boolean, nullable=False)

    category_id = Column(Integer, ForeignKey("commodities_categories.id"))
    category = relationship("CommodityCategory", lazy="joined")

    def get_api_model(self):
        return {
            "id": self.id,
            "name": self.name,
            "average_price": self.average_price,
            "is_rare": self.is_rare,
            "category": self.category.get_api_model(),
        }


class CommodityPrice(Base):
    __tablename__ = "commodities_prices"

    id = Column(Integer, primary_key=True)
    supply = Column(BigInteger)
    buy_price = Column(Integer)
    sell_price = Column(Integer)
    demand = Column(BigInteger)
    collected_at = Column(Integer, index=True)

    commodity_id = Column(Integer, index=True)
    commodity = relationship(
        "Commodity",
        primaryjoin="foreign(CommodityPrice.commodity_id) == remote(Commodity.id)",
        lazy="joined",
    )

    station_id = Column(Integer, index=True)
    station = relationship(
        "Station",
        primaryjoin="foreign(CommodityPrice.station_id) == remote(Station.id)",
        lazy="joined",
    )

    def from_eddn_dict(self, timestamp, data):
        msg_time = arrow.get(timestamp).to("utc").timestamp

        if msg_time > self.collected_at:
            self.demand = data.get("demand")
            self.buy_price = data.get("buyPrice")
            self.sell_price = data.get("sellPrice")
            self.supply = data.get("stock")
            self.collected_at = msg_time

    def get_api_model(self):
        return {
            "commodity": self.commodity.get_api_model(),
            "supply": self.supply,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "demand": self.demand,
            "collected_at": arrow.get(self.collected_at).isoformat(),
        }


class Engineer(Base):
    __tablename__ = "engineers"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class BlueprintIngredient(Base):
    __tablename__ = "blueprint_ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class EngineerBlueprint(Base):
    __tablename__ = "engineer_blueprints"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    grade = Column(Integer, nullable=True)
    engineers = relationship("BlueprintEngineerLink", lazy="joined")
    ingredients = relationship("BlueprintIngredientLink", lazy="joined")


class BlueprintEngineerLink(Base):
    __tablename__ = "blueprint_engineer_link"

    blueprint_id = Column(
        Integer, ForeignKey("engineer_blueprints.id"), primary_key=True
    )
    engineer_id = Column(Integer, ForeignKey("engineers.id"), primary_key=True)
    blueprint = relationship("EngineerBlueprint", lazy="joined")
    engineer = relationship("Engineer", lazy="joined")


class BlueprintIngredientLink(Base):
    __tablename__ = "blueprint_ingredient_link"

    id = Column(Integer, primary_key=True)
    blueprint_id = Column(Integer, ForeignKey("engineer_blueprints.id"))
    ingredient_id = Column(Integer, ForeignKey("blueprint_ingredients.id"))
    quantity = Column(Integer)
    blueprint = relationship("EngineerBlueprint", lazy="joined")
    ingredient = relationship("BlueprintIngredient", lazy="joined")


class CommunityGoalStatus(Base):
    __tablename__ = "community_goals_status"

    id = Column(Integer, primary_key=True)
    last_update = Column(DateTime, nullable=False)
    is_finished = Column(Boolean, nullable=False)
    current_tier = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)


class ModuleGroup(Base):
    __tablename__ = "modules_groups"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=False)

    def get_api_model(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "category": self.category,
        }


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True)
    module_class = Column(Integer, nullable=False)
    rating = Column(Text, nullable=False)
    price = Column(BigInteger, nullable=True)

    group_id = Column(Integer, ForeignKey("modules_groups.id"))
    group = relationship("ModuleGroup", lazy="joined")

    def get_api_model(self):
        return {
            "id": self.id,
            "module_class": self.module_class,
            "rating": self.module_class,
            "price": self.price,
            "group": self.group.get_api_model(),
        }


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
