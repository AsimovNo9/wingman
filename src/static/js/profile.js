// --- DOM Elements (Summary) ---
const summaryDisplayContainer = document.getElementById('summaryDisplayContainer');
const summaryEditContainer = document.getElementById('summaryEditContainer');
const summaryDisplay = document.getElementById('summaryDisplay');
const summaryEdit = document.getElementById('summaryEdit');
const editSummaryBtn = document.getElementById('editSummaryBtn');
const saveSummaryBtn = document.getElementById('saveSummaryBtn');
const cancelSummaryBtn = document.getElementById('cancelSummaryBtn');

// --- DOM Elements (Image Gallery) ---
const addImageSlot = document.getElementById('addImageSlot');
const galleryImageUpload = document.getElementById('galleryImageUpload');
const galleryScroll = document.getElementById('galleryScroll'); // The direct parent of images and add-slot

// --- State (To track if placeholders have been removed) ---
let placeholdersRemoved = false;

// --- Event Listeners (Summary) ---
editSummaryBtn.addEventListener('click', () => {
    summaryDisplayContainer.classList.add('hidden');
    summaryEditContainer.classList.remove('hidden');
    summaryEdit.value = summaryDisplay.textContent.trim();
    summaryEdit.focus();
});
cancelSummaryBtn.addEventListener('click', () => {
    summaryEditContainer.classList.add('hidden');
    summaryDisplayContainer.classList.remove('hidden');
});
saveSummaryBtn.addEventListener('click', () => {
    const newSummary = summaryEdit.value.trim();
    summaryDisplay.textContent = newSummary;
    summaryEditContainer.classList.add('hidden');
    summaryDisplayContainer.classList.remove('hidden');
    // In a real app, you would call: saveProfileSummary(newSummary);
});

// --- Event Listeners (Image Gallery) ---
addImageSlot.addEventListener('click', () => {
    galleryImageUpload.click();
});

galleryImageUpload.addEventListener('change', (event) => {
    const files = event.target.files;
    if (files.length > 0) {
        // Remove placeholder images only once when the first actual images are added
        if (!placeholdersRemoved) {
            const placeholderImages = galleryScroll.querySelectorAll('img[src*="via.placeholder.com"]');
            placeholderImages.forEach(img => img.remove());
            placeholdersRemoved = true; // Mark placeholders as removed
        }

        for (const file of files) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const imgElement = document.createElement('img');
                    imgElement.src = e.target.result;
                    imgElement.alt = "User photo"; // You could use file.name for more specific alt text
                    imgElement.classList.add('gallery-image');
                    
                    // Insert the new image before the "Add Photo" slot
                    galleryScroll.insertBefore(imgElement, addImageSlot);
                }
                reader.readAsDataURL(file);
            }
        }
        // Clear the file input value to allow selecting the same file again if desired
        event.target.value = null; 
        // In a real app, you would call: uploadProfileImages(files);
    }
});

// --- Placeholder for backend interaction functions ---
/*
async function uploadProfileImages(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('images[]', files[i]); // Ensure backend expects an array, e.g., 'images[]'
    }
    try {
        const response = await fetch('/api/upload-gallery-images', { // Your Flask endpoint
            method: 'POST',
            body: formData
            // Add headers if needed (e.g., for authentication)
        });
        if (response.ok) {
            const result = await response.json();
            console.log('Images uploaded successfully:', result);
            // Optionally, update image elements with URLs returned by the server if they are processed/renamed
        } else {
            console.error('Image upload failed:', response.statusText);
            alert('Image upload failed.');
        }
    } catch (error) {
        console.error('Error uploading images:', error);
        alert('An error occurred during image upload.');
    }
}

async function saveProfileSummary(summary) {
    try {
        const response = await fetch('/api/save-profile-summary', { // Your Flask endpoint
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ summary: summary })
        });
        if (response.ok) {
            console.log('Summary save successful');
        } else {
            console.error('Summary save failed:', response.statusText);
            alert('Failed to save summary.');
        }
    } catch (error) {
        console.error('Error saving summary:', error);
        alert('An error occurred while saving summary.');
    }
}
*/
// --- Placeholder for initial data loading (e.g., on page load) ---
/*
async function loadProfileData() {
    try {
        const response = await fetch('/api/profile-data'); // Your Flask GET endpoint
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Populate summary
        summaryDisplay.textContent = data.summary || 'Set your profile summary.';

        // Populate image gallery
        galleryScroll.innerHTML = ''; // Clear existing dynamic images (but not the add slot initially)
        if (data.imageUrls && data.imageUrls.length > 0) {
            data.imageUrls.forEach(url => {
                const imgElement = document.createElement('img');
                imgElement.src = url;
                imgElement.alt = "User photo";
                imgElement.classList.add('gallery-image');
                galleryScroll.appendChild(imgElement);
            });
            placeholdersRemoved = true; // Assume placeholders are not needed if data loads
        } else {
            // Add placeholder images if no images are loaded from backend (optional)
            // galleryScroll.innerHTML = `
            //  <img src="https://via.placeholder.com/200x150/2accc1/ffffff?Text=Photo+1" alt="User photo" class="gallery-image">
            //  <img src="https://via.placeholder.com/180x150/7bd1f0/ffffff?Text=Photo+2" alt="User photo" class="gallery-image">`;
            placeholdersRemoved = false;
        }
        galleryScroll.appendChild(addImageSlot); // Ensure add slot is always last

    } catch (error) {
        console.error('Failed to load profile data:', error);
        // Ensure add slot is present even if data loading fails
        if (!galleryScroll.contains(addImageSlot)) {
                galleryScroll.appendChild(addImageSlot);
        }
    }
}
window.addEventListener('DOMContentLoaded', () => {
    // loadProfileData(); // Uncomment to load data when the page is ready
});
*/