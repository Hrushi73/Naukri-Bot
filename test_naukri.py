from playwright.sync_api import sync_playwright
import time


def select_job_checkboxes(page, max_jobs=5):
    """Select up to 5 job checkboxes"""
    # Wait for job listings to be visible
    page.wait_for_selector("article.jobTuple", timeout=10000)

    # Find all job checkboxes
    checkboxes = page.query_selector_all("article.jobTuple .naukicon-ot-checkbox")
    print(f"Found {len(checkboxes)} job checkboxes")

    selected_count = 0
    for i, checkbox in enumerate(checkboxes[:max_jobs]):
        try:
            # Check if checkbox is already selected
            is_checked = checkbox.get_attribute(
                "class"
            ) and "checked" in checkbox.get_attribute("class")

            if not is_checked:
                # Click the checkbox to select it
                checkbox.click()
                selected_count += 1
                print(f"Selected job {i+1}")

                # Small delay between selections
                page.wait_for_timeout(100)

        except Exception as e:
            print(f"Error selecting job {i+1}: {e}")
            continue

    print(f"Successfully selected {selected_count} jobs")
    return selected_count


def apply_to_selected_jobs(page):
    """Apply to all selected jobs"""
    try:
        # Use the exact selector from the Naukri.com page structure
        # Based on the screenshot: button.multi-apply-button.typ-16Bold
        apply_selectors = [
            "button.multi-apply-button.typ-16Bold",
            "button.multi-apply-button",
            ".multi-apply-button",
            'button:has-text("Apply")',
            'button:has-text("Apply to Selected")',
        ]

        apply_button = None
        for selector in apply_selectors:
            try:
                apply_button = page.query_selector(selector)
                if apply_button and apply_button.is_visible():
                    print(f"Found apply button with selector: {selector}")
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue

        if apply_button:
            # Get button text for verification
            button_text = apply_button.text_content().strip()
            print(f"Found apply button: '{button_text}'")

            apply_button.click()
            print("✓ Clicked apply button")
            page.wait_for_timeout(2000)

            # Handle post-apply questionnaire if it appears
            handle_post_apply_questionnaire(page)

        else:
            print("✗ Apply button not found with any selector")

    except Exception as e:
        print(f"Error applying to jobs: {e}")


def handle_post_apply_questionnaire(page):
    """Handle the questionnaire that appears after clicking apply"""
    try:
        print("Checking for post-apply questionnaire...")

        # Wait a bit for the questionnaire to appear
        page.wait_for_timeout(2000)

        # Look for the exact chatbot elements from the screenshot
        # Based on the HTML structure: div[id="_5ohx29qn2ChatbotContainer" class="_chatBotContainer"]
        chatbot_selectors = [
            'div[id*="ChatbotContainer"]',
            'div[class*="_chatBotContainer"]',
            'div[class*="chatbot_Drawer"]',
            'div[class*="chatbot_Overlay"]',
        ]

        chatbot_found = False

        for selector in chatbot_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    print(f"Found chatbot element: {selector}")
                    chatbot_found = True
                    break
            except:
                continue

        if chatbot_found:
            print("Chatbot questionnaire detected, attempting to answer questions...")
            answer_chatbot_questions(page)
        else:
            print("No chatbot questionnaire detected, application may be complete")

    except Exception as e:
        print(f"Error handling questionnaire: {e}")


def answer_chatbot_questions(page):
    """Answer the questions in the chatbot questionnaire"""
    try:
        print("Looking for chatbot questions and input fields...")

        max_questions = 10  # Prevent infinite loops
        question_count = 0

        while question_count < max_questions:
            question_count += 1
            print(f"\n--- Processing Question {question_count} ---")

            # Wait a bit for the next question to appear
            page.wait_for_timeout(1500)

            # First, find and read the bot's question/message
            bot_question = get_bot_question(page)

            if not bot_question:
                print("No more bot questions found - questionnaire may be complete")
                break

            print(f"Bot asked: '{bot_question}'")

            # Now find the input field to answer
            input_field = find_chatbot_input_field(page)

            if input_field:
                # Generate appropriate answer based on the bot's question
                answer = generate_answer_from_question(bot_question)

                if answer:
                    # Fill the input field with the answer
                    fill_chatbot_input_field(page, input_field, answer)

                    # Click the Save button
                    click_chatbot_save_button(page)

                    # Wait for the next question to appear (bot processes and shows next question)
                    print("Waiting for next question to appear...")
                    page.wait_for_timeout(3000)

                    # Check if we're done (success message like "thanks for applying")
                    if check_if_questionnaire_complete(page):
                        print("✓ Questionnaire completed successfully!")
                        print("✓ Application submitted - got final response from bot!")
                        break

                    # Additional check: look for the next question appearing
                    next_question = get_bot_question(page)
                    if next_question and next_question != bot_question:
                        print(f"✓ Next question detected: '{next_question[:50]}...'")
                    else:
                        print("Waiting for next question...")
                        # Give a bit more time for the next question
                        page.wait_for_timeout(2000)

                else:
                    print("Could not generate appropriate answer for the question")
                    break
            else:
                print("Chatbot input field not found")
                break

        if question_count >= max_questions:
            print(f"Reached maximum questions limit ({max_questions}). Stopping.")

    except Exception as e:
        print(f"Error answering chatbot questions: {e}")


def get_bot_question(page):
    """Extract the bot's question from the chatbot"""
    try:
        print("Looking for bot messages/questions...")

        # Look for bot messages based on the exact screenshot structure
        # Based on: div class="botMsg msg" within li class="botItem chatbot_ListItem"
        bot_message_selectors = [
            'div[class*="botMsg msg"]',
            'li[class*="botItem"] div[class*="msg"]',
            'li[class*="chatbot_ListItem"] div[class*="msg"]',
            'div[class*="chatbot_MessageContainer"] div[class*="botMsg"]',
            'div[class*="chatbot_MessageContainer"] div[class*="msg"]',
            'div[class*="botMsg"]',
            'div[class*="msg"]',
        ]

        bot_message = None
        for selector in bot_message_selectors:
            try:
                bot_message = page.query_selector(selector)
                if bot_message and bot_message.is_visible():
                    print(f"Found bot message with selector: {selector}")
                    break
            except:
                continue

        if bot_message:
            # Get the text content of the bot message
            question_text = bot_message.text_content().strip()
            print(f"Bot message content: '{question_text}'")
            return question_text
        else:
            print("No bot message found")
            return None

    except Exception as e:
        print(f"Error getting bot question: {e}")
        return None


def find_chatbot_input_field(page):
    """Find the chatbot input field for typing answers"""
    try:
        print("Looking for chatbot input field...")

        # Look for the exact input field from the screenshot
        # Based on the HTML: div[id="userInput_5ohx29qn2InputBox" class="textArea" contenteditable="true"]
        input_selectors = [
            'div[id*="userInput"][class*="textArea"]',  # Most specific - from screenshot
            'div[class*="textArea"][contenteditable="true"]',  # With contenteditable
            'div[class*="chatbot_InputContainer"] div[class*="textArea"]',  # Nested structure
            'div[id*="InputBox"][class*="textArea"]',  # Alternative with InputBox
            'div[class*="chatbot_InputContainer"]',  # Fallback
            'div[class*="InputContainer"]',  # Fallback
        ]

        input_field = None
        for selector in input_selectors:
            try:
                input_field = page.query_selector(selector)
                if input_field and input_field.is_visible():
                    print(f"Found chatbot input field with selector: {selector}")
                    return input_field
            except:
                continue

        print("Chatbot input field not found")
        return None

    except Exception as e:
        print(f"Error finding chatbot input field: {e}")
        return None


def generate_answer_from_question(question):
    """Generate appropriate answer based on the bot's question"""
    try:
        question_lower = question.lower()
        print(f"Analyzing question: '{question}'")

        # Check if it's asking for location
        if any(
            word in question_lower
            for word in [
                "location",
                "city",
                "address",
                "where",
                "current location",
                "preferred location",
            ]
        ):
            return "Pune"

        # Check if it's asking for experience
        elif any(
            word in question_lower
            for word in [
                "experience",
                "years",
                "exp",
                "yr",
                "work experience",
                "professional experience",
            ]
        ):
            return "3 years"

        # Check if it's asking for salary
        elif any(
            word in question_lower
            for word in [
                "salary",
                "ctc",
                "package",
                "lacs",
                "expectation",
                "expected salary",
                "salary expectation",
            ]
        ):
            return "12 Lacs"

        # Check if it's asking for skills
        elif any(
            word in question_lower
            for word in [
                "skill",
                "technology",
                "tech",
                "programming",
                "expertise",
                "technical skills",
                "programming skills",
            ]
        ):
            return "Java, Spring, Hibernate, SQL, React"

        # Check if it's asking for availability
        elif any(
            word in question_lower
            for word in [
                "available",
                "notice",
                "joining",
                "when",
                "availability",
                "notice period",
                "joining date",
            ]
        ):
            return "Immediate"

        # Check if it's asking for reason to apply
        elif any(
            word in question_lower
            for word in [
                "why",
                "reason",
                "motivation",
                "interest",
                "why apply",
                "why this position",
            ]
        ):
            return "I am interested in this position and believe my skills match the requirements perfectly."

        # Check if it's asking for confirmation
        elif any(
            word in question_lower
            for word in ["confirm", "agree", "yes", "no", "okay", "proceed"]
        ):
            return "Yes"

        # Check if it's asking for additional information
        elif any(
            word in question_lower
            for word in ["additional", "more", "other", "anything else", "comments"]
        ):
            return "No additional information at this time."

        # Default answer for unknown questions
        else:
            print(f"Unknown question type, providing default answer")
            return "Yes, I am interested in this position."

    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Yes, I am interested in this position."


def fill_chatbot_input_field(page, input_field, answer):
    """Fill the chatbot input field with the answer"""
    try:
        print(f"Filling input field with answer: '{answer}'")

        # Try to fill the input field
        try:
            input_field.fill(answer)
            print(f"✓ Filled input field: {answer}")
            page.wait_for_timeout(500)  # Wait for input to register

        except Exception as e:
            print(f"Error filling input field: {e}")
            # Try alternative approach - click and type
            try:
                input_field.click()
                page.wait_for_timeout(500)
                input_field.type(answer)
                print(f"✓ Filled input field (alternative method): {answer}")
                page.wait_for_timeout(500)

            except Exception as e2:
                print(f"Alternative method also failed: {e2}")
                raise e2

    except Exception as e:
        print(f"Error filling chatbot input field: {e}")
        raise e


def click_chatbot_save_button(page):
    """Click the Save button in the chatbot to submit the questionnaire"""
    try:
        print("Looking for chatbot Save button...")

        # Updated selector based on your screenshot
        save_selectors = [
            "div.sendMsgbtn_container div.sendMsg",  # Most specific - from screenshot
            'div[id*="sendMsgbtn_container"] div.sendMsg',  # Alternative with ID
            'div.sendMsg[tabindex="0"]',  # With tabindex attribute
            'div:has-text("Save")',  # Fallback
        ]

        save_button = None
        for selector in save_selectors:
            try:
                save_button = page.query_selector(selector)
                if save_button and save_button.is_visible():
                    print(f"Found chatbot save button with selector: {selector}")
                    break
            except:
                continue

        if save_button:
            button_text = save_button.text_content().strip()
            print(f"Found chatbot save button: '{button_text}'")
            save_button.click()
            print("✓ Clicked chatbot save button")
            page.wait_for_timeout(2000)
        else:
            print("✗ Chatbot save button not found")

    except Exception as e:
        print(f"Error clicking chatbot save button: {e}")


def check_if_questionnaire_complete(page):
    """Check if the questionnaire is complete (success message, no more questions, etc.)"""
    try:
        # Look for success messages or confirmations
        success_selectors = [
            'div:has-text("success")',
            'div:has-text("submitted")',
            'div:has-text("applied")',
            'div:has-text("thank you")',
            'div:has-text("received")',
            'div:has-text("completed")',
            'div:has-text("application submitted")',
            'div[class*="success"]',
            'div[class*="message"]',
            'div[class*="chatbot"]:has-text("success")',
            'div[class*="chatbot"]:has-text("submitted")',
            'div[class*="chatbot"]:has-text("applied")',
        ]

        for selector in success_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    text = element.text_content().strip()
                    if any(
                        word in text.lower()
                        for word in [
                            "success",
                            "submitted",
                            "applied",
                            "thank",
                            "received",
                            "completed",
                        ]
                    ):
                        print(f"✓ Found success message: {text}")
                        return True
            except:
                continue

        # Check if the chatbot interface has changed or disappeared
        chatbot_gone = page.query_selector('div[id*="ChatbotContainer"]')
        if not chatbot_gone or not chatbot_gone.is_visible():
            print("✓ Chatbot interface closed - application may be complete")
            return True

        # Check if there are no more input fields (questionnaire complete)
        input_field = find_chatbot_input_field(page)
        if not input_field:
            print("✓ No more input fields found - questionnaire may be complete")
            return True

        # Check if we're waiting for a response (bot is processing)
        if is_bot_processing(page):
            print("Bot is processing response, waiting...")
            return False

        return False

    except Exception as e:
        print(f"Error checking questionnaire completion: {e}")
        return False


def is_bot_processing(page):
    """Check if the bot is processing/typing a response"""
    try:
        # Look for typing indicators or processing messages
        processing_selectors = [
            'div:has-text("typing")',
            'div:has-text("processing")',
            'div:has-text("please wait")',
            'div[class*="typing"]',
            'div[class*="processing"]',
            'div[class*="loading"]',
        ]

        for selector in processing_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    return True
            except:
                continue

        return False

    except Exception as e:
        print(f"Error checking bot processing status: {e}")
        return False


def check_if_questionnaire_complete(page):
    """Check if the questionnaire is complete (success message, no more questions, etc.)"""
    try:
        # Look for success messages or confirmations
        success_selectors = [
            'div:has-text("success")',
            'div:has-text("submitted")',
            'div:has-text("applied")',
            'div:has-text("thank you")',
            'div:has-text("received")',
            'div:has-text("completed")',
            'div:has-text("application submitted")',
            'div[class*="success"]',
            'div[class*="message"]',
            'div[class*="chatbot"]:has-text("success")',
            'div[class*="chatbot"]:has-text("submitted")',
            'div[class*="chatbot"]:has-text("applied")',
        ]

        for selector in success_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    text = element.text_content().strip()
                    if any(
                        word in text.lower()
                        for word in [
                            "success",
                            "submitted",
                            "applied",
                            "thank",
                            "received",
                            "completed",
                        ]
                    ):
                        print(f"✓ Found success message: {text}")
                        return True
            except:
                continue

        # Check if the chatbot interface has changed or disappeared
        chatbot_gone = page.query_selector('div[id*="ChatbotContainer"]')
        if not chatbot_gone or not chatbot_gone.is_visible():
            print("✓ Chatbot interface closed - application may be complete")
            return True

        # Check if there are no more input fields (questionnaire complete)
        input_field = find_chatbot_input_field(page)
        if not input_field:
            print("✓ No more input fields found - questionnaire may be complete")
            return True

        # Check if we're waiting for a response (bot is processing)
        if is_bot_processing(page):
            print("Bot is processing response, waiting...")
            return False

        return False

    except Exception as e:
        print(f"Error checking questionnaire completion: {e}")
        return False


def is_bot_processing(page):
    """Check if the bot is processing/typing a response"""
    try:
        # Look for typing indicators or processing messages
        processing_selectors = [
            'div:has-text("typing")',
            'div:has-text("processing")',
            'div:has-text("please wait")',
            'div[class*="typing"]',
            'div[class*="processing"]',
            'div[class*="loading"]',
        ]

        for selector in processing_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    return True
            except:
                continue

        return False

    except Exception as e:
        print(f"Error checking bot processing status: {e}")
        return False


def check_chatbot_application_status(page):
    """Check if the chatbot application was submitted successfully"""
    try:
        print("Checking chatbot application status...")

        # Look for success messages or confirmations in the chatbot
        success_selectors = [
            'div:has-text("success")',
            'div:has-text("submitted")',
            'div:has-text("applied")',
            'div:has-text("thank you")',
            'div:has-text("received")',
            'div:has-text("completed")',
            'div[class*="success"]',
            'div[class*="message"]',
            'div[class*="chatbot"]:has-text("success")',
            'div[class*="chatbot"]:has-text("submitted")',
            'div[class*="chatbot"]:has-text("applied")',
        ]

        for selector in success_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    text = element.text_content().strip()
                    if any(
                        word in text.lower()
                        for word in [
                            "success",
                            "submitted",
                            "applied",
                            "thank",
                            "received",
                            "completed",
                        ]
                    ):
                        print(f"✓ Chatbot application submitted successfully: {text}")
                        return True
            except:
                continue

        # Check if the chatbot interface has changed or disappeared
        chatbot_gone = page.query_selector('div[id*="ChatbotContainer"]')
        if not chatbot_gone or not chatbot_gone.is_visible():
            print("✓ Chatbot interface closed - application may be complete")
            return True

        print("Chatbot application status unclear - may need manual verification")
        return False

    except Exception as e:
        print(f"Error checking chatbot application status: {e}")
        return False


def test_naukri_apply_recommended_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(
            "https://www.naukri.com/nlogin/login?URL=https://www.naukri.com/mnjuser/homepage"
        )
        assert "Login" in page.title()
        page.fill('input[id="usernameField"]', "hrushikeshmalshikare710@gmail.com")
        page.fill('input[id="passwordField"]', "Hrushi710@naukri")
        page.click('button[type="submit"]')
        page.wait_for_load_state("load")

        # Navigate to Recommended Jobs
        page.click("nav >> text=Jobs")
        # page.click('nav >> text=Recommended Jobs')
        page.wait_for_url("**/mnjuser/recommendedjobs")

        # Wait for the page to load and job listings to appear
        page.wait_for_selector(".sim-jobs", timeout=10000)
        page.wait_for_timeout(2000)  # Additional wait for dynamic content

        # Select job checkboxes (up to 5 as per the UI text)
        selected_jobs = select_job_checkboxes(page, max_jobs=5)

        if selected_jobs > 0:
            # Apply to selected jobs
            apply_to_selected_jobs(page)
        else:
            print("No jobs were selected")

        page.wait_for_timeout(3000)  # Keep browser open to see results

        browser.close()
