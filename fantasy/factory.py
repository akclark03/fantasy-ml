from daos import Dao
from nfl import NFLStatsEtl


class MainFactory:
    def nfl_etl(self) -> NFLStatsEtl:
        return NFLStatsEtl()

    def dao(self) -> Dao:
        return Dao()


def main_factory() -> MainFactory:
    return MainFactory()
