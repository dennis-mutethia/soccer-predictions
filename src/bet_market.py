class BetMarket:
    def __init__(self, data):        
        self.sub_type_id = data.get("sub_type_id")
        self.name = data.get("name")
        self.odds = [Odd(odd) for odd in data.get("odds")]    

class Odd:
    def __init__(self, odd):
        self.display = odd.get("display")
        self.odd_key = odd.get("odd_key")
        self.odd_def = odd.get("odd_def")
        self.odd_value = odd.get("odd_value")
        self.special_bet_value = odd.get("special_bet_value")
        self.outcome_id = odd.get("outcome_id")
        self.parsed_special_bet_value = odd.get("parsed_special_bet_value")