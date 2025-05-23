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
        // Store for debugging
        this.lastGeneratedPlan = gardenPlan;
        
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        // Show only a minimal success message
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>✅ Garden Plan Generated Successfully!</strong><br>
                Your personalized plan for ${gardenPlan.location.city}, ${gardenPlan.location.state} 
                (Zone ${gardenPlan.location.usda_zone}) is ready.<br>
                <small>📱 ${gardenPlan.plant_information.length} plants included • Generated ${new Date().toLocaleDateString()}</small>
            </div>
        `;

        resultsDiv.style.display = 'block';
        
        // Don't scroll to results - let user naturally see the download button
    }

    renderPlantingSchedule(schedules) {
        console.log('🔍 Rendering planting schedules:', schedules);
        
        if (!schedules || !Array.isArray(schedules) || schedules.length === 0) {
            return '<div class="plan-section"><h3>📅 Planting Schedule</h3><p>No planting schedule available.</p></div>';
        }

        return `
            <div class="plan-section">
                <h3>📅 Planting Schedule</h3>
                <div class="schedule-grid">
                    ${schedules.map(schedule => `
                        <div class="schedule-item">
                            <h4>${schedule.plant_name}</h4>
                            ${schedule.start_indoors_date ? `<p><strong>Start Indoors:</strong> ${schedule.start_indoors_date}</p>` : ''}
                            ${schedule.direct_sow_date ? `<p><strong>Direct Sow:</strong> ${schedule.direct_sow_date}</p>` : ''}
                            ${schedule.transplant_date ? `<p><strong>Transplant:</strong> ${schedule.transplant_date}</p>` : ''}
                            ${schedule.harvest_start_date ? `<p><strong>Harvest Start:</strong> ${schedule.harvest_start_date}</p>` : ''}
                            ${schedule.harvest_end_date ? `<p><strong>Harvest End:</strong> ${schedule.harvest_end_date}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderGrowingInstructions(instructions) {
        console.log('🔍 Rendering growing instructions:', instructions);
        
        if (!instructions || !Array.isArray(instructions) || instructions.length === 0) {
            return '<div class="plan-section"><h3>🌱 Growing Instructions</h3><p>No growing instructions available.</p></div>';
        }

        return `
            <div class="plan-section">
                <h3>🌱 Growing Instructions</h3>
                <div class="instructions-list">
                    ${instructions.map(instruction => `
                        <div class="instruction-item">
                            <h4>${instruction.plant_name}</h4>
                            
                            ${instruction.preparation_steps && instruction.preparation_steps.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🏗️ Preparation Steps</h5>
                                    <ul>
                                        ${instruction.preparation_steps.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${instruction.planting_steps && instruction.planting_steps.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🌱 Planting Steps</h5>
                                    <ul>
                                        ${instruction.planting_steps.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${instruction.care_instructions && instruction.care_instructions.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🌿 Care Instructions</h5>
                                    <ul>
                                        ${instruction.care_instructions.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderGeneralTips(tips) {
        if (!tips || !Array.isArray(tips) || tips.length === 0) {
            return '';
        }

        return `
            <div class="plan-section">
                <h3>💡 General Tips</h3>
                <ul>
                    ${tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    showPDFOption(planId) {
        const pdfSection = document.getElementById('pdfSection');
        if (pdfSection) {
            pdfSection.innerHTML = `
                <div class="pdf-download-container" style="text-align: center; margin: 2rem 0; padding: 2rem; background: #f8fffe; border-radius: 12px; border: 2px solid #4a7c59;">
                    <h3 style="color: #2d5a2d; margin-bottom: 1rem;">📄 Your Garden Plan is Ready!</h3>
                    <button class="btn btn-pdf-download" onclick="app.downloadPDF('${planId}')" 
                            style="background: #4a7c59; color: white; border: none; padding: 1rem 2rem; font-size: 1.1rem; border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                        📥 Download PDF Garden Plan
                    </button>
                    <p style="margin-top: 1rem; color: #666; font-size: 0.9rem;">
                        Your complete garden plan with planting schedules, growing instructions, and layout recommendations.
                    </p>
                </div>
            `;
            pdfSection.style.display = 'block';
            
            // Add hover effect to button
            const button = pdfSection.querySelector('.btn-pdf-download');
            button.addEventListener('mouseenter', () => {
                button.style.background = '#2d5a2d';
                button.style.transform = 'translateY(-2px)';
            });
            button.addEventListener('mouseleave', () => {
                button.style.background = '#4a7c59';
                button.style.transform = 'translateY(0)';
            });
            
            // Scroll to the download section smoothly
            pdfSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
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