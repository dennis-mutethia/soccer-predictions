

from utils.jackpots.shabiki import Shabiki
from utils.postgres_crud import PostgresCRUD


class Jackpots():
    def __init__(self):
        self.shabiki = Shabiki()
        self.postgres_crud = PostgresCRUD()

    def __call__(self):
        jackpots = self.shabiki.get_jackpot_selections()
        self.postgres_crud.add_jackpot_selections(jackpots)
        

if __name__ == '__main__':
    Jackpots()()