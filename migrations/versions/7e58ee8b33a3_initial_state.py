"""Initial state

Revision ID: 7e58ee8b33a3
Revises:
Create Date: 2020-06-23 13:56:50.534412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7e58ee8b33a3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "blueprint_ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "commodities_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "commodities_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("supply", sa.BigInteger(), nullable=True),
        sa.Column("buy_price", sa.Integer(), nullable=True),
        sa.Column("sell_price", sa.Integer(), nullable=True),
        sa.Column("demand", sa.BigInteger(), nullable=True),
        sa.Column("collected_at", sa.Integer(), nullable=True),
        sa.Column("commodity_id", sa.Integer(), nullable=True),
        sa.Column("station_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_commodities_prices_collected_at"),
        "commodities_prices",
        ["collected_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_commodities_prices_commodity_id"),
        "commodities_prices",
        ["commodity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_commodities_prices_station_id"),
        "commodities_prices",
        ["station_id"],
        unique=False,
    )
    op.create_table(
        "community_goals_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_update", sa.DateTime(), nullable=False),
        sa.Column("is_finished", sa.Boolean(), nullable=False),
        sa.Column("current_tier", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "engineer_blueprints",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "engineers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "modules_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "systems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("z", sa.Float(), nullable=False),
        sa.Column("permit_required", sa.Boolean(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("allegiance", sa.Text(), nullable=True),
        sa.Column("government", sa.Text(), nullable=True),
        sa.Column("security", sa.Text(), nullable=True),
        sa.Column("primary_economy", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.Column("population", sa.BigInteger(), nullable=True),
        sa.Column("power", sa.Text(), nullable=True),
        sa.Column("power_state", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "blueprint_engineer_link",
        sa.Column("blueprint_id", sa.Integer(), nullable=False),
        sa.Column("engineer_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["blueprint_id"], ["engineer_blueprints.id"],),
        sa.ForeignKeyConstraint(["engineer_id"], ["engineers.id"],),
        sa.PrimaryKeyConstraint("blueprint_id", "engineer_id"),
    )
    op.create_table(
        "blueprint_ingredient_link",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("blueprint_id", sa.Integer(), nullable=True),
        sa.Column("ingredient_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["blueprint_id"], ["engineer_blueprints.id"],),
        sa.ForeignKeyConstraint(["ingredient_id"], ["blueprint_ingredients.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "commodities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("internal_name", sa.Text(), nullable=False),
        sa.Column("average_price", sa.Integer(), nullable=True),
        sa.Column("is_rare", sa.Boolean(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["commodities_categories.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("module_class", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Text(), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["modules_groups.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "stations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("last_shipyard_update", sa.DateTime(), nullable=True),
        sa.Column("distance_to_star", sa.Integer(), nullable=True),
        sa.Column("max_landing_pad", sa.Text(), nullable=True),
        sa.Column("is_planetary", sa.Boolean(), nullable=False),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("system_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["system_id"], ["systems.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "station_module_link",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"],),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"],),
        sa.PrimaryKeyConstraint("station_id", "module_id"),
    )
    op.create_table(
        "station_ship_link",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("ship_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["ship_id"], ["ships.id"],),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"],),
        sa.PrimaryKeyConstraint("station_id", "ship_id"),
    )


def downgrade():
    op.drop_table("station_ship_link")
    op.drop_table("station_module_link")
    op.drop_table("stations")
    op.drop_table("modules")
    op.drop_table("commodities")
    op.drop_table("blueprint_ingredient_link")
    op.drop_table("blueprint_engineer_link")
    op.drop_table("systems")
    op.drop_table("ships")
    op.drop_table("modules_groups")
    op.drop_table("engineers")
    op.drop_table("engineer_blueprints")
    op.drop_table("community_goals_status")
    op.drop_index(
        op.f("ix_commodities_prices_station_id"), table_name="commodities_prices"
    )
    op.drop_index(
        op.f("ix_commodities_prices_commodity_id"), table_name="commodities_prices"
    )
    op.drop_index(
        op.f("ix_commodities_prices_collected_at"), table_name="commodities_prices"
    )
    op.drop_table("commodities_prices")
    op.drop_table("commodities_categories")
    op.drop_table("blueprint_ingredients")
    # ### end Alembic commands ###
