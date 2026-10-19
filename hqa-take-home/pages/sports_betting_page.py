"""Desktop bet-slip interactions. Locators use the ids rendered by the app."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.constants import BASE_URL, EMPTY_SLIP_COPY


class SportsBettingPage:
    def __init__(self, driver, user_id: str, base_url: str = BASE_URL):
        self.driver = driver
        self.user_id = user_id
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        self.driver.get(f"{self.base_url}/?user-id={self.user_id}")
        self.wait.until(
            lambda d: d.find_elements(By.ID, "auth-error")
            or d.find_elements(By.CSS_SELECTOR, "#match-list .matchCard")
        )
        auth_error = self.driver.find_elements(By.ID, "auth-error")
        if auth_error:
            raise AssertionError(auth_error[0].text)
        return self

    def header_balance_text(self) -> str:
        # The pill also contains the wallet icon name, so read the span that shows the amount.
        for span in self.driver.find_elements(By.CSS_SELECTOR, "#header-balance span"):
            if "Balance" in span.text:
                return span.text
        return self.driver.find_element(By.ID, "header-balance").text

    def first_match(self):
        card = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#match-list .matchCard"))
        )
        names = card.find_elements(By.CSS_SELECTOR, ".teamName")
        home_button = card.find_element(By.XPATH, ".//button[.//span[normalize-space()='1']]")
        return {
            "card": card,
            "home_team": names[0].text.strip(),
            "away_team": names[1].text.strip(),
            "home_button": home_button,
            "home_odds": home_button.find_element(By.CSS_SELECTOR, ".oddsButtonValue").text.strip(),
        }

    def select_home(self, match):
        match["home_button"].click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".betSelectionCard")))
        return self

    def selection_text(self) -> str:
        return self.driver.find_element(By.CSS_SELECTOR, ".betSelectionMarket").text

    def selection_odds_text(self) -> str:
        return self.driver.find_element(By.CSS_SELECTOR, ".betSelectionOdds").text

    def enter_stake(self, stake: str):
        field = self.wait.until(EC.element_to_be_clickable((By.ID, "bet-slip-stake-input")))
        field.click()
        field.clear()
        field.send_keys(stake)
        return self

    def potential_payout_text(self) -> str:
        return self.driver.find_element(By.ID, "bet-slip-potential-payout").text

    def stake_warning_text(self):
        warnings = self.driver.find_elements(By.CSS_SELECTOR, ".stakeWarning")
        if not warnings:
            return None
        return warnings[0].text

    def place_bet_enabled(self) -> bool:
        return self.driver.find_element(By.ID, "bet-slip-place-bet").is_enabled()

    def place_bet(self):
        self.wait.until(lambda d: d.find_element(By.ID, "bet-slip-place-bet").is_enabled())
        self.driver.find_element(By.ID, "bet-slip-place-bet").click()
        return self

    def wait_for_receipt(self):
        # The client waits 1–4 seconds before it calls the API.
        self.wait.until(EC.visibility_of_element_located((By.ID, "modal-success")))
        return self

    def receipt(self) -> dict:
        def text(element_id):
            return self.driver.find_element(By.ID, element_id).text.strip()

        return {
            "bet_id": text("modal-success-bet-id"),
            "match": text("modal-success-match"),
            "stake": text("modal-success-stake"),
            "odds": text("modal-success-odds"),
            "payout": text("modal-success-payout"),
            "placed_at": text("modal-success-placed-at"),
        }

    def close_receipt(self):
        self.driver.find_element(By.ID, "modal-success-close").click()
        self.wait.until(EC.invisibility_of_element_located((By.ID, "modal-success")))
        return self

    def slip_is_empty(self) -> bool:
        count = self.driver.find_element(By.ID, "bet-slip-count").text.strip()
        body = self.driver.find_element(By.ID, "bet-slip").text
        return count == "0" and EMPTY_SLIP_COPY in body

    def success_modal_visible(self) -> bool:
        return bool(self.driver.find_elements(By.ID, "modal-success"))
