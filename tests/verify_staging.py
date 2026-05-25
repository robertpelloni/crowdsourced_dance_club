from playwright.sync_api import Page, expect, sync_playwright
import time
import subprocess
import os

def verify_staging_flow(page: Page):
    # Start server on a specific port for verification
    server_process = subprocess.Popen(["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"])
    time.sleep(5)

    try:
        page.goto("http://localhost:8004")

        # 1. User A Registration
        page.get_by_text("Need an account? Register").click()
        user_a = f"staging_a_{int(time.time())}"
        page.get_by_placeholder("Username").last.fill(user_a)
        page.get_by_placeholder("Password").last.fill("password123")
        page.get_by_role("button", name="REGISTER").click()

        # Login User A to get referral code
        page.get_by_placeholder("Username").first.fill(user_a)
        page.get_by_placeholder("Password").first.fill("password123")
        page.get_by_role("button", name="LOGIN").click()

        page.get_by_role("link", name="👤 Profile").click()
        ref_code = page.locator("#profile-referral-code").inner_text()
        print(f"User A Referral Code: {ref_code}")

        # Logout User A
        page.get_by_text("LOGOUT").click()

        # 2. User B Registration with User A's Code
        page.get_by_text("Need an account? Register").click()
        user_b = f"staging_b_{int(time.time())}"
        page.get_by_placeholder("Username").last.fill(user_b)
        page.get_by_placeholder("Password").last.fill("password123")
        page.get_by_placeholder("Referral Code (Optional)").fill(ref_code)
        page.get_by_role("button", name="REGISTER").click()

        # Login User B
        page.get_by_placeholder("Username").first.fill(user_b)
        page.get_by_placeholder("Password").first.fill("password123")
        page.get_by_role("button", name="LOGIN").click()

        # 3. User B: Request a Song
        page.get_by_role("link", name="🔍 Browse").click()
        page.get_by_role("button", name="＋").first.click()

        # 4. User B: Vote for a Song
        page.get_by_role("link", name="📋 Queue").click()
        page.get_by_role("button", name="▲").first.click()

        # 5. User B: Submit Feedback
        page.get_by_role("link", name="💬 Refine").click()
        # Rate Vibe (4 stars)
        page.locator("#rating-vibe .star-rating").nth(3).click()
        # Rate Tech (5 stars)
        page.locator("#rating-tech .star-rating").nth(4).click()
        page.get_by_placeholder("Any glitches or transition thoughts?").fill("Staging looks solid. Transitions were smooth during my session!")
        page.get_by_role("button", name="SUBMIT FEEDBACK").click()

        expect(page.get_by_text("Feedback submitted successfully")).to_be_visible()
        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/staging_validation.png")

    finally:
        server_process.terminate()

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_staging_flow(page)
        except Exception as e:
            print(f"Error during validation: {e}")
            os.makedirs("verification", exist_ok=True)
            page.screenshot(path="verification/staging_error.png")
        finally:
            browser.close()
