import os
import datetime
from guardian_auto import run_guardian

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.path.join(os.getcwd(),timestamp)
if not os.path.exists(folder_path):
   os.makedirs(timestamp)

run_guardian(folder_path,dur=60)
