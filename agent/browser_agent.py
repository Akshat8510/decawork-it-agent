import asyncio
import os
import re
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("FLASK_BASE_URL", "http://127.0.0.1:5000")

async def run_task(task: str, headless: bool = False) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        # --- FIX: SMART EMAIL EXTRACTION ---
        # We find the email and strip any trailing dots or punctuation
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', task)
        target_email = email_match.group(0).rstrip('.,! ') if email_match else "alice@company.com"
        
        print(f"[Agent] Observation: Navigating to {BASE_URL}")
        await page.goto(BASE_URL)
        task_lower = task.lower()

        try:
            # ── 1. ACTION: RESET PASSWORD ──────────────────────────
            if "reset" in task_lower and "password" in task_lower:
                print(f"[Agent] Intent: Password Reset for {target_email}")
                await page.get_by_role("link", name="User Management").click()
                
                # Navigate to the correct page and wait for it to load
                await page.wait_for_load_state("networkidle")
                
                # Find the dropdown in the 'Reset Password' sidebar card
                print(f"[Agent] Selecting {target_email} in the sidebar...")
                dropdown = page.get_by_role("combobox").first
                
                # We use 'value' selection which is faster and ignores the visible text format
                await dropdown.select_option(value=target_email)

                await asyncio.sleep(1)
                await page.get_by_role("button", name="Reset Password").click()
                
                # Wait for the flash message to appear
                await page.wait_for_selector(".flash")
                result = await page.locator(".flash").first.inner_text()
                return f"SUCCESS: {result.strip()}"

            # ── 2. ACTION: CREATE USER ─────────────────────────────
            elif "create" in task_lower or "new user" in task_lower:
                print("[Agent] Intent: User Creation")
                await page.get_by_role("link", name="User Management").click()
                await page.wait_for_load_state("networkidle")

                await page.get_by_placeholder("Jane Doe").fill("Carol Williams")
                await page.get_by_placeholder("jane@company.com").fill("carol@company.com")
                await page.get_by_placeholder("Engineer").fill("DevOps Engineer")
                
                await asyncio.sleep(1)
                await page.get_by_role("button", name="Create User").click()
                
                await page.wait_for_selector(".flash")
                result = await page.locator(".flash").first.inner_text()
                return f"SUCCESS: {result.strip()}"

            # ── 3. ACTION: DISABLE/ENABLE ──────────────────────────
            elif "disable" in task_lower or "enable" in task_lower:
                print(f"[Agent] Intent: Toggle Status for {target_email}")
                await page.get_by_role("link", name="User Management").click()
                await page.wait_for_load_state("networkidle")
                
                # The Toggle Status dropdown is the THIRD combobox in your sidebar
                dropdown = page.get_by_role("combobox").nth(2)
                await dropdown.select_option(value=target_email)
                
                await asyncio.sleep(1)
                await page.get_by_role("button", name="Toggle Status").click()
                
                await page.wait_for_selector(".flash")
                result = await page.locator(".flash").first.inner_text()
                return f"SUCCESS: {result.strip()}"

            else:
                return "Agent: Instruction received but no matching pattern found."

        except Exception as e:
            return f"Agent Execution Error: {str(e)}"
        finally:
            await asyncio.sleep(2) 
            await browser.close()

def run(task: str, headless: bool = False) -> str:
    return asyncio.run(run_task(task, headless=headless))