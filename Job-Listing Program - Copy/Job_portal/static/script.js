document.addEventListener('DOMContentLoaded', () => {
    const postJobBtn = document.getElementById('postJobBtn');
    const jobForm = document.getElementById('jobForm');
    const newJobForm = document.getElementById('newJobForm');
    const jobList = document.getElementById('jobList');
    const sortAlphaBtn = document.getElementById('sortAlpha');
    const sortDateBtn = document.getElementById('sortDate');

    postJobBtn.addEventListener('click', () => {
        jobForm.style.display = jobForm.style.display === 'none' ? 'block' : 'none';
    });

    newJobForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(newJobForm);
        const response = await fetch('/add', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            newJobForm.reset();
            jobForm.style.display = 'none';
            loadJobs();
        }
    });

    async function loadJobs() {
        const response = await fetch('/');
        const jobs = await response.text();
        jobList.innerHTML = jobs;
    }

    sortAlphaBtn.addEventListener('click', () => {
        sortJobs('alpha');
    });

    sortDateBtn.addEventListener('click', () => {
        sortJobs('date');
    });

    async function sortJobs(criteria) {
        const response = await fetch(`/sort?criteria=${criteria}`);
        const jobs = await response.text();
        jobList.innerHTML = jobs;
    }

    window.toggleApplicationForm = function(jobId) {
        const form = document.getElementById(`application-form-${jobId}`);
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    };

    window.submitApplication = function(jobId) {
        const applicationLetter = document.getElementById(`applicationLetter-${jobId}`).value;
        const portfolioLink = document.getElementById(`portfolioLink-${jobId}`).value;

        if (applicationLetter && portfolioLink) {
            alert(`Application submitted!\n\nLetter:\n${applicationLetter}\n\nPortfolio Link:\n${portfolioLink}`);
            toggleApplicationForm(jobId);
        } else {
            alert('Please fill in both fields before submitting your application.');
        }
    };

    loadJobs();
});