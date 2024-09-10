

from utils.jackpots.betika import Betika
from utils.jackpots.shabiki import Shabiki
from utils.postgres_crud import PostgresCRUD


class Jackpots():
    def __init__(self):
        self.shabiki = Shabiki()
        self.betika = Betika()
        self.postgres_crud = PostgresCRUD()

    def __call__(self):
        jackpots_shabiki = self.shabiki.get_jackpot_selections()
        jackpots_betika = self.betika.get_jackpot_selections()
        
        jackpots = jackpots_shabiki + jackpots_betika
        self.postgres_crud.add_jackpot_selections(jackpots)
        

if __name__ == '__main__':
    Jackpots()()