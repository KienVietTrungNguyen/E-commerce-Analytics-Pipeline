import logging
import os

def setup_logger(module_name: str, log_folder: str = 'log', log_filename: str = 'pipeline.log') -> logging.Logger:
    """
    Sets up and returns a centralized logger instance.
    This logger will write to both the console (terminal) and a file.
    Args:
        module_name (str): The name of the module calling the logger (usually **name**).
        log_folder (str): The directory where log files will be stored. Defaults to 'logs'.
        log_filename (str): The name of the log file. Defaults to 'pipeline.log'.
    Returns:
        logging.Logger: A configured logger instance.
    """ 

    # 1. Create the logs directory if it doesn't exist
    if not os.path.exists(log_folder):
        try:
            os.makedirs(log_folder)
        except OSError as e:
            print(f"Error creating log directory: {e}")
    #2. Define the Log Format (Time - Module - Level - Messeage)
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(messeage)s')
    #3 Get the logger instance
    logger =logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    # 4. Check if handlers already exist to avoid duplicate logs
    # (This prevents printing the same line twice if setup_logger is called multiple times)
    if not logger.handlers:
        
        #--- Handler 1: Write to File ---
        file_path = os.path.join(log_folder,log_filename)
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

        #--- Handler 2: Print to Console (Terminal) ---
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)
        
    return logger
    