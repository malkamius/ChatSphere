
import threading
import mysql.connector
import time
from filelock import FileLock, Timeout
from datetime import datetime
import uuid
import socket

import sys
import os

from TextGenerator import TextGenerator
#shared_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))

## Add the parent directory to sys.path
#sys.path.insert(1, shared_dir)

from shared.config import DevelopmentConfig
from shared.ansi_logger import getLogger
    
# Configure the logging
# logging.basicConfig(level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')




def fetch_pending_requests(config, batch_size):
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, session_id, user_id, request_text, generated_text FROM requests WHERE status = 'pending' ORDER BY created_at LIMIT %s FOR UPDATE", 
        (batch_size,)
    )
    requests = cursor.fetchall()
    request_ids = [request['id'] for request in requests]
    if request_ids:
        cursor.execute(
            "UPDATE requests SET status = 'processing', locked_at = NOW() WHERE id IN (%s)" % ','.join(map(str, request_ids))
        )
        connection.commit()
    cursor.close()
    connection.close()
    return requests

def fetch_previous_messages(config, session_id):
    
    connection = config.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT request_text, generated_text FROM requests WHERE session_id = %s AND status = 'completed' ORDER BY created_at DESC",
        (session_id,)
    )
    messages = cursor.fetchall()
    cursor.close()
    connection.close()

    combined_messages = []
    total_length = 0

    for msg in messages:
        user_message = {'role': 'user', 'content': msg['request_text']}
        assistant_message = {'role': 'assistant', 'content': msg['generated_text']}
        
        # Add the user message
        total_length += len(user_message['content'])
        if total_length <= 10000:
            combined_messages.insert(0, user_message)
        else:
            break
        
        # Add the assistant message
        total_length += len(assistant_message['content'])
        if total_length <= 10000:
            combined_messages.insert(0, assistant_message)
        else:
            break

    return combined_messages

def update_response_and_request(config, request_id, generated_text, is_complete):

    connection = config.get_db_connection()
    cursor = connection.cursor()
    status = 'completed' if is_complete else 'pending'
    locked_at = 'NULL' if status == 'completed' else 'NOW()'
    cursor.execute(
        f"UPDATE requests SET generated_text = CONCAT(generated_text, %s), token_count = token_count + %s, is_complete = %s, status = %s, locked_at = {locked_at}, updated_at = NOW() WHERE id = %s",
        (generated_text, len(generated_text.split()), is_complete, status, request_id)
    )
    connection.commit()
    cursor.close()
    connection.close()

def cleanup_stale_requests(config):

    connection = config.get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE requests
        SET status = 'pending', locked_at = NULL
        WHERE status = 'processing' AND locked_at < NOW() - INTERVAL 15 MINUTE
        """
    )
    connection.commit()
    cursor.close()
    connection.close()

def process_requests(config, logger):
    logger.info("\033[1;32mInitializing LLM Pipeline, this could take some time.\033[0m");
    text_generator = TextGenerator(config)
    batch_size = 10
    last_cleanup_time = time.time()
    cleanup_interval = 300  # 5 minutes in seconds
    max_new_tokens_per_request = 10
    logger.info("\033[1;32mLLM Initialized, checking for requests.\033[0m");
    while True:
        current_time = time.time()
        if current_time - last_cleanup_time > cleanup_interval:
            cleanup_stale_requests(config)
            last_cleanup_time = current_time
            
        requests = fetch_pending_requests(config, batch_size)
        
        if not requests:
            time.sleep(0.5)
            continue  # Skip to the next iteration if no requests are found
        
        num_requests = len(requests);
        logger.info(f"Gathering messages for {num_requests} requests.");
        
        messages_batch = []
        for request in requests:
            session_id = request['session_id']
            request_id = request['id']
            request_text = request['request_text']
            last_text = request['generated_text']
            user_message = {'role': 'user', 'content': request_text}
            
            previous_messages = fetch_previous_messages(config, session_id)
            previous_messages.insert(0, user_message)
            
            messages_batch.append({
                'request_id': request_id,
                'session_id': session_id,
                'messages': previous_messages,
                'lasttext': last_text
            })
        logger.info(f"Sending {num_requests} to the generator.");
        generated_texts = text_generator.generate_batch(messages_batch, max_new_tokens_per_request)
        for i, request in enumerate(requests):
            generated_text = generated_texts[i]
            request_id = request['id']
            is_complete = generated_text == "" or str.endswith(generated_text, "--end of text--")  # Implement your logic to determine if the response is complete
            update_response_and_request(config, request_id, generated_text, is_complete)
        logger.info(f"Done generating (max of {max_new_tokens_per_request} per request) new tokens for {num_requests} requests.");

def run():
    lockfile = "process.lock"
    lock = FileLock(lockfile, timeout=1)

    # Get the fully qualified domain name
    fqdn = socket.getfqdn()

    # Print the fully qualified domain name
    print(f"The fully qualified domain name is: {fqdn}")

    namespace = uuid.NAMESPACE_DNS
    guid = uuid.uuid3(namespace, fqdn)

    # Print the GUID
    print(f"Generated GUID: {guid}")

    config = DevelopmentConfig()

    logger = getLogger(config, __name__)
        
    # Get the current time
    current_time = datetime.now()

    try:
        with lock:
            try:
                process_requests(config, logger)  # For example, your main process function
            finally:
                logger.info("\033[1;33mPerforming cleanup...\033[0m");
    except Timeout:
        logger.error("\033[1;31mAnother instance is already running.\033[0m")
    except KeyboardInterrupt:
        logger.error("\033[1;31mProgram interrupted.\033[0m")
    finally:
        #logging.info("Performing cleanup...")
        #todo lock requests with pid? set them to not locked?
        #logging.info("Cleanup done.")
        logger.info("\033[1;31mExiting the program...\033[0m");
if __name__ == "__main__":
    run()