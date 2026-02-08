
import os

import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from fake_useragent import UserAgent

from selenium.webdriver.chrome.options import Options

from tqdm import tqdm

data_folder = os.path.join("data")
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

results_folder = os.path.join("results")
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

options = webdriver.ChromeOptions()
# options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

N_MATCHES = 10

PLATFORM_BASED_TESTS = ["the_moral_machine", "my_goodness", "last_haven", "tinker_tots"]