from factory import main_factory
from predict import PassingPredictor


class Worker:
    def __init__(self) -> None:
        self.fac = main_factory()

    def stat_scrape(self) -> None:
        self.fac.nfl_etl().run(2022, 2023)

    def predict(self) -> None:
        PassingPredictor(self.fac.dao()).run()

    def train(self) -> None:
        self.fac.dao().train_passing_yds()


if __name__ == "__main__":
    worker = Worker()
    # worker.stat_scrape()
    worker.train()
    worker.predict()
