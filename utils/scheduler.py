"""
Scheduler for automatic data updates
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

class UpdateScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        logging.basicConfig()
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Scheduler shutdown")
    
    def add_job(self, func, interval_minutes=30, job_id=None):
        """
        Add a periodic job
        
        Args:
            func: Function to execute
            interval_minutes: Interval in minutes
            job_id: Unique job identifier
        """
        if job_id:
            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass
        
        self.scheduler.add_job(
            func=func,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            replace_existing=True
        )
        print(f"Job '{job_id}' scheduled to run every {interval_minutes} minutes")
    
    def remove_job(self, job_id):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            print(f"Job '{job_id}' removed")
        except Exception as e:
            print(f"Error removing job: {str(e)}")
    
    def get_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()
