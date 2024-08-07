
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
from TextGenerator.phi_text_generator import PhiTextGenerator
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
        placeholders = ','.join(['%s'] * len(request_ids))
        cursor.execute(
            f"UPDATE requests SET status = 'processing', locked_at = NOW() WHERE id IN ({placeholders})",
            request_ids
        )
        connection.commit()
    cursor.close()
    connection.close()
    return requests

def fetch_previous_messages(config, session_id):
    combined_messages = []
    try:
        connection = config.get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Use a server-side cursor to fetch rows one at a time
        cursor.execute(
            "SELECT request_text, generated_text FROM requests WHERE session_id = %s AND is_complete = 1 ORDER BY created_at DESC",
            (session_id,)
        )
        
        
        total_length = 0
        max_length = 10000

        for msg in cursor:
            # Add the user message
            request_text = msg['request_text'] or ''
            total_length += len(request_text)
            if total_length <= max_length:
                user_message = {'role': 'user', 'content': request_text}
                combined_messages.insert(0, user_message)
            else:
                break
            
            # Add the assistant message
            generated_text = msg['generated_text'] or ''
            total_length += len(generated_text)
            if total_length <= max_length:
                assistant_message = {'role': 'assistant', 'content': generated_text}
                combined_messages.insert(0, assistant_message)
            else:
                break
        connection.rollback()
        cursor.close()
        connection.close()

        return combined_messages

    except Exception as e:
        if connection:
            connection.close()
        print(f"An error occurred: {e}")
        return combined_messages

def update_response_and_request(config, request_id, generated_text, is_complete):

    connection = config.get_db_connection()
    cursor = connection.cursor()
    status = 'completed' if is_complete else 'pending'
    locked_at = 'NULL' if status == 'completed' else 'NOW()'
    cursor.execute(
            """
            UPDATE requests 
            SET 
                generated_text = CONCAT(COALESCE(generated_text, ''), %s), 
                token_count = token_count + %s, 
                is_complete = %s, 
                status = %s, 
                locked_at = CASE 
                           WHEN %s = 'completed' THEN NULL 
                           ELSE NOW() 
                        END, 
                updated_at = NOW() 
            WHERE 
                id = %s 
                AND is_complete = false
            """,
        (generated_text, len(generated_text.split()), is_complete, status, status, request_id)
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
    # text_generator = TextGenerator(config)
    text_generator = PhiTextGenerator(config)
    batch_size = 10
    last_cleanup_time = time.time()
    cleanup_interval = 15 
    max_new_tokens_per_request = 10
    logger.info("\033[1;32mLLM Initialized, checking for requests.\033[0m");
    cleanup_stale_requests(config)
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
            
            # messages should be handed to the LLM oldest first with the most recent
            # request at the end
            previous_messages.reverse()

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
            is_complete = generated_text == None or generated_text == "" or str.endswith(generated_text, "--end of text--")  # Implement your logic to determine if the response is complete
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