from playwright.sync_api import Page
import time

class NaukriCheckboxHandler:
    """Utility class for handling checkbox interactions on Naukri.com"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def wait_for_jobs_to_load(self, timeout=10000):
        """Wait for job listings to be visible"""
        self.page.wait_for_selector('.sim-jobs', timeout=timeout)
        self.page.wait_for_selector('article.jobTuple', timeout=timeout)
        # Additional wait for dynamic content
        self.page.wait_for_timeout(2000)
    
    def get_job_checkboxes(self):
        """Get all available job checkboxes"""
        return self.page.query_selector_all('article.jobTuple .naukicon-ot-checkbox')
    
    def is_checkbox_selected(self, checkbox):
        """Check if a checkbox is currently selected"""
        try:
            class_attr = checkbox.get_attribute('class') or ''
            # Look for indicators that checkbox is selected
            selected_indicators = ['checked', 'selected', 'active']
            return any(indicator in class_attr for indicator in selected_indicators)
        except:
            return False
    
    def select_checkbox(self, checkbox, job_index=None):
        """Select a specific checkbox"""
        try:
            if not self.is_checkbox_selected(checkbox):
                checkbox.click()
                self.page.wait_for_timeout(500)  # Wait for state change
                print(f"✓ Selected checkbox for job {job_index or 'unknown'}")
                return True
            else:
                print(f"⚠ Checkbox for job {job_index or 'unknown'} already selected")
                return False
        except Exception as e:
            print(f"✗ Error selecting checkbox for job {job_index or 'unknown'}: {e}")
            return False
    
    def select_multiple_jobs(self, max_jobs=5, start_from=0):
        """Select multiple job checkboxes"""
        checkboxes = self.get_job_checkboxes()
        print(f"Found {len(checkboxes)} job checkboxes")
        
        selected_count = 0
        for i, checkbox in enumerate(checkboxes[start_from:start_from + max_jobs]):
            job_index = start_from + i + 1
            if self.select_checkbox(checkbox, job_index):
                selected_count += 1
            
            if selected_count >= max_jobs:
                break
        
        print(f"Successfully selected {selected_count} jobs")
        return selected_count
    
    def select_jobs_by_criteria(self, criteria_func, max_jobs=5):
        """Select jobs based on custom criteria"""
        checkboxes = self.get_job_checkboxes()
        job_articles = self.page.query_selector_all('article.jobTuple')
        
        selected_count = 0
        for i, (checkbox, article) in enumerate(zip(checkboxes, job_articles)):
            if selected_count >= max_jobs:
                break
                
            try:
                # Get job details for criteria evaluation
                job_title_elem = article.query_selector('h2, .jobTuple h3, .title')
                job_title = job_title_elem.text_content().strip() if job_title_elem else f"Job {i+1}"
                
                # Check if job meets criteria
                if criteria_func(job_title, article):
                    if self.select_checkbox(checkbox, i+1):
                        selected_count += 1
                        print(f"Selected job: {job_title}")
                        
            except Exception as e:
                print(f"Error evaluating job {i+1}: {e}")
                continue
        
        return selected_count
    
    def deselect_all_jobs(self):
        """Deselect all currently selected job checkboxes"""
        checkboxes = self.get_job_checkboxes()
        deselected_count = 0
        
        for i, checkbox in enumerate(checkboxes):
            if self.is_checkbox_selected(checkbox):
                checkbox.click()
                self.page.wait_for_timeout(300)
                deselected_count += 1
        
        print(f"Deselected {deselected_count} jobs")
        return deselected_count
    
    def get_selected_job_count(self):
        """Get the count of currently selected jobs"""
        checkboxes = self.get_job_checkboxes()
        return sum(1 for checkbox in checkboxes if self.is_checkbox_selected(checkbox))
    
    def apply_to_selected_jobs(self):
        """Apply to all currently selected jobs"""
        selected_count = self.get_selected_job_count()
        
        if selected_count == 0:
            print("No jobs selected to apply to")
            return False
        
        print(f"Attempting to apply to {selected_count} selected jobs")
        
        # Use the exact selector from the Naukri.com page structure
        # Based on the screenshot: button.multi-apply-button.typ-16Bold
        apply_selectors = [
            'button.multi-apply-button.typ-16Bold',
            'button.multi-apply-button',
            '.multi-apply-button',
            'button:has-text("Apply")',
            'button:has-text("Apply to Selected")'
        ]
        
        apply_button = None
        for selector in apply_selectors:
            try:
                apply_button = self.page.query_selector(selector)
                if apply_button and apply_button.is_visible():
                    print(f"Found apply button with selector: {selector}")
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        if apply_button:
            try:
                # Get button text for verification
                button_text = apply_button.text_content().strip()
                print(f"Found apply button: '{button_text}'")
                
                apply_button.click()
                print("✓ Clicked apply button")
                self.page.wait_for_timeout(2000)
                return True
            except Exception as e:
                print(f"✗ Error clicking apply button: {e}")
                return False
        else:
            print("✗ Apply button not found with any selector")
            return False

# Example usage functions
def select_java_developer_jobs(page: Page, max_jobs=5):
    """Select jobs that contain 'Java' in the title"""
    handler = NaukriCheckboxHandler(page)
    handler.wait_for_jobs_to_load()
    
    def java_criteria(job_title, article):
        return 'java' in job_title.lower()
    
    return handler.select_jobs_by_criteria(java_criteria, max_jobs)

def select_jobs_by_location(page: Page, location, max_jobs=5):
    """Select jobs in a specific location"""
    handler = NaukriCheckboxHandler(page)
    handler.wait_for_jobs_to_load()
    
    def location_criteria(job_title, article):
        try:
            location_elem = article.query_selector('.location, .loc')
            if location_elem:
                job_location = location_elem.text_content().lower()
                return location.lower() in job_location
        except:
            pass
        return False
    
    return handler.select_jobs_by_criteria(location_criteria, max_jobs)

def select_jobs_by_experience(page: Page, min_exp, max_exp, max_jobs=5):
    """Select jobs within experience range"""
    handler = NaukriCheckboxHandler(page)
    handler.wait_for_jobs_to_load()
    
    def experience_criteria(job_title, article):
        try:
            exp_elem = article.query_selector('.exp, .experience')
            if exp_elem:
                exp_text = exp_elem.text_content()
                # Parse experience text like "2-5 Yrs"
                if 'yrs' in exp_text.lower():
                    exp_parts = exp_text.lower().replace('yrs', '').strip().split('-')
                    if len(exp_parts) == 2:
                        job_min_exp = float(exp_parts[0])
                        job_max_exp = float(exp_parts[1])
                        return min_exp <= job_min_exp and job_max_exp <= max_exp
        except:
            pass
        return False
    
    return handler.select_jobs_by_criteria(experience_criteria, max_jobs)
