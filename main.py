from fastapi import FastAPI, HTTPException
from clickhouse_driver import Client
from typing import List

app = FastAPI()

# Connect to ClickHouse
try:
    # client = Client(host='localhost', database='default')
    client = Client(host='localhost', port=9000, database='default')
    client.execute('SELECT 1')  # Test connection
    print("Database connectedbbb successfully")
except Exception as e:
    print(f"Failedppppp to connect to ClickHouse: {e}")

# Helper Function to Execute Queries Safely
def execute_query(query: str, params: dict = None):
    try:
        print(f"query :{query}")
        return client.execute(query, params)
         
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/aggregate/calls", response_model=List[dict])
async def aggregate_calls(start_date: str, end_date: str):
    print(f"START ing.............. :{start_date}")
    query = """
    SELECT 
        call_drops_cnt AS CallDrop, 
        `Average_Call_Duration_minutes` AS CallDuration
    FROM calls_data1
    WHERE time_min BETWEEN toDateTime(%(start_date)s) AND toDateTime(%(end_date)s);
    """
    params = {"start_date": start_date, "end_date": end_date}
    print(f"query :{query}")
    print(f"params :{params}")
    result = execute_query(query, params)
    return [{"CallDrop": row[0], "CallDuration": row[1]} for row in result]

@app.get("/aggregate/sms", response_model=List[dict])
async def aggregate_sms(start_date: str, end_date: str):
    query = """
    SELECT 
        mcc, 
        mnc, 
        COUNT(sms_attempts) AS total_sms_attempts, 
        AVG(sms_long_completion_time) AS avg_sms_completion_time
    FROM sms_data
    WHERE time BETWEEN toDate(%(start_date)s) AND toDate(%(end_date)s)
    GROUP BY mcc, mnc;
    """
    params = {"start_date": start_date, "end_date": end_date}
    result = execute_query(query, params)
    return [
        {"mcc": row[0], "mnc": row[1], "total_sms_attempts": row[2], "avg_sms_completion_time": row[3]}
        for row in result
    ]
