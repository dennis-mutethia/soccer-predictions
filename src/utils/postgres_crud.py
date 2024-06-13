import psycopg2, uuid

class PostgresCRUD:
    def __init__(self):
        db_host = 'aws-0-eu-central-1.pooler.supabase.com'
        db_name = 'postgres'
        db_port = '6543'
        db_user = 'postgres.rjqbkiuwthhyriaybcpr'
        db_pass = 'Mmxsp65$$$Mmxsp65'
        
        try:
            self.conn = psycopg2.connect(database=db_name, user=db_user, password=db_pass, host=db_host, port=db_port)   
            
        except Exception as e:
            print(f'An error occurred: {e}')

    def insert_match(self, match):
        start_time = match['start_time']
        start_date = start_time.date()
        home_team = match['home_team'].replace("'","''")
        away_team = match['away_team'].replace("'","''")
        prediction = match['prediction']
        match_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{start_date}{home_team}{away_team}'))
        odd = match['odd']
        match_url = match['match_url']
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
        home_results = match['home_results'] if match['home_results'] is not None else 'NULL'
        away_results = match['away_results'] if match['away_results'] is not None else 'NULL'
        analysis = match['analysis'].replace("'","''")
          
        cur = self.conn.cursor()
        query = f"""
            INSERT INTO matches(match_id,kickoff,home_team,away_team,prediction,odd,match_url,meetings,average_goals_home,average_goals_away,overall_prob,
            over_0_5_home_perc,over_0_5_away_perc,over_1_5_home_perc,over_1_5_away_perc,over_2_5_home_perc,over_2_5_away_perc,over_3_5_home_perc,over_3_5_away_perc,analysis)
            VALUES('{match_id}','{start_time}','{home_team}','{away_team}','{prediction}',{odd}, '{match_url}',{meetings}, {average_goals_home},{average_goals_away},{overall_prob},
            {over_0_5_home_perc},{over_0_5_away_perc},{over_1_5_home_perc},{over_1_5_away_perc},{over_2_5_home_perc},{over_2_5_away_perc},{over_3_5_home_perc},{over_3_5_away_perc},
            '{analysis}')
            ON CONFLICT (match_id) DO UPDATE SET
                home_results = {home_results},
                away_results = {away_results},
                prediction = '{prediction}',
                overall_prob = {overall_prob},
                analysis = '{analysis}';
        """
        
        cur.execute(query)
        self.conn.commit()
        
        #self.conn.close()
    
    def insert_betslip(self, match_id, profile_id):
        betslip_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{match_id}{profile_id}'))
        with self.conn.cursor() as cur:
            query = f"""
                INSERT INTO betslips(betslip_id,match_id,profile_id)
                VALUES('{betslip_id}','{match_id}','{profile_id}')
                ON CONFLICT (betslip_id) DO NOTHING;
            """
            
            cur.execute(query)
            self.conn.commit()
            
    def update_placed(self, match_id):
        with self.conn.cursor() as cur:
            query = f"""
                UPDATE matches
                SET placed=1
                WHERE match_id = '{match_id}'
            """
            
            cur.execute(query)
            self.conn.commit()
          
    def is_placed(self, match_id):
        with self.conn.cursor() as cur:
            query = """
                SELECT COUNT(*) 
                FROM betslips
                WHERE match_id = %s;
            """
            cur.execute(query, (match_id,))
            data = cur.fetchone()[0]
            return data != 0
      
# Example usage:
if __name__ == "__main__":
    crud = PostgresCRUD()