import subprocess
import logging
import logging.config
import threading
from datetime import datetime
from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error
from bs4 import BeautifulSoup


def read_config_file(filename, section):
    """Read a configuration file and return a dictionary object

    Params:
        filename: name of the configuration file
        section: section of the file with the configuration
    Returns:
        config: a dictionary with the configuration
    """

    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    config = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            config[item[0]] = item[1]
    else:
        logging.warning(f'{section} not found in the {filename} file')
        raise Exception(f'{section} not found in the {filename} file')

    return config


def initilize_logger(datetime):
    """Initialize the logging and logfile

    Args:
        datetime (datetime): current date and time

    Raises:
        Exception: If it can't configurate and create the log file
    """
    path = read_config_file('./config/config.ini', 'LOGGER').get('logger_path')
    yymmdd = datetime.strftime('%y%m%d')
    loggger_filename = f'{path}LOG{yymmdd}.log'

    try:
        logging.basicConfig(filename=loggger_filename,
                            format='%(asctime)s | %(levelname)s | %(message)s',
                            level=logging.DEBUG)
    except:
        raise Exception('Error while creating the log file...')


def save_to_db(date_time_exec, data):
    """Make the connection to the MySQL database and save the content

    Args:
        date_time_exec (string): the date and time when ran
        data (string): the content to save in the database
    """

    query = 'INSERT INTO consult_save(date_time_exec,data) VALUES(%s,%s)'
    args = (date_time_exec, data)

    try:
        db_config = read_config_file('./config/config.ini', 'DATABASE')
        connection = MySQLConnection(**db_config)

        if connection.is_connected():
            logging.info('Connection established...')

        try:
            cursor = connection.cursor()
            cursor.execute(query, args)
            connection.commit()
        except Error as error:
            logging.error('Error while insert the data...')
            raise Exception('Error while insert the data...', error)


    except Error as error:
        logging.error('Error while connecting to MySQL...')
        raise Exception('Error while connecting to MySQL...', error)

    finally:
        cursor.close()
        connection.close()
        logging.info('Database connection closed...')


def __get_website_content(url, connect_timeout):
    """Get the content of a website

    Args:
        url (str): url where to get the content
        connect_timeout (str): the time to wait for the website response. Wait seconds, for milliseconds use comma instead of period. E.g. 1 millisecond -> 0,001 seconds

    Raises:
        Exception: if it can't get the website content or the command fails

    Returns:
        str: the website content
    """
    try:
        curl_response = subprocess.Popen(['curl', '--connect-timeout', connect_timeout, url],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT) # if fails it's going to be show it in the STDOUT
    except:
        logging.error('Error while getting the website content...')
        raise Exception('Error while getting the website content...')

    stdout = curl_response.communicate()[0]
    data = stdout.decode('utf-8')

    return data


def __get_website_content_required(url, connect_timeout):
    """Get the piece of the content of the website that interests

    Args:
        url (str): url where to get the content
        connect_timeout (str): the time to wait for the website response. Wait seconds, for milliseconds use comma instead of period. E.g. 1 millisecond -> 0,001 seconds

    Returns:
        str: the content needed. Empty if 1) the content of the website is different than expected 2) The response is less faster than connect_timeout
    """
    content = __get_website_content(url, connect_timeout)

    # this can fail if the website content change
    if 'id="clock0_bg"' in content:
        soup = BeautifulSoup(content, 'lxml')

        title = soup.select('h1')[0].text.strip()
        clock = soup.select('time#clock')[0].text.strip()
        date = soup.select('div#dd')[0].text.strip()

        return f'{title} {clock} {date}'

    return ''


def exec_website_query(url, website_response_timeout, query_period, default_value_to_save):
    threading.Timer(float(query_period), exec_website_query, [url, website_response_timeout, query_period, default_value_to_save]).start()

    data_to_save = __get_website_content_required(url, website_response_timeout)

    if data_to_save != '':
        save_to_db(datetime.today(), data_to_save)
    else:
        save_to_db(datetime.today(), default_value_to_save)


def run():
    initilize_logger(datetime.today())
    query_website_configuration = read_config_file('./config/config.ini', 'QUERY_CONFIGURATION')
    exec_website_query(query_website_configuration.get('url'), \
                        query_website_configuration.get('website_response_timeout'), \
                        query_website_configuration.get('query_period'), \
                        query_website_configuration.get('default_value_to_save'))


if __name__ == '__main__':
    run()
