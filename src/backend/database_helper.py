import sqlite3

# open connection within environment, commit and close when run is finished, open connection on reset
# If run does not finish, try and close the connection before opening it within reset

sql_create_run_info = """
CREATE TABLE Model_Run_Info (
    Run_Number INTEGER,
    Boss_ID INTEGER,
    Boss_Ending_Health REAL,
    Player_Ending_Health REAL,
    Total_Time REAL,
    Victory BOOLEAN,
    PRIMARY KEY (Run_Number, Boss_ID),
    FOREIGN KEY (Boss_ID) REFERENCES Bosses(Boss_ID)
);
"""

sql_create_bosses = """
CREATE TABLE Bosses (
    Boss_ID INTEGER PRIMARY KEY,
    Attempts INTEGER,
    Wins INTEGER
);
"""

table_names = [
    ("Model_Run_Info", sql_create_run_info),
    ("Bosses", sql_create_bosses)
]

def validate_data(data: dict) -> None:
    for key in data:
        if data[key] is None:
            data[key] = 'NULL'

def create_database() -> None:
        con = sqlite3.connect("elden_ring.db")
        cur = con.cursor()

        for table_name, create_sql in table_names:
            try:
                cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if not cur.fetchone():
                    cur.execute(create_sql)
                    con.commit()
            except sqlite3.Error as e:
                print(f"Error creating table {table_name}: {e}")

        con.close()

def write_to_database_run(info: dict) -> None:
    # use info to write to run info
    # also write to bosses and increment attempts
    dbstr = f"""
    INSERT INTO Model_Run_Info (
    Run_Number,
    Boss_ID,
    Boss_Ending_Health,
    Player_Ending_Health,
    Total_Time,
    Victory) VALUES (
    {info["Run_Number"]},
    {info["Boss_ID"]},
    {info["Boss_Ending_Health"]},
    {info["Player_Ending_Health"]},
    {info["Total_Time"]},
    {info["Victory"]}
    );
    """

    con = sqlite3.connect("elden_ring.db")
    cur = con.cursor()
    cur.execute(dbstr)
    con.commit()
    con.close()

def increase_attempts(boss_id: int) -> None:
    # use info to write to bosses
    dbstr = f"""
    INSERT INTO Bosses (boss_id, attempts, wins) 
    VALUES ({boss_id}, 1, 0)
    ON CONFLICT(boss_id) DO UPDATE SET attempts = attempts + 1;
    """

    con = sqlite3.connect("elden_ring.db")
    cur = con.cursor()
    cur.execute(dbstr)
    con.commit()
    con.close()

def beat_boss(boss_id: int) -> None:
    dbstr = f"""
    UPDATE Bosses
    SET wins = wins + 1
    WHERE boss_id = {boss_id};
    """

    con = sqlite3.connect("elden_ring.db")
    cur = con.cursor()
    cur.execute(dbstr)
    con.commit()
    con.close()

def get_run_number() -> int:
    # get the largest run number from run info table
    con = sqlite3.connect("elden_ring.db")
    cur = con.cursor()
    cur.execute("SELECT COALESCE(MAX(Run_Number), 0) FROM Model_Run_Info;")
    run_number = cur.fetchone()[0]
    con.close()
    return run_number
