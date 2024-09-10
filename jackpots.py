

from utils.jackpots.shabiki import Shabiki
from utils.postgres_crud import PostgresCRUD


class Jackpots():
    def __init__(self):
        self.shabiki = Shabiki()
        self.postgres_crud = PostgresCRUD()

    def __call__(self):
        selections = self.shabiki.get_jackpot_selections()
        self.postgres_crud.add_jackpot_selectionss(selections)
        

if __name__ == '__main__':
    Jackpots()()