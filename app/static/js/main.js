document.addEventListener("DOMContentLoaded", function () {
	// DOM elements
	const form = document.getElementById("extraction-form");
	const promptColumn = document.getElementById("prompt-column");
	const resultsColumn = document.getElementById("results-column");
	const analyzeBtn = document.getElementById("analyze-btn");
	const clearBtn = document.getElementById("clear-btn");
	const uploadArea = document.getElementById("upload-area");
	const previewContainer = document.getElementById("preview-container");
	const previewImg = document.getElementById("preview-image");
	const imageInput = document.getElementById("image-input");
	const fileName = document.getElementById("file-name");
	const promptInput = document.getElementById("prompt-input");
	const loadingOverlay = document.getElementById("loading-overlay");
	const exampleItems = document.querySelectorAll(".example-item");

	// Check if we should show results on page load (for server-side rendering)
	const showResultsParam = document.body.getAttribute("data-show-results");
	if (showResultsParam && showResultsParam.toLowerCase() === "true") {
		showResults();
	}

	// Function to show results
	function showResults() {
		promptColumn.style.display = "none";
		resultsColumn.style.display = "block";
		resultsColumn.classList.add("fade-in");
		analyzeBtn.innerHTML = '<i class="fas fa-sync-alt"></i> New Analysis';
		analyzeBtn.classList.remove("btn-primary");
		analyzeBtn.classList.add("btn-success");
	}

	// Function to show form
	function showPromptForm() {
		resultsColumn.style.display = "none";
		promptColumn.style.display = "block";
		analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze';
		analyzeBtn.classList.remove("btn-success");
		analyzeBtn.classList.add("btn-primary");
	}

	// Bind example item click events
	exampleItems.forEach((item) => {
		item.addEventListener("click", function () {
			const text = this.textContent.replace(/^\s*[\u200B\u00A0\s]+|[\u200B\u00A0\s]+$/g, "");
			promptInput.value = text;
			// Enable the analyze button if image is also uploaded
			checkFormValidity();
		});
	});

	// Function to preview image
	function handleImagePreview(input) {
		if (input.files && input.files[0]) {
			const reader = new FileReader();

			reader.onload = function (e) {
				previewImg.src = e.target.result;
				previewContainer.style.display = "block";
				uploadArea.style.display = "none";
				fileName.textContent = input.files[0].name;

				// Enable the analyze button if prompt is also filled
				checkFormValidity();
			};

			reader.readAsDataURL(input.files[0]);
		}
	}

	// Attach the image preview function to the input change event
	imageInput.addEventListener("change", function () {
		handleImagePreview(this);
	});

	// Function to fill prompt from examples - this can be called from HTML onclick
	window.fillPrompt = function (text) {
		promptInput.value = text;
		// Enable the analyze button if image is also uploaded
		checkFormValidity();
	};

	// Function to copy text to clipboard
	window.copyText = function (elementId) {
		const element = document.getElementById(elementId);
		const text = element.innerText;

		navigator.clipboard
			.writeText(text)
			.then(() => {
				const copyBtn = event.currentTarget;
				const originalHTML = copyBtn.innerHTML;

				copyBtn.innerHTML = '<i class="fas fa-check"></i>';
				copyBtn.style.backgroundColor = "#4caf50";
				copyBtn.style.color = "white";

				setTimeout(() => {
					copyBtn.innerHTML = originalHTML;
					copyBtn.style.backgroundColor = "";
					copyBtn.style.color = "";
				}, 2000);
			})
			.catch((err) => {
				console.error("Failed to copy text: ", err);
			});
	};

	// Function to check form validity
	function checkFormValidity() {
		if (imageInput.files.length > 0 && promptInput.value.trim() !== "") {
			analyzeBtn.disabled = false;
		} else {
			analyzeBtn.disabled = true;
		}
	}

	// Clear button functionality
	clearBtn.addEventListener("click", function () {
		// Clear image
		imageInput.value = "";
		previewContainer.style.display = "none";
		uploadArea.style.display = "flex";
		fileName.textContent = "";

		// Clear prompt
		promptInput.value = "";

		// If showing results, switch back to form
		if (resultsColumn.style.display === "block") {
			showPromptForm();
		}

		// Disable analyze button
		analyzeBtn.disabled = true;
	});

	// Form submission handler
	form.addEventListener("submit", function (e) {
		e.preventDefault();

		// If we're already showing results, clicking means "New Analysis"
		if (resultsColumn.style.display === "block") {
			showPromptForm();
			return;
		}

		// Validate form
		if (!form.checkValidity()) {
			form.reportValidity();
			return;
		}

		// Show loading overlay
		loadingOverlay.style.display = "flex";

		// Submit form data
		const formData = new FormData(form);

		fetch("/extract", {
			method: "POST",
			body: formData,
			headers: {
				"X-Requested-With": "XMLHttpRequest",
			},
		})
			.then((response) => response.json())
			.then((data) => {
				// Update results section with data
				document.getElementById("result-prompt").textContent = data.prompt;
				document.getElementById("extracted-text").textContent = data.extracted_text;
				document.getElementById("result-text").textContent = data.result;

				// Show results
				showResults();

				// Hide loading overlay
				loadingOverlay.style.display = "none";
			})
			.catch((error) => {
				console.error("Error:", error);
				loadingOverlay.style.display = "none";
				alert("An error occurred while processing your request. Please try again.");
			});
	});

	// Add event listeners for form validation
	imageInput.addEventListener("change", checkFormValidity);
	promptInput.addEventListener("input", checkFormValidity);

	// Initialize form validation state
	analyzeBtn.disabled = true;
});
