from playwright.sync_api import sync_playwright
from checkbox_utils import NaukriCheckboxHandler, select_java_developer_jobs, select_jobs_by_location, select_jobs_by_experience

def example_basic_checkbox_selection():
    """Basic example of selecting checkboxes"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Login to Naukri (you'll need to handle this)
        page.goto("https://www.naukri.com/nlogin/login?URL=https://www.naukri.com/mnjuser/homepage")
        
        # Fill in your credentials
        page.fill('input[id="usernameField"]', 'your_email@example.com')
        page.fill('input[id="passwordField"]', 'your_password')
        page.click('button[type="submit"]')
        page.wait_for_load_state('load')
        
        # Navigate to recommended jobs
        page.click('nav >> text=Jobs')
        page.wait_for_url("**/mnjuser/recommendedjobs")
        
        # Use the checkbox handler
        handler = NaukriCheckboxHandler(page)
        
        # Wait for jobs to load
        handler.wait_for_jobs_to_load()
        
        # Select first 3 jobs
        selected_count = handler.select_multiple_jobs(max_jobs=3)
        print(f"Selected {selected_count} jobs")
        
        # Check how many are currently selected
        current_selected = handler.get_selected_job_count()
        print(f"Currently selected: {current_selected}")
        
        # Apply to selected jobs
        if selected_count > 0:
            handler.apply_to_selected_jobs()
        
        page.wait_for_timeout(3000)
        browser.close()

def example_select_by_criteria():
    """Example of selecting jobs by specific criteria"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Go directly to recommended jobs (if already logged in)
        page.goto("https://www.naukri.com/mnjuser/recommendedjobs")
        page.wait_for_load_state('load')
        
        # Example 1: Select Java Developer jobs
        print("=== Selecting Java Developer jobs ===")
        java_jobs = select_java_developer_jobs(page, max_jobs=3)
        print(f"Selected {java_jobs} Java Developer jobs")
        
        # Example 2: Select jobs in Pune
        print("\n=== Selecting jobs in Pune ===")
        pune_jobs = select_jobs_by_location(page, "Pune", max_jobs=2)
        print(f"Selected {pune_jobs} jobs in Pune")
        
        # Example 3: Select jobs with 2-5 years experience
        print("\n=== Selecting jobs with 2-5 years experience ===")
        exp_jobs = select_jobs_by_experience(page, 2, 5, max_jobs=2)
        print(f"Selected {exp_jobs} jobs with 2-5 years experience")
        
        # Get total selected count
        handler = NaukriCheckboxHandler(page)
        total_selected = handler.get_selected_job_count()
        print(f"\nTotal jobs selected: {total_selected}")
        
        # Apply to all selected jobs
        if total_selected > 0:
            print("\n=== Applying to selected jobs ===")
            handler.apply_to_selected_jobs()
        
        page.wait_for_timeout(3000)
        browser.close()

def example_advanced_checkbox_handling():
    """Advanced example with custom criteria and error handling"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://www.naukri.com/mnjuser/recommendedjobs")
        page.wait_for_load_state('load')
        
        handler = NaukriCheckboxHandler(page)
        handler.wait_for_jobs_to_load()
        
        # Custom criteria: Select jobs with specific skills
        def skill_based_criteria(job_title, article):
            try:
                # Look for skills section
                skills_elem = article.query_selector('.skills, .tags, .key-skill')
                if skills_elem:
                    skills_text = skills_elem.text_content().lower()
                    # Check for specific skills
                    desired_skills = ['java', 'spring', 'hibernate', 'sql']
                    return any(skill in skills_text for skill in desired_skills)
            except:
                pass
            return False
        
        print("=== Selecting jobs with specific skills ===")
        skill_jobs = handler.select_jobs_by_criteria(skill_based_criteria, max_jobs=3)
        print(f"Selected {skill_jobs} jobs with desired skills")
        
        # Custom criteria: Select jobs with salary above certain amount
        def salary_based_criteria(job_title, article):
            try:
                salary_elem = article.query_selector('.salary, .CTC')
                if salary_elem:
                    salary_text = salary_elem.text_content()
                    # Look for salary in Lacs (e.g., "10-17 Lacs PA")
                    if 'lacs' in salary_text.lower():
                        # Extract minimum salary
                        import re
                        match = re.search(r'(\d+)', salary_text)
                        if match:
                            min_salary = int(match.group(1))
                            return min_salary >= 10  # 10 Lacs or more
            except:
                pass
            return False
        
        print("\n=== Selecting jobs with salary >= 10 Lacs ===")
        salary_jobs = handler.select_jobs_by_criteria(salary_based_criteria, max_jobs=2)
        print(f"Selected {salary_jobs} jobs with salary >= 10 Lacs")
        
        # Show current selection status
        total_selected = handler.get_selected_job_count()
        print(f"\nTotal jobs selected: {total_selected}")
        
        # Option to deselect all and start over
        if total_selected > 0:
            print("\n=== Deselecting all jobs ===")
            handler.deselect_all_jobs()
            
            print("\n=== Selecting first 2 jobs instead ===")
            handler.select_multiple_jobs(max_jobs=2)
            
            # Apply to newly selected jobs
            handler.apply_to_selected_jobs()
        
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Basic checkbox selection")
    print("2. Select by criteria (Java, Location, Experience)")
    print("3. Advanced custom criteria")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        example_basic_checkbox_selection()
    elif choice == "2":
        example_select_by_criteria()
    elif choice == "3":
        example_advanced_checkbox_handling()
    else:
        print("Invalid choice. Running basic example...")
        example_basic_checkbox_selection()

