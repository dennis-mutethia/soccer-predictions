import os, uuid, requests, psycopg2
from dotenv import load_dotenv

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
    
    
            
    def add_jackpot_selectionss(self, jackpot_selections):         
        self.ensure_connection()
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO jackpot_selections(id, provider, event_id, start_date, home, away, home_odds, draw_odds, away_odds, created_at)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            for selection in jackpot_selections:
                cur.execute(query, (selection.id, selection.provider, selection.event_id, selection.start_date, selection.home, selection.away, selection.home_odds, selection.draw_odds, selection.away_odds)) 
                
            self.conn.commit()
            self.conn.close()
                  
                        
# Example usage:
if __name__ == "__main__":
    crud = PostgresCRUD()