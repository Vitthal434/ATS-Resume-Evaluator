const uploadBox = document.querySelector(".upload-box");
const fileInput = document.getElementById("resume");
const selectedFile = document.getElementById("selected-file");
const removeButton = document.getElementById("remove-file");

function updateFile(file){

    if(!file) return;

    const allowed = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ];

    if(!allowed.includes(file.type)){

        alert("Only PDF and DOC/DOCX files are allowed.");

        fileInput.value="";

        selectedFile.textContent="No file selected";

        removeButton.style.display="none";

        return;

    }

    selectedFile.textContent="✅ " + file.name;

    removeButton.style.display="inline-block";

}

fileInput.addEventListener("change",()=>{

    if(fileInput.files.length){

        updateFile(fileInput.files[0]);

    }

});

uploadBox.addEventListener("dragover",(e)=>{

    e.preventDefault();

    uploadBox.classList.add("dragover");

});

uploadBox.addEventListener("dragleave",()=>{

    uploadBox.classList.remove("dragover");

});

uploadBox.addEventListener("drop",(e)=>{

    e.preventDefault();

    uploadBox.classList.remove("dragover");

    const file=e.dataTransfer.files[0];

    if(file){

        fileInput.files=e.dataTransfer.files;

        updateFile(file);

    }

});

removeButton.addEventListener("click",()=>{

    fileInput.value="";

    selectedFile.textContent="No file selected";

    removeButton.style.display="none";

});

const analyzeForm = document.querySelector("form[action='/match']");

if (analyzeForm) {
    analyzeForm.addEventListener("submit", (e) => {
        const submitBtn = analyzeForm.querySelector("button[type='submit']");
        const jdTextarea = analyzeForm.querySelector("textarea[name='job_description']");

        if (!fileInput || !fileInput.files.length) {
            alert("Please select or upload a resume file.");
            e.preventDefault();
            return;
        }

        if (!jdTextarea || !jdTextarea.value.trim()) {
            alert("Please paste a job description.");
            e.preventDefault();
            return;
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Analyzing Resume...
            `;
        }
    });

    window.addEventListener("pageshow", () => {
        const submitBtn = analyzeForm.querySelector("button[type='submit']");
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = "Analyze Resume";
        }
    });
}
