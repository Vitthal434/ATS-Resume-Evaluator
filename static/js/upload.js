/* ==========================================================================
   ResumeIQ — Upload & UI Interactions Script
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const uploadBox = document.getElementById("upload-drop-zone");
    const fileInput = document.getElementById("resume");
    const fileInfoCard = document.getElementById("file-info-card");
    const fileNameEl = document.getElementById("selected-file-name");
    const fileSizeEl = document.getElementById("selected-file-size");
    const removeButton = document.getElementById("remove-file");
    const analyzeForm = document.getElementById("resume-analyze-form");
    const jdTextarea = document.getElementById("job_description");
    const jdWordCount = document.getElementById("jd-word-count");
    const loadSampleJdBtn = document.getElementById("btn-load-sample-jd");

    function formatFileSize(bytes) {
        if (!bytes || bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
    }

    function updateFileDisplay(file) {
        if (!file) return;

        const allowedExtensions = [".pdf", ".doc", ".docx"];
        const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

        if (!allowedExtensions.includes(ext)) {
            alert("Please upload a valid PDF or DOC/DOCX resume file.");
            if (fileInput) fileInput.value = "";
            if (fileInfoCard) fileInfoCard.classList.add("d-none");
            return;
        }

        if (fileNameEl) fileNameEl.textContent = file.name;
        if (fileSizeEl) fileSizeEl.textContent = formatFileSize(file.size);
        if (fileInfoCard) {
            fileInfoCard.classList.remove("d-none");
            fileInfoCard.classList.add("d-flex");
        }
    }

    // Ensure clicking anywhere in the dropzone triggers the file picker
    if (uploadBox && fileInput) {
        uploadBox.addEventListener("click", function (e) {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files && fileInput.files.length) {
                updateFileDisplay(fileInput.files[0]);
            }
        });
    }

    if (uploadBox) {
        ["dragenter", "dragover"].forEach(eventName => {
            uploadBox.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                uploadBox.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            uploadBox.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                uploadBox.classList.remove("dragover");
            });
        });

        uploadBox.addEventListener("drop", function (e) {
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length) {
                fileInput.files = dt.files;
                updateFileDisplay(dt.files[0]);
            }
        });
    }

    if (removeButton) {
        removeButton.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (fileInput) fileInput.value = "";
            if (fileInfoCard) {
                fileInfoCard.classList.add("d-none");
                fileInfoCard.classList.remove("d-flex");
            }
        });
    }

    // Live word count for Job Description textarea
    if (jdTextarea && jdWordCount) {
        function updateWordCount() {
            const text = jdTextarea.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            jdWordCount.textContent = words + " word" + (words === 1 ? "" : "s");
        }

        jdTextarea.addEventListener("input", updateWordCount);
        updateWordCount();
    }

    // Load Sample JD helper
    if (loadSampleJdBtn && jdTextarea) {
        loadSampleJdBtn.addEventListener("click", function (e) {
            e.preventDefault();
            jdTextarea.value = `Senior Backend Software Engineer

Requirements:
- Strong proficiency in Python or Go with 3+ years of experience
- Hands-on experience building REST APIs with FastAPI, Flask, or Django
- Proficiency in PostgreSQL, MySQL, or relational SQL databases
- Experience with Docker containerization and CI/CD pipelines (Jenkins or GitHub Actions)
- Cloud infrastructure experience with AWS, Azure, or GCP

Nice to Have:
- Knowledge of Redis caching and Kafka message queues
- Experience with Kubernetes cluster orchestration`;
            if (jdWordCount) {
                const words = jdTextarea.value.trim().split(/\s+/).length;
                jdWordCount.textContent = words + " words";
            }
            jdTextarea.focus();
        });
    }

    // Form submission validation & spinner
    if (analyzeForm) {
        analyzeForm.addEventListener("submit", function (e) {
            const submitBtn = document.getElementById("btn-analyze-submit");
            const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;
            const hasJd = jdTextarea && jdTextarea.value.trim().length > 0;

            if (!hasFile) {
                alert("Please select or drop a resume file (PDF or DOCX).");
                e.preventDefault();
                return;
            }

            if (!hasJd) {
                alert("Please paste a job description.");
                e.preventDefault();
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Evaluating Resume with ATS Engine...
                `;
            }
        });

        window.addEventListener("pageshow", function () {
            const submitBtn = document.getElementById("btn-analyze-submit");
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="bi bi-stars me-2"></i> Calculate ATS Score & Generate Report`;
            }
        });
    }
});
