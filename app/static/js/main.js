// Global state
let currentMachineId = null;

// DOM Elements
const statusModal = document.getElementById('statusModal');
const statusSelect = document.getElementById('statusSelect');
const saveStatusBtn = document.getElementById('saveStatus');
const machineForm = document.getElementById('machineForm');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any tooltips or other UI elements
    initializeTooltips();
    
    // Set up event listeners
    setupEventListeners();
});

function initializeTooltips() {
    // Initialize any tooltips if needed
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupEventListeners() {
    // Status update modal
    if (saveStatusBtn) {
        saveStatusBtn.addEventListener('click', handleStatusUpdate);
    }
    
    // Machine form submission
    if (machineForm) {
        machineForm.addEventListener('submit', handleMachineFormSubmit);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === statusModal) {
            closeStatusModal();
        }
    });
}

// Status Modal Functions
function openStatusModal(machineId) {
    currentMachineId = machineId;
    if (statusModal) {
        statusModal.classList.remove('hidden');
    }
}

function closeStatusModal() {
    if (statusModal) {
        statusModal.classList.add('hidden');
    }
    currentMachineId = null;
}

// API Functions
async function updateMachineStatus(machineId, status) {
    try {
        const response = await fetch(`/api/machines/${machineId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status }),
        });
        
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json();
            showError(`Failed to update status: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showError('Failed to update status. Please try again.');
    }
}

async function createMachine(machineData) {
    try {
        const response = await fetch('/api/machines', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(machineData),
        });
        
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json();
            showError(`Failed to create machine: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error creating machine:', error);
        showError('Failed to create machine. Please try again.');
    }
}

// Event Handlers
async function handleStatusUpdate() {
    if (!currentMachineId || !statusSelect) return;
    
    const status = statusSelect.value;
    await updateMachineStatus(currentMachineId, status);
    closeStatusModal();
}

function handleMachineFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(machineForm);
    const machineData = {
        name: formData.get('name'),
        location: formData.get('location')
    };
    
    createMachine(machineData);
}

// UI Helpers
function showError(message) {
    // You can replace this with a more sophisticated notification system
    alert(message);
}

// Make functions available globally for inline handlers
window.updateStatus = updateMachineStatus;
window.openStatusModal = openStatusModal;
window.closeStatusModal = closeStatusModal;
