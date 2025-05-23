// JardAIn Garden Planner - Frontend JavaScript

class GardenPlannerApp {
    constructor() {
        this.selectedPlants = new Set();
        this.availablePlants = [];
        this.init();
    }

    async init() {
        console.log('🌱 Initializing JardAIn Garden Planner...');
        
        // Load available plants
        await this.loadPlants();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ App initialized successfully!');
    }

    async loadPlants() {
        try {
            const response = await fetch('/api/plants');
            const data = await response.json();
            this.availablePlants = data.plants || [];
            this.renderPlantGrid();
        } catch (error) {
            console.error('Error loading plants:', error);
            this.showError('Failed to load plant database. Please refresh the page.');
        }
    }

    renderPlantGrid() {
        const plantGrid = document.getElementById('plant-grid');
        if (!plantGrid) {
            console.warn('Plant grid element not found');
            return;
        }

        plantGrid.innerHTML = this.availablePlants.map(plant => `
            <div class="plant-card" data-plant="${plant.name}" onclick="app.togglePlant('${plant.name}')">
                <div class="plant-emoji">${this.getPlantEmoji(plant.type)}</div>
                <div class="plant-name">${plant.name}</div>
                <div class="plant-type">${plant.type}</div>
            </div>
        `).join('');
        
        console.log(`✅ Loaded ${this.availablePlants.length} plants`);
    }

    getPlantEmoji(type) {
        const emojis = {
            'fruit': '🍅',
            'leafy_green': '🥬',
            'root_vegetable': '🥕',
            'herb': '🌿',
            'legume': '🌱',
            'vine': '🥒',
            'bulb': '🧅',
            'cruciferous': '🥦'
        };
        return emojis[type] || '🌱';
    }

    togglePlant(plantName) {
        if (this.selectedPlants.has(plantName)) {
            this.selectedPlants.delete(plantName);
        } else {
            this.selectedPlants.add(plantName);
        }
        
        // Update visual selection
        const plantCard = document.querySelector(`[data-plant="${plantName}"]`);
        if (plantCard) {
            plantCard.classList.toggle('selected');
        }
        
        // Update selected count
        this.updateSelectedCount();
        
        console.log(`Selected plants: ${Array.from(this.selectedPlants).join(', ')}`);
    }

    updateSelectedCount() {
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = this.selectedPlants.size;
        }
        
        // Enable/disable generate button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.disabled = this.selectedPlants.size === 0;
        }
    }

    setupEventListeners() {
        // Generate plan button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateGardenPlan());
        }

        // Plant search
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterPlants(e.target.value));
        }
    }

    filterPlants(searchTerm) {
        const plantCards = document.querySelectorAll('.plant-card');
        plantCards.forEach(card => {
            const plantName = card.querySelector('.plant-name').textContent.toLowerCase();
            const matches = plantName.includes(searchTerm.toLowerCase());
            card.style.display = matches ? 'block' : 'none';
        });
    }

    async generateGardenPlan() {
        const zipCode = document.getElementById('zip-code').value;
        const gardenSize = document.getElementById('garden-size').value;
        
        if (!zipCode) {
            this.showError('Please enter your zip code.');
            return;
        }
        
        if (this.selectedPlants.size === 0) {
            this.showError('Please select at least one plant.');
            return;
        }

        // Show loading state
        this.showLoading();

        try {
            const requestData = {
                zip_code: zipCode,
                selected_plants: Array.from(this.selectedPlants),
                garden_size: gardenSize || 'medium',
                experience_level: 'beginner'
            };

            console.log('🚀 Generating garden plan:', requestData);

            const response = await fetch('/api/plans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const gardenPlan = await response.json();
            console.log('✅ Garden plan generated:', gardenPlan);
            
            this.displayResults(gardenPlan);
            
            // Generate PDF option
            this.showPDFOption(gardenPlan.plan_id);

        } catch (error) {
            console.error('Error generating garden plan:', error);
            this.showError(`Failed to generate garden plan: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(gardenPlan) {
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <h2>🌱 Your Personalized Garden Plan</h2>
            <div class="alert alert-success">
                <strong>Success!</strong> Generated plan for ${gardenPlan.location.city}, ${gardenPlan.location.state} 
                (Zone ${gardenPlan.location.hardiness_zone})
            </div>
            
            <div class="plan-section">
                <h3>Selected Plants (${gardenPlan.plant_information.length})</h3>
                <div class="plants-summary">
                    ${gardenPlan.plant_information.map(plant => `
                        <div class="plant-summary">
                            <h4>${plant.name}</h4>
                            <p><strong>Days to Harvest:</strong> ${plant.days_to_harvest} days</p>
                            <p><strong>Spacing:</strong> ${plant.spacing_inches} inches apart</p>
                            <p><strong>Planting Depth:</strong> ${plant.planting_depth_inches} inches</p>
                            <p><strong>Sun Requirements:</strong> ${plant.sun_requirements}</p>
                            <p><strong>Water Needs:</strong> ${plant.water_requirements}</p>
                        </div>
                    `).join('')}
                </div>
            </div>

            ${gardenPlan.planting_schedules && gardenPlan.planting_schedules.length > 0 ? `
                <div class="plan-section">
                    <h3>📅 Planting Schedule</h3>
                    <div class="schedule-grid">
                        ${gardenPlan.planting_schedules.map(item => `
                            <div class="schedule-item">
                                <strong>${item.plant}:</strong> ${item.optimal_planting_time}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            ${gardenPlan.growing_instructions && gardenPlan.growing_instructions.length > 0 ? `
                <div class="plan-section">
                    <h3>🌱 Growing Instructions</h3>
                    <div class="instructions-list">
                        ${gardenPlan.growing_instructions.map(instruction => `
                            <div class="instruction-item">
                                <h4>${instruction.plant}</h4>
                                <p>${instruction.detailed_instructions}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            ${gardenPlan.general_tips && gardenPlan.general_tips.length > 0 ? `
                <div class="plan-section">
                    <h3>💡 General Tips</h3>
                    <ul>
                        ${gardenPlan.general_tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;

        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    showPDFOption(planId) {
        const pdfSection = document.getElementById('pdfSection');
        if (pdfSection) {
            pdfSection.innerHTML = `
                <h3>📄 Download Your Plan</h3>
                <p>Get a beautiful PDF copy of your garden plan:</p>
                <button class="btn btn-primary" onclick="app.downloadPDF('${planId}')">
                    📥 Download PDF Plan
                </button>
            `;
            pdfSection.style.display = 'block';
        }
    }

    async downloadPDF(planId) {
        try {
            const response = await fetch(`/api/pdf/garden-plan/${planId}`);
            
            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `garden-plan-${planId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showSuccess('PDF downloaded successfully!');
        } catch (error) {
            console.error('Error downloading PDF:', error);
            this.showError('Failed to download PDF. Please try again.');
        }
    }

    showLoading() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <h3>🌱 Creating Your Garden Plan...</h3>
                    <p>Our AI is analyzing your location and plant selections...</p>
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    }

    hideLoading() {
        // Loading will be replaced by results or error
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Error:</strong> ${message}
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    }

    showSuccess(message) {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            const successAlert = document.createElement('div');
            successAlert.className = 'alert alert-success';
            successAlert.innerHTML = `<strong>Success:</strong> ${message}`;
            resultsDiv.insertBefore(successAlert, resultsDiv.firstChild);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GardenPlannerApp();
}); 