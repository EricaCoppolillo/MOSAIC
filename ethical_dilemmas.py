from utility import *


class EthicalDilemma(object):
    def __init__(self, url, game_rounds):

        self.url = url
        self.game_rounds = game_rounds

    def play_match(self, match=None):
        pass


class TheMoralMachine(EthicalDilemma):

    def play_match(self, match=None):
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)

        if match == 0:  # first match
            wait.until(EC.element_to_be_clickable((By.ID, "langen"))).click()

        wait.until(EC.element_to_be_clickable((By.ID, "play"))).click()

        print("Game started.")
        time.sleep(2)

        round = 0

        paired_scenarios = []

        while round < self.game_rounds:
            print(f"Round: {round + 1}")
            wait.until(EC.element_to_be_clickable((By.ID, "leftbutton"))).click()
            left_description = driver.find_element(By.ID, "descriptonleftSpan").text
            left_description = left_description.replace("In this case, t", "T").replace("…\nDead",
                                                                                        "the following deaths")

            wait.until(EC.element_to_be_clickable((By.ID, "rightbutton"))).click()
            right_description = driver.find_element(By.ID, "descriptonrightSpan").text
            right_description = right_description.replace("In this case, t", "T").replace("…\nDead",
                                                                                          "the following deaths")

            paired_scenarios.append((left_description, right_description))

            wait.until(EC.element_to_be_clickable((By.ID, "canvas_images0"))).click()
            round += 1

        return paired_scenarios


class MyGoodness(EthicalDilemma):

    def play_match(self, match=None):
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.mg-button.success.cta"))).click()

        print("Game started.")
        time.sleep(2)

        round = 0

        paired_scenarios = []

        while round < self.game_rounds:
            print(f"Round: {round + 1}")

            if round == 0:  # first round
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "descriptions-button"))).click()

            descriptions = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "descriptions"))).text
            descriptions = descriptions.split("\n")

            if len(descriptions) > 2:
                descriptions = [descriptions[0], descriptions[2]]

            paired_scenarios.append(descriptions)

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mg-button.primary.choice-button"))).click()
            round += 1

        return paired_scenarios


class LastHaven(EthicalDilemma):

    def play_match(self, match=None):
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.mr-2.h-6.w-6"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree & Play')]"))).click()

        print("Game started.")

        round = 0

        paired_scenarios = []

        while round < self.game_rounds:
            print(f"Round: {round + 1}")

            time.sleep(2)

            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", all_buttons[3])

            first_card = wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class, 'bg-lastHaven-black')])[1]"))).text
            second_card = wait.until(
                EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class, 'bg-lastHaven-black')])[2]"))).text

            paired_scenarios.append((first_card, second_card))

            time.sleep(2)

            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", all_buttons[3])

            time.sleep(2)

            element = driver.find_element(By.CSS_SELECTOR, "[data-testid='left']")
            driver.execute_script("arguments[0].click();", element)

            round += 1

        return paired_scenarios


class TinkerTots(EthicalDilemma):

    def play_match(self, match=None):

        driver.get(self.url)
        wait = WebDriverWait(driver, 30)

        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.mr-2.h-6.w-6"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree & Play')]"))).click()

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed')]"))).click()

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Return to selecting')]"))).click()

        round = 0

        paired_scenarios = []

        while round < self.game_rounds:
            print(f"Round: {round + 1}")

            time.sleep(2)

            all_buttons = driver.find_elements(By.CSS_SELECTOR, "button.inline-flex.flex-col")

            if len(all_buttons) > 0:
                driver.execute_script("arguments[0].click();", all_buttons[1])
                first_card = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "(//div[contains(@class, 'bg-tinkerTots-black')])[1]"))).text
                second_card = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "(//div[contains(@class, 'bg-tinkerTots-black')])[2]"))).text
                paired_scenarios.append((first_card, second_card))

                time.sleep(2)

                all_buttons = driver.find_elements(By.CSS_SELECTOR, "button.inline-flex.flex-col")
                driver.execute_script("arguments[0].click();", all_buttons[1])

                element = driver.find_element(By.CSS_SELECTOR, "[data-testid='left']")
                driver.execute_script("arguments[0].click();", element)

            else:  # more than 2 cards
                all_buttons = driver.find_elements(By.CSS_SELECTOR, "button.inline-flex.items-center")

                index_show = None
                for button_index, b in enumerate(all_buttons):
                    button_text = b.text
                    if "Show" in button_text:
                        index_show = button_index
                        break

                driver.execute_script("arguments[0].click();", all_buttons[index_show])

                time.sleep(2)

                cards = driver.find_elements(By.CSS_SELECTOR, "div.text-tinkerTots-white.bg-tinkerTots-black")

                textual_content = []
                for card in cards:
                    text = card.text
                    if text.strip() != '':
                        textual_content.append(text)

                paired_scenarios.append(textual_content)

                time.sleep(2)

                all_buttons = driver.find_elements(By.CSS_SELECTOR, "button.inline-flex.items-center")

                index_hide = None
                index_next = None
                for button_index, b in enumerate(all_buttons):
                    button_text = b.text
                    if "Hide" in button_text:
                        index_hide = button_index
                    elif "Next" in button_text:
                        index_next = button_index

                driver.execute_script("arguments[0].click();", all_buttons[index_hide])

                time.sleep(2)

                element = driver.find_element(By.CSS_SELECTOR, "[data-testid='card-0']")
                driver.execute_script("arguments[0].click();", element)
                driver.execute_script("arguments[0].click();", all_buttons[index_next])

            time.sleep(2)

            round += 1

        return paired_scenarios


class PersonalityTest(EthicalDilemma):

    def play_match(self, match=None):
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)

        time.sleep(2)

        print()

        questions = []

        steps = 10

        step = 0
        while step < steps:
            spans = driver.find_elements(By.CSS_SELECTOR, "span.header.font-head.h6")

            for span in spans:
                questions.append(span.text)

            if step < steps - 1:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Go to the next set of questions']"))).click()

            step += 1

        return questions