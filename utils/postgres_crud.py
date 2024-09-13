import os, uuid, psycopg2
from dotenv import load_dotenv
import pandas as pd

from utils.entities import Event, Jackpot, Odds

class PostgresCRUD:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.conn_params = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'port': os.getenv('DB_PORT'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
        self.conn = None
        self.ensure_connection()
    
    def ensure_connection(self):
        try:
            # Check if the connection is open
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(**self.conn_params)
            else:
                # Test the connection
                with self.conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
        except Exception as e:
            # Reconnect if the connection is invalid
            self.conn = psycopg2.connect(**self.conn_params)
          
    def insert_match(self, match):
        kickoff = match['start_time']
        home_team = match['home_team'].replace("'","''")
        away_team = match['away_team'].replace("'","''")
        prediction = match['prediction']
        match_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{kickoff.date()}{home_team}{away_team}'))
        odd = match['odd']
        match_url = match['match_url'].replace("#","*")
        meetings = match['meetings']
        average_goals_home = match['average_goals_home']
        average_goals_away = match['average_goals_away']
        overall_prob = match['overall_prob']
        over_0_5_home_perc = match['over_0_5_home_perc']
        over_0_5_away_perc = match['over_0_5_away_perc']
        over_1_5_home_perc = match['over_1_5_home_perc']
        over_1_5_away_perc = match['over_1_5_away_perc']
        over_2_5_home_perc = match['over_2_5_home_perc']
        over_2_5_away_perc = match['over_2_5_away_perc']
        over_3_5_home_perc = match['over_3_5_home_perc']
        over_3_5_away_perc = match['over_3_5_away_perc']
        analysis = match['analysis']        
        
        analysis = match['analysis'].replace("'","''")
        
        self.ensure_connection()
        with self.conn.cursor() as cursor:
            query = """
                INSERT INTO matches(match_id, kickoff, home_team, away_team, prediction, odd, match_url, meetings, average_goals_home, average_goals_away, overall_prob,
                over_0_5_home_perc, over_0_5_away_perc, over_1_5_home_perc, over_1_5_away_perc, over_2_5_home_perc, over_2_5_away_perc, over_3_5_home_perc, over_3_5_away_perc, analysis)
                VALUES(%s, %s + INTERVAL '2 hours', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id) DO UPDATE SET
                    kickoff = %s + INTERVAL '2 hours',
                    prediction = %s,
                    overall_prob = %s,
                    analysis = %s
            """
            cursor.execute(query, (match_id, kickoff, home_team, away_team, prediction, odd, match_url , meetings, average_goals_home, average_goals_away, overall_prob, 
                                   over_0_5_home_perc, over_0_5_away_perc, over_1_5_home_perc, over_1_5_away_perc, over_2_5_home_perc, over_2_5_away_perc, over_3_5_home_perc,
                                   over_3_5_away_perc, analysis, kickoff, prediction, overall_prob, analysis))
            self.conn.commit()
    
    def fetch_open_matches(self):
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                SELECT *
                FROM matches
                WHERE (status IS NULL OR status = 'LIVE')
                    AND DATE(kickoff) >= CURRENT_DATE - 1
            """
            cur.execute(query)
            return cur.fetchall()
    
    def fetch_matches(self, day, comparator, status): 
        self.ensure_connection()           
        with self.conn.cursor() as cur:
            query = f"""
                SELECT *
                FROM matches
                WHERE DATE(kickoff) {comparator} CURRENT_DATE {day} {status}
                ORDER BY status DESC
            """
            cur.execute(query)
            return cur.fetchall()
    
    def update_match_results(self, match_id, home_results, away_results, status):        
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                UPDATE matches SET
                    home_results = %s,
                    away_results = %s,
                    status = %s
                WHERE match_id = %s
            """
            
            cur.execute(query, (home_results, away_results, status, match_id)) 
            self.conn.commit()
    
        
    def fetch_subscribers(self, status):
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                SELECT phone
                FROM subscribers
                WHERE status = %s AND (last_delivered_at IS NULL OR DATE(last_delivered_at) < current_date)
            """
            cur.execute(query, (status,))
            return cur.fetchall()
    
    def add_or_remove_subscriber(self, phone, status=1):         
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO subscribers(phone, status, created_at)
                VALUES(%s, %s, NOW())
                ON CONFLICT (phone) DO UPDATE SET
                    status = %s,
                    last_delivered_at = NULL,
                    updated_at = NOW()
            """
            
            cur.execute(query, (phone, status, status)) 
            self.conn.commit()
         
    
    def update_subscriber_on_send(self, phone):         
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                UPDATE subscribers
                SET last_delivered_at=NOW()
                WHERE phone = %s
            """
            
            cur.execute(query, (phone,)) 
            self.conn.commit()
         
    
    def update_subscriber_on_dlr(self, phone):         
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                UPDATE subscribers
                SET last_delivered_at=NOW()
                WHERE phone = %s
            """
            
            cur.execute(query, (phone, )) 
            self.conn.commit()
    
                
    def add_jackpot_selections(self, jackpots):         
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO jackpot_selections(id, provider, event_id, start_date, home, away, home_odds, draw_odds, away_odds, created_at)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            for jackpot in jackpots:
                for event in jackpot.events:
                    for odds in event.odds:
                        cur.execute(query, (jackpot.id, jackpot.provider, event.id, event.start_date, event.home, event.away, odds.home_odds, odds.draw_odds, odds.away_odds)) 
                
            self.conn.commit()
            self.conn.close()
    
        
    def fetch_jackpots(self):
        self.ensure_connection()
        selections = []
        with self.conn.cursor() as cur:
            query = """
                SELECT DISTINCT id, provider
                FROM jackpot_selections
            """
            cur.execute(query)
            data = cur.fetchall()
            for datum in data:
                events = self.fetch_events(datum[0])
                selections.append(Jackpot(datum[0], datum[1], events))
                  
        return selections
      
    def fetch_events(self, jackpot_id):
        self.ensure_connection()
        events = []
        with self.conn.cursor() as cur:
            query = """
                SELECT DISTINCT event_id, start_date, home, away, prediction
                FROM jackpot_selections
                WHERE id = %s AND start_date > NOW()
            """
            cur.execute(query,(jackpot_id, ))
            data = cur.fetchall()
            for datum in data:
                odds = self.fetch_odds(datum[0])
                events.append(Event(datum[0], datum[1], datum[2], datum[3], odds, datum[4]))
                  
        return events
    
    def fetch_odds(self, event_id):
        self.ensure_connection()
        selection_odds = []
        with self.conn.cursor() as cur:
            query = """
                SELECT home_odds, draw_odds, away_odds, created_at
                FROM jackpot_selections
                WHERE event_id = %s
                ORDER BY created_at
            """
            cur.execute(query,(event_id,))
            data = cur.fetchall()
            for datum in data:
                selection_odds.append(Odds(datum[0], datum[1], datum[2], datum[3]))
            
        return selection_odds
    
    def fetch_all_odds(self):
        self.ensure_connection()
        query = """
            SELECT id, event_id, home_odds, draw_odds, away_odds, created_at
            FROM jackpot_selections
            ORDER BY created_at
        """
            
        return pd.read_sql_query(query, self.conn)
                
    def update_prediction_to_jackpot_selections(self, odds_df):         
        self.ensure_connection()
        with self.conn.cursor() as cur:
            for index, row in odds_df.iterrows():
                query = """
                UPDATE jackpot_selections
                SET prediction = %s
                WHERE id=%s AND event_id = %s 
                """
                cur.execute(query, (row['prediction'], row['id'], row['event_id']))
                
            self.conn.commit()
            self.conn.close()
    
                
# Example usage:
if __name__ == "__main__":
    crud = PostgresCRUD()