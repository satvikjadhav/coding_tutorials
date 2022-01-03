from datetime import datetime, timedelta
from textwrap import dedent
from jugaad_trader import Zerodha
import pandas as pd
import sqlalchemy
import config

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

####################################################
# 1. DEFINE PYTHON FUNCTIONS
####################################################
kite = Zerodha(user_id=config.USERNAME, password=config.PASS, twofa=config.TWOFA)
kite.login()

# instrument = kite.instruments(exchange='NFO')

def get_stock_data():
    # instrument tokens: 1510401 - Axis Bank, 340481 - HDFC Bank, 5215745 - Coal India, 492033 - Kotak Bank
    print('1 Fetching stock prices')
    instrument_token_list = [1510401, 340481, 5215745, 492033]

    df_list = []

    for token in instrument_token_list:
        data = kite.historical_data(instrument_token=token,
                                    from_date=datetime.today() - timedelta(minutes=1080),
                                    to_date=datetime.today(),
                                    interval='minute')
        # temp_df = pd.DataFrame(data)
        # print(temp_df)
        # dataframe_list.append(temp_df, ignore_index=True)
        for i in range(len(data)):
            df_list.append(data[i])

    final_df = pd.DataFrame(data=df_list)

    print('Creating stock_list csv file')
    print(final_df.head(5))
    final_df.to_csv('stock_list.csv', index=False)
    print('Completed \n\n')


def transform_stock_data():
    print('2 Pulling stocks_prices ')
    # stocks_prices = ti.xcom_pull(
    #     task_ids='extract_data')  # <-- xcom_pull is used to pull the stocks_prices list generated above
    stock_dataframe = pd.read_csv('stock_list.csv')
    # stock_dataframe = pd.concat(stocks_prices, ignore_index=True)
    stock_dataframe['average_price'] = stock_dataframe.iloc[:, 1:4].astype(float).mean(axis=1)
    stock_dataframe['traded_value'] = stock_dataframe['average_price'] * stock_dataframe['volume']

    print('DF Shape: ', stock_dataframe.shape)
    print(stock_dataframe.head(5))

    stock_dataframe.to_csv('stock_list_transformed.csv', index=False)
    print('Completed \n\n')


def load_stock_data():
    print('3 Loading Stock Data into Database ')
    # ti = kwargs['ti']
    # stock_price_final = ti.xcom_pull(task_ids='transform_data')  # <-- xcom_pull is used to pull the stocks_prices list generated above

    stock_price_final = pd.read_csv('stock_list_transformed.csv')
    # DB connection details
    host = config.DBHOST'soulreaper.mysql.pythonanywhere-services.com'
    database = config.DATABASE'soulreaper$stockdata'
    user = config.DBUSER
    password = config.DBPASS
    port = config.DBPORT

    engine = sqlalchemy.create_engine(f'mysql+mysqldb://{user}:{password}@{host}:{port}/{database}',
                                      pool_recycle=280)

    stock_price_final.to_sql(con=engine, name='stock_data', if_exists='append', index=False)

    print('Completed')


############################################
# 2. DEFINE AIRFLOW DAG (SETTINGS + SCHEDULE)
############################################

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'satvikjadhav',
    'depends_on_past': False,
    'email': ['test@test.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

with DAG(
        'stock_data_ETL',
        default_args=default_args,
        description='A simple pipeline to get stock data, transform it, and load it in a databse',
        schedule_interval='0 4 * * *',
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['stock_pipeline']
) as dag:
    extract = PythonOperator(
        task_id='extract_data',
        python_callable=get_stock_data,
        dag=dag
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_stock_data,
        dag=dag
    )

    load = PythonOperator(
        task_id='load_data',
        python_callable=load_stock_data,
        dag=dag
    )

    extract >> transform >> load
