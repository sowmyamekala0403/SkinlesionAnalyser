const dropzone = document.querySelector('.dropzone');
const fileInput = document.getElementById('fileInput');
const progressBar = document.querySelector('.progress-bar');
const progress = document.querySelector('.progress');
const result = document.querySelector('.result');
const predictionText = document.getElementById('prediction');
const analyzedImage = document.getElementById('analyzedImage');

// Function to display loading progress
function updateProgress(value) {
  progress.style.width = `${value}%`;
}

// Function to handle file drag and drop events with visual feedback
dropzone.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropzone.classList.add('dragover'); // Add hover class for visual feedback
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (event) => {
  event.preventDefault();
  dropzone.classList.remove('dragover');
  const file = event.dataTransfer.files[0];
  fileInput.files = file;
  uploadFile(file);
});

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  uploadFile(file);
});

// Function to handle file upload, display progress, and show result
async function uploadFile(file) {
  if (!file) {
    alert('Please select a file to upload.'); // Display an alert for missing file
    return;
  }

  // Show progress bar
  progressBar.classList.remove('hidden');

  // Create a FormData object to send the file
  const formData = new FormData();
  formData.append('file', file);

  try {
    // Send the file upload request to the backend
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData,
      onUploadProgress: (event) => {
        const progress = Math.round((event.loaded * 100) / event.total);
        updateProgress(progress);
      }
    }
  
  );

    // Hide progress bar
    progressBar.classList.add('hidden');

    // Check for successful response
    if (!response.ok) {
      throw new Error(`Error uploading file: ${response.statusText}`);
    }

    // Parse the JSON response
    const data = await response.json();

    // Display result
    // if (data.analyzed_image) {
    //   const imageDataURI = `data:image/jpeg;base64,${data.analyzed_image}`;  // Construct image data URI
    //   analyzedImage.src = imageDataURI;
    // } else {
    //   analyzedImage.src = '';  // Clear image if not provided
    // }
    predictionText.textContent = data.prediction || 'Prediction unavailable.';
    analyzedImage.src = `data:image/jpeg;base64,${data.analyzed_image}`;
    analyzedImage.style.display = 'block';
    result.classList.remove('hidden');
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred during upload. Please try again.');
  } finally {
    // Optional: Reset the upload input after submission (if needed)
    // uploadInput.value = '';
  }
}
