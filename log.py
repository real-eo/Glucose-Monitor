# ! NOTE: This is a terrible log implementation, but cba, because it's good enough
from constants import WARNING
from datetime import datetime
import logging


# Create a unique log filename based on current date and time
logFilename = f"logs/log-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.ERROR,
    filename=logFilename,
    filemode='w',
    format='[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

print(WARNING, "Program crashed!")
print(WARNING, "New log file created at: \"%s\"" % logFilename)
