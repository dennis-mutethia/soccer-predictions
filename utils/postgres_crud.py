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
        
        print(self.conn_params)
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
            
    def update_match(self, params):
        try:
            url = f"https://tipspesa.uk/match-update?{params}"
                        
            headers = {
                "Accept": "application/json",
                "User-Agent": "PostmanRuntime/7.32.2"
            }

            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                #reponse_json = json.loads(response.content)
                print('Received json')
                print(response.content)
                
            else:
                error_response = response.text
                # Process the error response if needed
                print(f"Error: {error_response}")

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            
    def insert_match(self, match):
        start_time = match['start_time']
        start_date = start_time.date()
        home_team = match['home_team'].replace("'","''")
        away_team = match['away_team'].replace("'","''")
        prediction = match['prediction']
        match_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{start_date}{home_team}{away_team}'))
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
        
        params = f'update_predictions=true&match_id={match_id}&kickoff={start_time}&home_team={home_team}&away_team={away_team}&prediction={prediction}&odd={odd}&match_url={match_url}&meetings={meetings}&average_goals_home={average_goals_home}&average_goals_away={average_goals_away}&overall_prob={overall_prob}&over_0_5_home_perc={over_0_5_home_perc}&over_0_5_away_perc={over_0_5_away_perc}&over_1_5_home_perc={over_1_5_home_perc}&over_1_5_away_perc={over_1_5_away_perc}&over_2_5_home_perc={over_2_5_home_perc}&over_2_5_away_perc={over_2_5_away_perc}&over_3_5_home_perc={over_3_5_home_perc}&over_3_5_away_perc={over_3_5_away_perc}&analysis={analysis}' 
        self.update_match(params)   
        
        analysis = match['analysis'].replace("'","''")
        
        self.ensure_connection()
        with self.conn.cursor() as cursor:
            query = f"""
                INSERT INTO matches(match_id,kickoff,home_team,away_team,prediction,odd,match_url,meetings,average_goals_home,average_goals_away,overall_prob,
                over_0_5_home_perc,over_0_5_away_perc,over_1_5_home_perc,over_1_5_away_perc,over_2_5_home_perc,over_2_5_away_perc,over_3_5_home_perc,over_3_5_away_perc,analysis)
                VALUES('{match_id}','{start_time}','{home_team}','{away_team}','{prediction}',{odd}, '{match_url}',{meetings}, {average_goals_home},{average_goals_away},{overall_prob},
                {over_0_5_home_perc},{over_0_5_away_perc},{over_1_5_home_perc},{over_1_5_away_perc},{over_2_5_home_perc},{over_2_5_away_perc},{over_3_5_home_perc},{over_3_5_away_perc},
                '{analysis}')
                ON CONFLICT (match_id) DO UPDATE SET
                    prediction = '{prediction}',
                    overall_prob = {overall_prob},
                    analysis = '{analysis}';
            """
        
            cursor.execute(query)
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
        params = f'update_results=true&match_id={match_id}&home_results={home_results}&away_results={away_results}&status={status}' 
        self.update_match(params)   
        
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
               
# Example usage:
if __name__ == "__main__":
    crud = PostgresCRUD()